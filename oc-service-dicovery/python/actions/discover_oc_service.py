# *************************************************************
#  NSO Service Discovery
#  Copyright 2022 Cisco Systems. All rights reserved
# *************************************************************
#  Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements. The ASF licenses this
# file to you under the Apache License, Version 2.0.
# You may not use this file except in compliance with the
# License.  You may obtain a copy of the License at
#
#   http:#www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
# *************************************************************

import os
import sys
import importlib
import copy

import ncs
import _ncs

from ncs.dp import Action

from pathlib import Path
try:
    from .utilities import get_device_config, get_device_ned_id, json_to_str
    from .utilities import read_device_config
except ImportError:
    from utilities import get_device_config, get_device_ned_id, json_to_str
    from utilities import read_device_config

nso_dir = Path(__file__).parent.parent.parent.parent.absolute()
package_nso_to_oc_dir = os.path.join(nso_dir, 'package_nso_to_oc')
if not (os.path.exists(package_nso_to_oc_dir) and os.path.isdir(package_nso_to_oc_dir)):
    nso_dir = Path(__file__).parent.parent.parent.parent.parent.parent.parent.absolute()
    package_nso_to_oc_dir = os.path.join(nso_dir, 'package_nso_to_oc')
    if not (os.path.exists(package_nso_to_oc_dir) and os.path.isdir(package_nso_to_oc_dir)):
        print(f"ERROR: The nso-oc-service package_nso_to_oc is not installed properly ({package_nso_to_oc_dir})")
        exit(1)
sys.path.append(str(nso_dir))
try:
    package_nso_to_oc = importlib.import_module('package_nso_to_oc')
except ModuleNotFoundError as err:
    print(err)
    exit(1)


class DiscoverOcService(Action):

    @Action.action
    def cb_action(self, uinfo, name, kp, _input, output, trans):
        """
        Invoked with device action 'discover-oc-service'.
        The function is called with parameters:
            uinfo -- a UserInfo object
            name -- the tailf:snmp-action name (string)
            kp -- the keypath of the action (HKeypathRef)
            _input -- input node (maagic.Node)
            output -- output node (maagic.Node)
        """
        self.log.info(f"Entered cb_action {name}, on device path: {kp}")
        output.result = "false"
        device_name = str(kp).split('{')[1].split('}')[0]
        root = ncs.maagic.get_root(trans)
        device = root.devices.device[device_name]
        ned_id = get_device_ned_id(device)
        if ned_id not in ['cisco-ios-cli', 'cisco-iosxr-cli']:
            _log_and_result(f"ERROR: The {ned_id} NED is currently not supported by oc-service-discovery package",
                            output, self.log.error)
            return

        openconfig = getattr(device, 'openconfig')
        if openconfig is None:
            _log_and_result(f"ERROR: The nso-oc-service package is not installed properly",
                            output, self.log.error)
            return

        self.log.info(f"Requested discovery for openconfig service: {_input.service}, on device: {device_name}")

        oc_config, leftover = get_oc_service(device.name, ned_id, str(_input.service), self.log, output)

        if oc_config:
            output.result = apply_service(device.name, oc_config, _input.nso_action)
            if _input.show_leftover.exists():
                output.result += f"\nDevice config not in the OC service:\n{json_to_str(leftover)}"


