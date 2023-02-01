#! /usr/bin/env python3
"""
Translate NSO Device config to MDD OpenConfig

This script will pull a device's configuration from an NSO server, convert the NED structured configuration to
MDD OpenConfig, save the NSO configuration to a file named {device_name}_full_ned_configuration.json, save the
NSO device configuration minus parts replaced by OpenConfig to a file named
{device_name}_full_ned_configuration_remaining.json, and save the MDD OpenConfig configuration to a file named
{nso_device}_full_openconfig.json.

The script requires the following environment variables:
always:
- NSO_DEVICE - NSO device name for configuration translation
- TEST - True or False (default False). True enables sending the OpenConfig to the NSO server after generation
if pulling configs from NSO:
- NSO_URL - URL for the NSO server
- NSO_USERNAME
- NSO_PASSWORD
elif reading in from file:
- NSO_NED_FILE (path and filename)
"""

import copy
import os

import common
from xe import main_xe
from xr import main_xr


if __name__ == "__main__":
    nso_api_url = os.environ.get("NSO_URL", 'http://localhost')
    nso_username = os.environ.get("NSO_USERNAME", "admin")
    nso_password = os.environ.get("NSO_PASSWORD", "admin")
    nso_device = os.environ.get("NSO_DEVICE", "xr")
    device_os = os.environ.get("DEVICE_OS", common.XR)
    test = os.environ.get("TEST", "False")

    # Append any pertinent notes here. This will be printed out in output_data directory
    translation_notes = []
    config_before_dict = common.nso_get_device_config(nso_api_url, nso_username, nso_password, nso_device)
    configs_leftover = copy.deepcopy(config_before_dict)
    oc = {"mdd:openconfig": {}}

    if device_os == common.XE:
        main_xe.build_xe_to_oc(config_before_dict, configs_leftover, oc, translation_notes)
    elif device_os == common.XR:
        main_xr.build_xr_to_oc(config_before_dict, configs_leftover, oc, translation_notes)

    config_name = ""
    config_remaining_name = "_remaining"
    oc_name = "_openconfig"
    common.print_and_test_configs(nso_device, config_before_dict, configs_leftover, oc, config_name,
                                  config_remaining_name, oc_name, translation_notes)
