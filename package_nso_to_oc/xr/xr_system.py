#! /usr/bin/env python3
"""
Translate NSO Device config to MDD OpenConfig

This script will pull a device's configuration from an NSO server, convert the NED structured configuration to
MDD OpenConfig, save the NSO configuration to a file named {device_name}_configuration.json, save the NSO device
configuration minus parts replaced by OpenConfig to a file named {device_name}_configuration_remaining.json,
and save the MDD OpenConfig configuration to a file named {nso_device}_openconfig.json.

The script requires the following environment variables:
NSO_HOST - IP address or hostname for the NSO server
NSO_USERNAME
NSO_PASSWORD
NSO_DEVICE - NSO device name for configuration translation
TEST - True or False. True enables sending the OpenConfig to the NSO server after generation
"""
import copy
import json
import os

openconfig_system = {
    "openconfig-system:system": {
        "openconfig-system:aaa": {},
        "openconfig-system:clock": {},
        "openconfig-system:config": {},
        "openconfig-system:dns": {},
        "openconfig-system:logging": {},
        "openconfig-system:ntp": {
            "openconfig-system:config": {},
            "openconfig-system:ntp-keys": {
                "openconfig-system:ntp-key": []},
            "openconfig-system:servers": {
                "openconfig-system:server": []}
        },
        "openconfig-system:ssh-server": {"openconfig-system:config": {}}
    }
}


def xr_system_config(config_before: dict, config_leftover: dict) -> None:
    """
    Translates NSO XE NED to MDD OpenConfig System Config
    """
    openconfig_system_config = openconfig_system["openconfig-system:system"]["openconfig-system:config"]
    defualt_secret = config_before.get("tailf-ned-cisco-ios-xr:line", {}).get("default", {}).get("secret", {})
    console_exec_timeout = config_before["tailf-ned-cisco-ios-xr:line"].get("console", {}).get("exec-timeout", {})

    openconfig_system_config["openconfig-system:hostname"] = config_before["tailf-ned-cisco-ios-xr:hostname"]
    del config_leftover["tailf-ned-cisco-ios-xr:hostname"]

    if config_before.get("tailf-ned-cisco-ios-xr:banner", {}).get("login").get("message"):
        openconfig_system_config["openconfig-system:login-banner"] = (
            config_before.get("tailf-ned-cisco-ios-xr:banner",{})
            .get("login")
            .get("message")
        )
        del config_leftover["tailf-ned-cisco-ios-xr:banner"]["login"]

    if config_before.get("tailf-ned-cisco-ios-xr:banner", {}).get("motd").get("message"):
        openconfig_system_config["openconfig-system:motd-banner"] = (
            config_before.get("tailf-ned-cisco-ios-xr:banner",{})
            .get("motd")
            .get("message")
        )
        del config_leftover["tailf-ned-cisco-ios-xr:banner"]["motd"]

    if config_before.get("tailf-ned-cisco-ios-xr:domain", {}).get("name"):
        openconfig_system_config["openconfig-system:domain-name"] = (
            config_before.get("tailf-ned-cisco-ios-xr:domain", {})
            .get("name")
        )
        del config_leftover["tailf-ned-cisco-ios-xr:domain"]["name"]


    if defualt_secret.get("secret") and defualt_secret.get("type") == "0":
        openconfig_system_config["openconfig-system-ext:enable-secret"] = defualt_secret.get("secret")
        del config_leftover["tailf-ned-cisco-ios-xr:line"]["default"]["secret"]

    if console_exec_timeout.get('minutes') or console_exec_timeout.get('seconds'):
        seconds = console_exec_timeout.get('minutes') * 60
        seconds += console_exec_timeout.get('seconds', 0)
        openconfig_system_config["openconfig-system-ext:console-exec-timeout-seconds"] = seconds
        del config_leftover["tailf-ned-cisco-ios-xr:line"]["console"]["exec-timeout"]

def main(before: dict, leftover: dict) -> dict:
    """
    Translates NSO Device configurations to MDD OpenConfig configurations.

    Requires environment variables:
    NSO_HOST: str
    NSO_USERNAME: str
    NSO_PASSWORD: str
    NSO_DEVICE: str
    TEST - If True, sends generated OC configuration to NSO Server: str

    :param before: Original NSO Device configuration: dict
    :param leftover: NSO Device configuration minus configs replaced with MDD OC: dict
    :param if_ip: Map of interface names to IP addresses: dict
    :return: MDD Openconfig System configuration: dict
    """

    xr_system_config(before, leftover)

    return openconfig_system


if __name__ == "__main__":
    import sys

    sys.path.append("../../")
    sys.path.append("../../../")
    from package_nso_to_oc import common

    nso_host = os.environ.get("NSO_HOST")
    nso_username = os.environ.get("NSO_USERNAME", "ubuntu")
    nso_password = os.environ.get("NSO_PASSWORD", "admin")
    nso_device = os.environ.get("NSO_DEVICE", "xr1")
    test = os.environ.get("TEST", "False")

    config_before_dict = common.nso_get_device_config(nso_host, nso_username, nso_password, nso_device)
    config_leftover_dict = copy.deepcopy(config_before_dict)
    main(config_before_dict, config_leftover_dict)

    print(json.dumps(openconfig_system, indent=4))
    with open(f"../{nso_device}_configuration.json", "w") as b:
        b.write(json.dumps(config_before_dict, indent=4))
    with open(f"../{nso_device}_configuration_remaining.json", "w") as a:
        a.write(json.dumps(config_leftover_dict, indent=4))
    with open(f"../{nso_device}_openconfig_system.json", "w") as o:
        o.write(json.dumps(openconfig_system, indent=4))

    if test == "True":
        common.test_nso_program_oc(nso_host, nso_username, nso_password, nso_device, openconfig_system)