def apply_service(device_name: str, oc_service_config: dict, nso_action: str) -> str:
    service_config = {"tailf-ncs:devices": {"device": [{"name": device_name}]}}
    service_config["tailf-ncs:devices"]["device"][0].update(oc_service_config)
    with ncs.maapi.Maapi() as m:
        with ncs.maapi.Session(m, 'admin', 'system'):
            with m.start_write_trans() as t:
                _ncs.maapi.load_config_cmds(m.msock, t.th,
                                            (_ncs.maapi.CONFIG_JSON +
                                             _ncs.maapi.CONFIG_UNHIDE_ALL +
                                             _ncs.maapi.CONFIG_MERGE),
                                            json_to_str(service_config), '/')
                cp = ncs.maapi.CommitParams()
                if nso_action == 'dry-run':
                    cp.dry_run_cli()
                elif nso_action == 'reconcile-discard-non-service-config':
                    cp.reconcile_discard_non_service_config()
                elif nso_action == 'reconcile':
                    cp.reconcile_keep_non_service_config()

                r = t.apply_params(False, cp)
                if 'local-node' in r:
                    res = "\n"
                    if nso_action == 'dry-run':
                        res += f"\nOpenconfig service discovered:\n{r['local-node']}"
                elif 'error' in r:
                    res = r['error']
                else:
                    res = 'true'
                return res


def build_config_leftover(device_name: str, leftover: dict, keys_include: list) -> dict:
    dev_config = {"devices": {"device": [{"name": device_name, "config": {}}]}}
    for key in keys_include:
        if key in leftover:
            dev_config["devices"]["device"][0]["config"][key] = leftover[key]
    return dev_config


def get_oc_service(device_name: str, ned_id: str, input_service: str, logger, output_=None) -> (dict, dict):
    nso_device_config = get_device_config(device_name)
    # nso_device_config = read_device_config(device_name)
    # print(nso_device_config)
    device_config = nso_device_config["tailf-ncs:devices"]["device"][0]["config"]
    translation_notes = []
    config_leftover = copy.deepcopy(device_config)
    oc = {"mdd:openconfig": {}}
    leftover = {}

    if 'cisco-ios-cli' == ned_id:
        from package_nso_to_oc.xe import xe_network_instances, xe_vlans, xe_interfaces,\
            xe_system, xe_stp, xe_acls, xe_routing_policy
        from package_nso_to_oc import common

        interface_ip_name_dict = common.xe_system_get_interface_ip_address(device_config)
        if 'interfaces' == input_service:
            openconfig_interfaces = xe_interfaces.main(device_config, config_leftover, translation_notes)
            oc['mdd:openconfig'].update(openconfig_interfaces)
            leftover = build_config_leftover(device_name, config_leftover, ["tailf-ned-cisco-ios:interface"])
        elif 'network-instance' == input_service:
            openconfig_interfaces = xe_interfaces.main(device_config, config_leftover, translation_notes)
            openconfig_network_instances =\
                xe_network_instances.main(device_config, config_leftover, translation_notes)
            openconfig_network_instance_default_vlans =\
                xe_vlans.main(device_config, config_leftover, translation_notes)
            openconfig_network_instance = \
                openconfig_network_instances["openconfig-network-instance:network-instances"][
                    "openconfig-network-instance:network-instance"][0]
            openconfig_network_instance.update(
                openconfig_network_instance_default_vlans["openconfig-network-instance:network-instances"][
                    "openconfig-network-instance:network-instance"][0]["openconfig-network-instance:vlans"])
            oc['mdd:openconfig'].update(openconfig_network_instances)
            components = ["tailf-ned-cisco-ios:interface"]
            leftover = build_config_leftover(device_name, config_leftover, components)
        elif 'acl' == input_service:
            openconfig_acls = xe_acls.main(device_config, config_leftover, translation_notes)
            oc['mdd:openconfig'].update(openconfig_acls)
            components = ["openconfig-acl:acl", "openconfig-acl:ip",
                          "tailf-ned-cisco-ios:ntp", "tailf-ned-cisco-ios:line"]
            leftover = build_config_leftover(device_name, config_leftover, components)
        elif 'routing-policy' == input_service:
            openconfig_routing_policy = xe_routing_policy.main(device_config, config_leftover, translation_notes)
            oc['mdd:openconfig'].update(openconfig_routing_policy)
            components = ["openconfig-routing-policy:routing-policy"]
            leftover = build_config_leftover(device_name, config_leftover, components)
        elif 'system' == input_service:
            openconfig_system = xe_system.main(
                device_config, config_leftover, interface_ip_name_dict, translation_notes)
            oc['mdd:openconfig'].update(openconfig_system)
            components = ["openconfig-system:system"]
            leftover = build_config_leftover(device_name, config_leftover, components)
        elif 'stp' == input_service:
            openconfig_stp = xe_stp.main(device_config, config_leftover, translation_notes)
            oc['mdd:openconfig'].update(openconfig_stp)
            components = ["openconfig-spanning-tree:stp"]
            leftover = build_config_leftover(device_name, config_leftover, components)
        else:
            _log_and_result(f"ERROR: Openconfig service {input_service} is not supported on {ned_id} NED",
                            output_, logger.error)
            return {}, leftover

    elif 'cisco-iosxr-cli' == ned_id:
        from package_nso_to_oc.xr import xr_system, xr_interfaces, xr_acls

        if 'interfaces' == input_service:
            openconfig_interfaces = xr_interfaces.main(device_config, config_leftover, translation_notes)
            oc['mdd:openconfig'].update(openconfig_interfaces)
            leftover = build_config_leftover(device_name, config_leftover, ["tailf-ned-cisco-iosxr:interface"])
        elif 'system' == input_service:
            openconfig_system = xr_system.main(device_config, config_leftover, translation_notes)
            oc['mdd:openconfig'].update(openconfig_system)
            components = ["openconfig-system:system"]
            leftover = build_config_leftover(device_name, config_leftover, components)
        elif 'acl' == input_service:
            openconfig_system = xr_acls.main(device_config, config_leftover, translation_notes)
            oc['mdd:openconfig'].update(openconfig_system)
            components = ["openconfig-acl:acl"]
            leftover = build_config_leftover(device_name, config_leftover, components)
        else:
            _log_and_result(f"ERROR: Openconfig service {input_service} is not supported on {ned_id} NED",
                            output_, logger.error)
            return {}, leftover
    return oc, leftover


def _log_and_result(msg, output, log_f):
    log_f(msg)
    if output is not None:
        output.result += f"\n{msg}"


# ---------------------------------------------
# COMPONENT THREAD THAT WILL BE STARTED BY NCS.
# ---------------------------------------------
class DiscoverOcServiceMain(ncs.application.Application):
    def setup(self):
        # The application class sets up logging for us. It is accessible
        # through 'self.log' and is a ncs.log.Log instance.
        self.log.info('DiscoverOcServiceMain RUNNING')

        # Service callbacks require a registration for a 'service point',
        # as specified in the corresponding data model.
        #
        self.register_service('discover-oc-service-action-point', DiscoverOcService)

        # If we registered any callback(s) above, the Application class
        # took care of creating a daemon (related to the service/action point).

        # When this setup method is finished, all registrations are
        # considered done and the application is 'started'.

    def teardown(self):
        # When the application is finished (which would happen if NCS went
        # down, packages were reloaded or some error occurred) this teardown
        # method will be called.

        self.log.info('DiscoverOcServiceMain FINISHED')


if __name__ == '__main__':
    import logging
    import ncs

    mylog = ncs.log.Log(logging.getLogger(__name__))
    dev_name = 'xe-65'
    ned = 'cisco-ios-cli'
    oc_service = 'network-instance'
    oc_cfg, left = get_oc_service(dev_name, ned, oc_service, mylog)
    if oc_cfg:
        print(f"Discovered openconfig service '{oc_service}':")
        print(json_to_str(oc_cfg))
        print("\nNot translated NSO configuration:")
        print(json_to_str(left))
        # exit(0)

        print(f"\nApplying commit dry-run to discovered {oc_service} OC service:")
        result = apply_service(dev_name, oc_cfg, "dry-run")
        print(result)
        if left:
            print("\nDevice config not in the OC service:")
            print(json_to_str(left))
