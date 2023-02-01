#! /usr/bin/env python3
"""
Translate NSO Device config to MDD OpenConfig

This script will pull a device's configuration from an NSO server, convert the NED structured configuration to
MDD OpenConfig, save the NSO configuration to a file named {device_name}_configuration.json, save the NSO device
configuration minus parts replaced by OpenConfig to a file named {device_name}_configuration_remaining.json,
and save the MDD OpenConfig configuration to a file named {nso_device}_openconfig.json.

The script requires the following environment variables:
NSO_URL - URL for the NSO server
NSO_USERNAME
NSO_PASSWORD
NSO_DEVICE - NSO device name for configuration translation
TEST - True or False. True enables sending the OpenConfig to the NSO server after generation
"""

import sys
from importlib.util import find_spec

TACACS = "tacacs"
RADIUS = "radius"
system_notes = []

openconfig_system = {
    "openconfig-system:system": {
        "openconfig-system:aaa": {
            "openconfig-system:server-groups": {
                "openconfig-system:server-group": []},
            "openconfig-system:accounting": {},
            "openconfig-system:authorization": {},
            "openconfig-system:authentication": {}
        },
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
        "openconfig-system:ssh-server": {
            "openconfig-system:config": {},
            "openconfig-system-ext:algorithm": {
                "openconfig-system-ext:config": {}
            }
        },
        "openconfig-system-ext:services": {
            "openconfig-system-ext:http": {
                "openconfig-system-ext:config": {}
            },
            "openconfig-system-ext:config": {},
            "openconfig-system-ext:login-security-policy": {
                "openconfig-system-ext:config": {},
                "openconfig-system-ext:block-for": {"openconfig-system-ext:config": {}}
            },
            "openconfig-system-ext:boot-network": {
                "openconfig-system-ext:config": {},
            }
        }
    }
}

def xe_system_services(config_before: dict, config_leftover: dict) -> None:
    """
    Translates NSO XE NED to MDD OpenConfig System Services
    """
    openconfig_system_services = openconfig_system["openconfig-system:system"]["openconfig-system-ext:services"]
    if config_before.get("tailf-ned-cisco-ios:ip", {}).get("domain", {}).get("lookup-conf", {}).get("lookup",
                                                                                                    True) is False:
        openconfig_system_services["openconfig-system-ext:config"]["openconfig-system-ext:ip-domain-lookup"] = False
        del config_leftover["tailf-ned-cisco-ios:ip"]["domain"]["lookup-conf"]
    else:
        openconfig_system_services["openconfig-system-ext:config"]["openconfig-system-ext:ip-domain-lookup"] = True
    # login on-success log
    if type(config_before.get("tailf-ned-cisco-ios:login", {}).get("on-success", {}).get("log", '')) is list:
        openconfig_system_services["openconfig-system-ext:login-security-policy"]["openconfig-system-ext:config"][
            "openconfig-system-ext:on-success"] = True
        del config_leftover["tailf-ned-cisco-ios:login"]["on-success"]["log"]
    else:
        openconfig_system_services["openconfig-system-ext:login-security-policy"]["openconfig-system-ext:config"][
            "openconfig-system-ext:on-success"] = False
    # login on-failure log
    if type(config_before.get("tailf-ned-cisco-ios:login", {}).get("on-failure", {}).get("log", '')) is list:
        openconfig_system_services["openconfig-system-ext:login-security-policy"]["openconfig-system-ext:config"][
            "openconfig-system-ext:on-failure"] = True
        del config_leftover["tailf-ned-cisco-ios:login"]["on-failure"]["log"]
    else:
        openconfig_system_services["openconfig-system-ext:login-security-policy"]["openconfig-system-ext:config"][
            "openconfig-system-ext:on-failure"] = False
    # login block-for
    if config_before.get("tailf-ned-cisco-ios:login", {}).get("block-for", {}).get("seconds"):
        openconfig_system_services["openconfig-system-ext:login-security-policy"]["openconfig-system-ext:block-for"]["openconfig-system-ext:config"]["openconfig-system-ext:seconds"] = config_before.get("tailf-ned-cisco-ios:login", {}).get("block-for", {}).get("seconds")
        del config_leftover["tailf-ned-cisco-ios:login"]["block-for"]["seconds"]
    if config_before.get("tailf-ned-cisco-ios:login", {}).get("block-for", {}).get("attempts"):
        openconfig_system_services["openconfig-system-ext:login-security-policy"]["openconfig-system-ext:block-for"]["openconfig-system-ext:config"]["openconfig-system-ext:attempts"] = config_before.get("tailf-ned-cisco-ios:login", {}).get("block-for", {}).get("attempts")
        del config_leftover["tailf-ned-cisco-ios:login"]["block-for"]["attempts"]
    if config_before.get("tailf-ned-cisco-ios:login", {}).get("block-for", {}).get("within"):
        openconfig_system_services["openconfig-system-ext:login-security-policy"]["openconfig-system-ext:block-for"]["openconfig-system-ext:config"]["openconfig-system-ext:within"] = config_before.get("tailf-ned-cisco-ios:login", {}).get("block-for", {}).get("within")
        del config_leftover["tailf-ned-cisco-ios:login"]["block-for"]["within"]
    # Archive Logging
    if type(config_before.get("tailf-ned-cisco-ios:archive", {}).get("log", {}).get("config", {}).get("logging", {}).get("enable", '')) is list:
        openconfig_system_services["openconfig-system-ext:config"]["openconfig-system-ext:archive-logging"] = True
        del config_leftover["tailf-ned-cisco-ios:archive"]["log"]["config"]["logging"]["enable"]
    else:
        openconfig_system_services["openconfig-system-ext:config"]["openconfig-system-ext:archive-logging"] = False
    # boot network
    if not config_before.get("tailf-ned-cisco-ios:boot", {}).get("network"):
        openconfig_system_services["openconfig-system-ext:boot-network"]["openconfig-system-ext:config"]["openconfig-system-ext:bootnetwork-enabled"] = "DISABLED"
    else:
        openconfig_system_services["openconfig-system-ext:boot-network"]["openconfig-system-ext:config"]["openconfig-system-ext:bootnetwork-enabled"] = "MANUAL_CONFIG"
    # IP bootp server
    if config_before.get("tailf-ned-cisco-ios:ip", {}).get("bootp", {}).get("server", True) is False:
        openconfig_system_services["openconfig-system-ext:config"]["openconfig-system-ext:ip-bootp-server"] = False
        del config_leftover["tailf-ned-cisco-ios:ip"]["bootp"]["server"]
    else:
        openconfig_system_services["openconfig-system-ext:config"]["openconfig-system-ext:ip-bootp-server"] = True
    # IP dns server
    if type(config_before.get("tailf-ned-cisco-ios:ip", {}).get("dns", {}).get("server", '')) is dict:
        openconfig_system_services["openconfig-system-ext:config"]["openconfig-system-ext:ip-dns-server"] = True
        del config_leftover["tailf-ned-cisco-ios:ip"]["dns"]["server"]
    else:
        openconfig_system_services["openconfig-system-ext:config"]["openconfig-system-ext:ip-dns-server"] = False
    # IP identd
    if type(config_before.get("tailf-ned-cisco-ios:ip", {}).get("identd", '')) is list:
        openconfig_system_services["openconfig-system-ext:config"]["openconfig-system-ext:ip-identd"] = True
        del config_leftover["tailf-ned-cisco-ios:ip"]["identd"]
    else:
        openconfig_system_services["openconfig-system-ext:config"]["openconfig-system-ext:ip-identd"] = False
    # IP http server
    if config_before.get("tailf-ned-cisco-ios:ip", {}).get("http", {}).get("server", True) is False:
        openconfig_system_services["openconfig-system-ext:http"]["openconfig-system-ext:config"]["openconfig-system-ext:http-enabled"] = False
        del config_leftover["tailf-ned-cisco-ios:ip"]["http"]["server"]
    else:
        openconfig_system_services["openconfig-system-ext:http"]["openconfig-system-ext:config"]["openconfig-system-ext:http-enabled"] = True
    # IP RCMD rcp-enable
    if type(config_before.get("tailf-ned-cisco-ios:ip", {}).get("rcmd", {}).get("rcp-enable", '')) is list:
        openconfig_system_services["openconfig-system-ext:config"]["openconfig-system-ext:ip-rcmd-rcp-enable"] = True
        del config_leftover["tailf-ned-cisco-ios:ip"]["rcmd"]["rcp-enable"]
    else:
        openconfig_system_services["openconfig-system-ext:config"]["openconfig-system-ext:ip-rcmd-rcp-enable"] = False
    # IP RCMD rsh-enable
    if type(config_before.get("tailf-ned-cisco-ios:ip", {}).get("rcmd", {}).get("rsh-enable", '')) is list:
        openconfig_system_services["openconfig-system-ext:config"]["openconfig-system-ext:ip-rcmd-rsh-enable"] = True
        del config_leftover["tailf-ned-cisco-ios:ip"]["rcmd"]["rsh-enable"]
    else:
        openconfig_system_services["openconfig-system-ext:config"]["openconfig-system-ext:ip-rcmd-rsh-enable"] = False
    # IP finger
    if type(config_before.get("tailf-ned-cisco-ios:ip", {}).get("finger", '')) is dict:
        openconfig_system_services["openconfig-system-ext:config"]["openconfig-system-ext:finger"] = True
        del config_leftover["tailf-ned-cisco-ios:ip"]["finger"]
    else:
        openconfig_system_services["openconfig-system-ext:config"]["openconfig-system-ext:finger"] = False
    # service config
    if type(config_before.get("tailf-ned-cisco-ios:service", {}).get("config", '')) is list:
        openconfig_system_services["openconfig-system-ext:config"]["openconfig-system-ext:service-config"] = True
        del config_leftover["tailf-ned-cisco-ios:service"]["config"]
    else:
        openconfig_system_services["openconfig-system-ext:config"]["openconfig-system-ext:service-config"] = False
    # service tcp-small-servers
    if type(config_before.get("tailf-ned-cisco-ios:service", {}).get("tcp-small-servers", '')) is list:
        openconfig_system_services["openconfig-system-ext:config"]["openconfig-system-ext:service-tcp-small-servers"] = True
        del config_leftover["tailf-ned-cisco-ios:service"]["tcp-small-servers"]
    else:
        openconfig_system_services["openconfig-system-ext:config"]["openconfig-system-ext:service-tcp-small-servers"] = False
    # service udp-small-servers
    if type(config_before.get("tailf-ned-cisco-ios:service", {}).get("udp-small-servers", '')) is list:
        openconfig_system_services["openconfig-system-ext:config"]["openconfig-system-ext:service-udp-small-servers"] = True
        del config_leftover["tailf-ned-cisco-ios:service"]["udp-small-servers"]
    else:
        openconfig_system_services["openconfig-system-ext:config"]["openconfig-system-ext:service-udp-small-servers"] = False
    # service pad
    if config_before.get("tailf-ned-cisco-ios:service", {}).get("conf", {}).get("pad", True) is False:
        openconfig_system_services["openconfig-system-ext:config"]["openconfig-system-ext:service-pad"] = False
        del config_leftover["tailf-ned-cisco-ios:service"]["conf"]["pad"]
    else:
        openconfig_system_services["openconfig-system-ext:config"]["openconfig-system-ext:service-pad"] = True
    # service password-encryption
    if type(config_before.get("tailf-ned-cisco-ios:service", {}).get("password-encryption", '')) is dict:
        openconfig_system_services["openconfig-system-ext:config"]["openconfig-system-ext:service-password-encryption"] = True
        del config_leftover["tailf-ned-cisco-ios:service"]["password-encryption"]
    else:
        openconfig_system_services["openconfig-system-ext:config"]["openconfig-system-ext:service-password-encryption"] = False


def xe_system_config(config_before: dict, config_leftover: dict) -> None:
    """
    Translates NSO XE NED to MDD OpenConfig System Config
    """
    openconfig_system_config = openconfig_system["openconfig-system:system"]["openconfig-system:config"]

    if "tailf-ned-cisco-ios:hostname" in config_before:
        openconfig_system_config["openconfig-system:hostname"] = config_before["tailf-ned-cisco-ios:hostname"]
        del config_leftover["tailf-ned-cisco-ios:hostname"]

    if config_before.get("tailf-ned-cisco-ios:banner", {}).get("login"):
        openconfig_system_config["openconfig-system:login-banner"] = config_before.get("tailf-ned-cisco-ios:banner",
                                                                                       {}).get("login")
        del config_leftover["tailf-ned-cisco-ios:banner"]["login"]

    if config_before.get("tailf-ned-cisco-ios:banner", {}).get("motd"):
        openconfig_system_config["openconfig-system:motd-banner"] = config_before.get("tailf-ned-cisco-ios:banner",
                                                                                      {}).get("motd")
        del config_leftover["tailf-ned-cisco-ios:banner"]["motd"]

    if config_before.get("tailf-ned-cisco-ios:ip", {}).get("domain", {}).get("name"):
        openconfig_system_config["openconfig-system:domain-name"] = config_before.get("tailf-ned-cisco-ios:ip", {}).get(
            "domain", {}).get("name")
        del config_leftover["tailf-ned-cisco-ios:ip"]["domain"]["name"]

    if config_before.get("tailf-ned-cisco-ios:ip", {}).get("options", {}).get("drop"):
        openconfig_system_config["openconfig-system-ext:ip-options"] = "DROP"
        del config_leftover["tailf-ned-cisco-ios:ip"]["options"]

    if config_before.get("tailf-ned-cisco-ios:ip", {}).get("options", {}).get("ignore"):
        openconfig_system_config["openconfig-system-ext:ip-options"] = "IGNORE"
        del config_leftover["tailf-ned-cisco-ios:ip"]["options"]

    if (config_before.get("tailf-ned-cisco-ios:enable", {}).get("secret", {}).get("secret")) and \
            (config_before.get("tailf-ned-cisco-ios:enable", {}).get("secret", {}).get("type") == "0"):
        openconfig_system_config["openconfig-system-ext:enable-secret"] = config_before.get(
            "tailf-ned-cisco-ios:enable", {}).get("secret", {}).get("secret")
        del config_leftover["tailf-ned-cisco-ios:enable"]

    if "tailf-ned-cisco-ios:line" in config_before and\
            config_before["tailf-ned-cisco-ios:line"]["console"][0].get("exec-timeout"):
        seconds = config_before["tailf-ned-cisco-ios:line"]["console"][0]["exec-timeout"].get("minutes", 0) * 60
        seconds += config_before["tailf-ned-cisco-ios:line"]["console"][0]["exec-timeout"].get("seconds", 0)
        openconfig_system_config["openconfig-system-ext:console-exec-timeout-seconds"] = seconds
        del config_leftover["tailf-ned-cisco-ios:line"]["console"][0]["exec-timeout"]


def xe_system_ssh_server(config_before: dict, config_leftover: dict) -> None:
    """
    Translates NSO XE NED to MDD OpenConfig System SSH Server
    """
    openconfig_system_ssh_server_config = openconfig_system["openconfig-system:system"]["openconfig-system:ssh-server"]["openconfig-system:config"]
    openconfig_system_ssh_server_alg_config = openconfig_system["openconfig-system:system"]["openconfig-system:ssh-server"]["openconfig-system-ext:algorithm"]["openconfig-system-ext:config"]

    if config_before.get("tailf-ned-cisco-ios:ip", {}).get("ssh", {}).get("time-out"):
        openconfig_system_ssh_server_config["openconfig-system-ext:ssh-timeout"] = config_before.get(
            "tailf-ned-cisco-ios:ip", {}).get("ssh", {}).get("time-out")
        del config_leftover["tailf-ned-cisco-ios:ip"]["ssh"]["time-out"]

    if config_before.get("tailf-ned-cisco-ios:ip", {}).get("ssh", {}).get("version"):
        if config_before.get("tailf-ned-cisco-ios:ip", {}).get("ssh", {}).get("version") == 1:
            openconfig_system_ssh_server_config["openconfig-system:protocol-version"] = "V1"
        elif config_before.get("tailf-ned-cisco-ios:ip", {}).get("ssh", {}).get("version") == 2:
            openconfig_system_ssh_server_config["openconfig-system:protocol-version"] = "V2"
        del config_leftover["tailf-ned-cisco-ios:ip"]["ssh"]["version"]
    else:
        openconfig_system_ssh_server_config["openconfig-system:protocol-version"] = "V1_V2"

    if config_before.get("tailf-ned-cisco-ios:ip", {}).get("ssh", {}).get("source-interface"):
        for i, n in config_before["tailf-ned-cisco-ios:ip"]["ssh"]["source-interface"].items():
            openconfig_system_ssh_server_config["openconfig-system-ext:ssh-source-interface"] = f"{i}{n}"
        del config_leftover["tailf-ned-cisco-ios:ip"]["ssh"]["source-interface"]

    if "tailf-ned-cisco-ios:line" in config_before:
        if config_before["tailf-ned-cisco-ios:line"]["vty"][0].get("exec-timeout"):
            seconds = config_before["tailf-ned-cisco-ios:line"]["vty"][0]["exec-timeout"].get("minutes", 0) * 60
            seconds += config_before["tailf-ned-cisco-ios:line"]["vty"][0]["exec-timeout"].get("seconds", 0)
            openconfig_system_ssh_server_config["openconfig-system:timeout"] = seconds
            del config_leftover["tailf-ned-cisco-ios:line"]["vty"][0]["exec-timeout"]

        if config_before["tailf-ned-cisco-ios:line"]["vty"][0].get("absolute-timeout"):
            openconfig_system_ssh_server_config["openconfig-system-ext:absolute-timeout-minutes"] = \
                config_before["tailf-ned-cisco-ios:line"]["vty"][0]["absolute-timeout"]
            del config_leftover["tailf-ned-cisco-ios:line"]["vty"][0]["absolute-timeout"]

        if config_before["tailf-ned-cisco-ios:line"]["vty"][0].get("session-limit"):
            openconfig_system_ssh_server_config["openconfig-system:session-limit"] = \
                config_before["tailf-ned-cisco-ios:line"]["vty"][0].get("session-limit")
            del config_leftover["tailf-ned-cisco-ios:line"]["vty"][0]["session-limit"]

    if type(config_before.get("tailf-ned-cisco-ios:ip", {}).get("ssh", {}).get("server", {}).get("algorithm", {}).get("encryption", '')) is list:
        openconfig_system_ssh_server_alg_config["openconfig-system-ext:encryption"] = config_before.get("tailf-ned-cisco-ios:ip", {}).get("ssh", {}).get("server", {}).get("algorithm", {}).get("encryption")
        del config_leftover["tailf-ned-cisco-ios:ip"]["ssh"]["server"]["algorithm"]["encryption"]

    if type(config_before.get("tailf-ned-cisco-ios:ip", {}).get("ssh", {}).get("server", {}).get("algorithm", {}).get("mac", '')) is list:
        openconfig_system_ssh_server_alg_config["openconfig-system-ext:mac"] = config_before.get("tailf-ned-cisco-ios:ip", {}).get("ssh", {}).get("server", {}).get("algorithm", {}).get("mac")
        del config_leftover["tailf-ned-cisco-ios:ip"]["ssh"]["server"]["algorithm"]["mac"]

def xe_add_oc_ntp_server(before_ntp_server_list: list, after_ntp_server_list: list, openconfig_ntp_server_list: list,
                         ntp_type: str, ntp_vrf: str, if_ip: dict) -> None:
    """Generate Openconfig NTP server configurations"""
    for ntp_server_index, ntp_server in enumerate(before_ntp_server_list):
        ntp_server_temp = {"openconfig-system:address": ntp_server["name"],
                           "openconfig-system:config": {
                               "openconfig-system:address": ntp_server["name"],
                               "openconfig-system:association-type": ntp_type,
                               "openconfig-system:port": 123,
                               "openconfig-system:version": 4
                           }}
        # version
        if ntp_server.get("version"):
            ntp_server_temp["openconfig-system:config"]["openconfig-system:version"] = ntp_server.get("version")
            del after_ntp_server_list[ntp_server_index]["version"]
        # iburst
        if type(ntp_server.get("iburst", "")) is list:
            ntp_server_temp["openconfig-system:config"]["openconfig-system:iburst"] = True
            del after_ntp_server_list[ntp_server_index]["iburst"]
        else:
            ntp_server_temp["openconfig-system:config"]["openconfig-system:iburst"] = False
        # prefer
        if type(ntp_server.get("prefer", "")) is list:
            ntp_server_temp["openconfig-system:config"]["openconfig-system:prefer"] = True
            del after_ntp_server_list[ntp_server_index]["prefer"]
        else:
            ntp_server_temp["openconfig-system:config"]["openconfig-system:prefer"] = False
        # authentication key
        if ntp_server.get("key"):
            ntp_server_temp["openconfig-system:config"]["openconfig-system-ext:ntp-auth-key-id"] = ntp_server.get("key")
            del after_ntp_server_list[ntp_server_index]["key"]
        # source interface
        if ntp_server.get("source"):
            for k, v in ntp_server.get("source").items():
                nso_source_interface = f"{k}{v}"
                ntp_server_temp["openconfig-system:config"]["openconfig-system-ext:ntp-source-address"] = if_ip.get(
                    nso_source_interface)
                del after_ntp_server_list[ntp_server_index]["source"]
        # vrf
        if ntp_vrf:
            ntp_server_temp["openconfig-system:config"]["openconfig-system-ext:ntp-use-vrf"] = ntp_vrf

        openconfig_ntp_server_list.append(ntp_server_temp)


def xe_system_ntp(config_before: dict, config_leftover: dict, if_ip: dict) -> None:
    """
    Translates NSO XE NED to MDD OpenConfig System NTP
    """
    openconfig_system_ntp = openconfig_system["openconfig-system:system"]["openconfig-system:ntp"]

    if config_before.get("tailf-ned-cisco-ios:ntp", {}).get("authenticate"):
        openconfig_system_ntp["openconfig-system:config"]["openconfig-system:enable-ntp-auth"] = True
        del config_leftover["tailf-ned-cisco-ios:ntp"]["authenticate"]

    if config_before.get("tailf-ned-cisco-ios:ntp", {}).get("logging"):
        openconfig_system_ntp["openconfig-system:config"]["openconfig-system-ext:ntp-enable-logging"] = True
        del config_leftover["tailf-ned-cisco-ios:ntp"]["logging"]

    if config_before.get("tailf-ned-cisco-ios:ntp", {}).get("source"):
        for i, n in config_before.get("tailf-ned-cisco-ios:ntp", {}).get("source").items():
            source_interface = f"{i}{n}"
            source_interface_ip = if_ip.get(source_interface)
            openconfig_system_ntp["openconfig-system:config"][
                "openconfig-system:ntp-source-address"] = source_interface_ip
        del config_leftover["tailf-ned-cisco-ios:ntp"]["source"]

    if config_before.get("tailf-ned-cisco-ios:ntp", {}).get("trusted-key") and config_before.get(
            "tailf-ned-cisco-ios:ntp", {}).get("authentication-key"):
        trusted_key_numbers = [x["key-number"] for x in
                               config_before.get("tailf-ned-cisco-ios:ntp", {}).get("trusted-key")]
        for auth_key in config_before.get("tailf-ned-cisco-ios:ntp", {}).get("authentication-key"):
            if auth_key["number"] in trusted_key_numbers and auth_key.get("md5"):
                key_dict = {"openconfig-system:key-id": auth_key["number"],
                            "openconfig-system:config": {"openconfig-system:key-id": auth_key["number"],
                                                         "openconfig-system:key-type": "NTP_AUTH_MD5",
                                                         "openconfig-system:key-value": auth_key.get("md5").get(
                                                             "secret")}
                            }
                openconfig_system_ntp["openconfig-system:ntp-keys"]["openconfig-system:ntp-key"].append(key_dict)

                config_leftover["tailf-ned-cisco-ios:ntp"]["authentication-key"].remove(auth_key)
                try:  # trusted-keys can use a starting number, hyphen, and ending number in NED. Skip remove if this is the case.
                    config_leftover["tailf-ned-cisco-ios:ntp"]["trusted-key"].remove({"key-number": auth_key["number"]})
                except:
                    pass

    if config_before.get("tailf-ned-cisco-ios:ntp", {}).get("peer") or config_before.get("tailf-ned-cisco-ios:ntp",
                                                                                         {}).get("server"):
        openconfig_system_ntp.update({"openconfig-system:servers": {"openconfig-system:server": []}})
        openconfig_system_ntp_server_list = openconfig_system_ntp["openconfig-system:servers"][
            "openconfig-system:server"]
        # NTP SERVER
        if config_before.get("tailf-ned-cisco-ios:ntp", {}).get("server", {}).get("peer-list"):
            xe_add_oc_ntp_server(config_before["tailf-ned-cisco-ios:ntp"]["server"]["peer-list"],
                                 config_leftover["tailf-ned-cisco-ios:ntp"]["server"]["peer-list"],
                                 openconfig_system_ntp_server_list, "SERVER", "", if_ip)
        # NTP PEER
        if config_before.get("tailf-ned-cisco-ios:ntp", {}).get("peer", {}).get("peer-list"):
            xe_add_oc_ntp_server(config_before["tailf-ned-cisco-ios:ntp"]["peer"]["peer-list"],
                                 config_leftover["tailf-ned-cisco-ios:ntp"]["peer"]["peer-list"],
                                 openconfig_system_ntp_server_list, "PEER", "", if_ip)
        # VRF SERVER
        if config_before.get("tailf-ned-cisco-ios:ntp", {}).get("server", {}).get("vrf"):
            for nso_vrf_index, vrf in enumerate(
                    config_before.get("tailf-ned-cisco-ios:ntp", {}).get("server", {}).get("vrf")):
                xe_add_oc_ntp_server(
                    config_before["tailf-ned-cisco-ios:ntp"]["server"]["vrf"][nso_vrf_index]["peer-list"],
                    config_leftover["tailf-ned-cisco-ios:ntp"]["server"]["vrf"][nso_vrf_index]["peer-list"],
                    openconfig_system_ntp_server_list, "SERVER", vrf["name"], if_ip)
        # VRF PEER
        if config_before.get("tailf-ned-cisco-ios:ntp", {}).get("peer", {}).get("vrf"):
            for nso_vrf_index, vrf in enumerate(
                    config_before.get("tailf-ned-cisco-ios:ntp", {}).get("peer", {}).get("vrf")):
                xe_add_oc_ntp_server(
                    config_before["tailf-ned-cisco-ios:ntp"]["peer"]["vrf"][nso_vrf_index]["peer-list"],
                    config_leftover["tailf-ned-cisco-ios:ntp"]["peer"]["vrf"][nso_vrf_index]["peer-list"],
                    openconfig_system_ntp_server_list, "PEER", vrf["name"], if_ip)


def xe_system_aaa(config_before: dict, config_leftover: dict, if_ip: dict) -> None:
    """
    Translates NSO XE NED to MDD OpenConfig System AAA
    """
    oc_system_server_group = openconfig_system["openconfig-system:system"]["openconfig-system:aaa"]["openconfig-system:server-groups"]["openconfig-system:server-group"]
    oc_system_aaa_accounting = openconfig_system["openconfig-system:system"]["openconfig-system:aaa"]["openconfig-system:accounting"]
    oc_system_aaa_authorization = openconfig_system["openconfig-system:system"]["openconfig-system:aaa"]["openconfig-system:authorization"]
    oc_system_aaa_authentication = openconfig_system["openconfig-system:system"]["openconfig-system:aaa"]["openconfig-system:authentication"]
    tacacs_group_list = config_before.get("tailf-ned-cisco-ios:aaa", {}).get("group", {}).get("server", {}).get("tacacs-plus")
    radius_group_list = config_before.get("tailf-ned-cisco-ios:aaa", {}).get("group", {}).get("server", {}).get("radius")
    tacacs_server_list = config_before.get("tailf-ned-cisco-ios:tacacs", {}).get("server")
    radius_server_list = config_before.get("tailf-ned-cisco-ios:radius", {}).get("server")
    accounting_dict = config_before.get("tailf-ned-cisco-ios:aaa", {}).get("accounting")
    authorization_dict = config_before.get("tailf-ned-cisco-ios:aaa", {}).get("authorization")
    authentication_dict = config_before.get("tailf-ned-cisco-ios:aaa", {}).get("authentication")
    authentication_user_list = config_before.get("tailf-ned-cisco-ios:username")

    # TACACS GROUP
    if tacacs_group_list:
        for tacacs_group_index, tacacs_group in enumerate(tacacs_group_list):
            process_aaa_tacacs(oc_system_server_group, config_leftover, if_ip, tacacs_group_index, tacacs_group, tacacs_server_list)

    # RADIUS GROUP
    if radius_group_list:
        for radius_group_index, radius_group in enumerate(radius_group_list):
            process_aaa_radius(oc_system_server_group, config_leftover, if_ip, radius_group_index, radius_group, radius_server_list)

    # AAA ACCOUNTING
    if accounting_dict:
        if accounting_dict.get("commands") or accounting_dict.get("exec"):
            temp_aaa_accounting = {
                "openconfig-system:config": set_accounting_method(oc_system_aaa_accounting, config_leftover, accounting_dict),
                "openconfig-system:events": set_accounting_event(oc_system_aaa_accounting, config_leftover, accounting_dict)
            }
            oc_system_aaa_accounting.update(temp_aaa_accounting)

    # AAA AUTHORIZATION
    if authorization_dict:
        if authorization_dict.get("commands") or authorization_dict.get("exec"):
            temp_aaa_authorization = {
                "openconfig-system:config": set_authorization_method(oc_system_aaa_authorization, config_leftover, authorization_dict),
                "openconfig-system:events": set_authorization_event(oc_system_aaa_authorization, config_leftover, authorization_dict)
            }
            oc_system_aaa_authorization.update(temp_aaa_authorization)

    # AAA AUTHENTICATION
    if authentication_dict or authentication_user_list:
        temp_aaa_authentication = {
            "openconfig-system:config": set_authentication_method(oc_system_aaa_authentication, config_leftover, authentication_dict),
            "openconfig-system:admin-user": set_authentication_admin(oc_system_aaa_authentication, config_leftover, authentication_user_list),
            "openconfig-system:users": set_authentication_user(oc_system_aaa_authentication, config_leftover, authentication_user_list)
        }
        oc_system_aaa_authentication.update(temp_aaa_authentication)

        updated_usernames = []

        for username in config_leftover.get("tailf-ned-cisco-ios:username", []):
            if username:
                updated_usernames.append(username)

        if len(updated_usernames) > 0:
            config_leftover["tailf-ned-cisco-ios:username"] = updated_usernames
        elif "tailf-ned-cisco-ios:username" in config_leftover:
            del config_leftover["tailf-ned-cisco-ios:username"]

    cleanup_server_access(config_leftover, f"{TACACS}-plus", TACACS)
    cleanup_server_access(config_leftover, RADIUS, RADIUS)

def process_aaa_tacacs(oc_system_server_group, config_leftover, if_ip, tacacs_group_index, tacacs_group, tacacs_server_list):
    tacacs_group_leftover = config_leftover.get("tailf-ned-cisco-ios:aaa", {}).get("group", {}).get("server", {}).get("tacacs-plus")[tacacs_group_index]
    # If we got here, we init an empty dict and append to oc_system_server_group list for future use.
    oc_system_server_group.append({})
    tac_group_index = len(oc_system_server_group) - 1
    set_tacacs_group_config(tacacs_group_leftover, config_leftover, oc_system_server_group, if_ip, tac_group_index, tacacs_group, tacacs_server_list)

def process_aaa_radius(oc_system_server_group, config_leftover, if_ip, radius_group_index, radius_group, radius_server_list):
    radius_group_leftover = config_leftover.get("tailf-ned-cisco-ios:aaa", {}).get("group", {}).get("server", {}).get("radius")[radius_group_index]
    # If we got here, we init an empty dict and append to oc_system_server_group list for future use.
    oc_system_server_group.append({})
    rad_group_index = len(oc_system_server_group) - 1
    set_radius_group_config(radius_group_leftover, config_leftover, oc_system_server_group, if_ip, rad_group_index, radius_group, radius_server_list)

def set_tacacs_group_config(tacacs_group_leftover, config_leftover, oc_system_server_group, if_ip, tac_group_index, tacacs_group, tacacs_server_list):
    # TACACS SERVER-GROUPS
    oc_system_server_group[tac_group_index]["openconfig-system:name"] = f'{tacacs_group.get("name")}'
    temp_tacacs_group = {"openconfig-system:config": {
        "openconfig-system:type": "TACACS",
        "openconfig-system:name": f'{tacacs_group.get("name")}'},
        "openconfig-system:servers": set_server_tacacs_config(tacacs_group_leftover, config_leftover, oc_system_server_group, if_ip, tac_group_index, tacacs_group, tacacs_server_list)
    }
    oc_system_server_group[tac_group_index].update(temp_tacacs_group)

def set_radius_group_config(radius_group_leftover, config_leftover, oc_system_server_group, if_ip, rad_group_index, radius_group, radius_server_list):
    # RADIUS SERVER-GROUPS
    oc_system_server_group[rad_group_index]["openconfig-system:name"] = f'{radius_group.get("name")}'
    # RADIUS SERVER-GROUP NAME AND TYPE
    temp_radius_group = {"openconfig-system:config": {
        "openconfig-system:type": "RADIUS",
        "openconfig-system:name": f'{radius_group.get("name")}'},
        "openconfig-system:servers": set_server_radius_config(radius_group_leftover, config_leftover, oc_system_server_group, if_ip, rad_group_index, radius_group, radius_server_list)
    }
    oc_system_server_group[rad_group_index].update(temp_radius_group)

def set_server_tacacs_config(tacacs_group_leftover, config_leftover, oc_system_server_group, if_ip, tac_group_index, tacacs_group, tacacs_server_list):
    tac_server = {"openconfig-system:server": []}
    tac_server_list = tac_server["openconfig-system:server"]
    source_interface_ip = None
    # TACACS SOURCE-INTERFACE
    for i, n in tacacs_group.get("ip", {}).get("tacacs", {}).get("source-interface", {}).items():
        source_interface = f"{i}{n}"
        source_interface_ip = if_ip.get(source_interface)
        if source_interface_ip:
            del config_leftover["tailf-ned-cisco-ios:aaa"]["group"]["server"]["tacacs-plus"][tac_group_index]["ip"]["tacacs"][
                "source-interface"]

    if tacacs_server_list:
        for server_list_index, server in enumerate(tacacs_server_list):
            for i in range(len(tacacs_group.get("server", {}).get("name", []))):
                if server.get("name") in tacacs_group["server"]["name"][i]["name"]:
                    # TACACS SERVER NAME, ADDRESS AND TIMEOUT
                    temp_tacacs_server = {"openconfig-system:address": f'{server.get("address", {}).get("ipv4")}',
                                          "openconfig-system:config": {
                                              "openconfig-system:address": f'{server.get("address", {}).get("ipv4")}',
                                              "openconfig-system:name": f'{server.get("name")}',
                                              "openconfig-system:timeout": f'{server.get("timeout", 5)}'},
                                          "openconfig-system:tacacs": {"openconfig-system:config": {
                                              "openconfig-system:port": f'{server.get("port", 49)}',
                                              "openconfig-system:secret-key": f'{server.get("key", {}).get("secret")}'
                                          }}}
                    if source_interface_ip:
                        temp_tacacs_server["openconfig-system:tacacs"]["openconfig-system:config"]["openconfig-system:source-address"] = source_interface_ip
                    tac_server_list.append(temp_tacacs_server)
                    config_leftover["tailf-ned-cisco-ios:aaa"]["group"]["server"]["tacacs-plus"][tac_group_index][
                        "server"]["name"][i] = None
            config_leftover["tailf-ned-cisco-ios:tacacs"]["server"][server_list_index] = None

    return tac_server

def set_server_radius_config(radius_group_leftover, config_leftover, oc_system_server_group, if_ip, rad_group_index,
                             radius_group, radius_server_list):
    rad_server = {"openconfig-system:server": []}
    rad_server_list = rad_server["openconfig-system:server"]
    source_interface_ip = None
    # RADIUS SOURCE-INTERFACE
    for i, n in radius_group.get("ip", {}).get("radius", {}).get("source-interface", {}).items():
        source_interface = f"{i}{n}"
        source_interface_ip = if_ip.get(source_interface)
        if source_interface_ip:
            del \
            config_leftover["tailf-ned-cisco-ios:aaa"]["group"]["server"]["radius"][rad_group_index]["ip"]["radius"][
                "source-interface"]

    if radius_server_list:
        for server_list_index, server in enumerate(radius_server_list):
            for i in range(len(radius_group.get("server", {}).get("name", []))):
                if server.get("id") in radius_group["server"]["name"][i]["name"]:
                    # RADIUS SERVER NAME, ADDRESS AND TIMEOUT
                    temp_radius_server = {
                        "openconfig-system:address": f'{server.get("address", {}).get("ipv4", {}).get("host")}',
                        "openconfig-system:config": {
                            "openconfig-system:address": f'{server.get("address", {}).get("ipv4", {}).get("host")}',
                            "openconfig-system:name": f'{server.get("id")}',
                            "openconfig-system:timeout": f'{server.get("timeout", 5)}'},
                        "openconfig-system:radius": {"openconfig-system:config": {
                            "openconfig-system:acct-port": f'{server.get("address", {}).get("ipv4", {}).get("acct-port")}',
                            "openconfig-system:auth-port": f'{server.get("address", {}).get("ipv4", {}).get("auth-port")}'
                        }}}
                    if source_interface_ip:
                        temp_radius_server["openconfig-system:radius"]["openconfig-system:config"][
                            "openconfig-system:source-address"] = source_interface_ip
                    if server.get("key", {}).get("secret"):
                        temp_radius_server["openconfig-system:radius"]["openconfig-system:config"][
                            "openconfig-system:secret-key"] = server.get("key", {}).get("secret")
                    rad_server_list.append(temp_radius_server)
                    config_leftover["tailf-ned-cisco-ios:aaa"]["group"]["server"]["radius"][rad_group_index][
                        "server"]["name"][i] = None
            config_leftover["tailf-ned-cisco-ios:radius"]["server"][server_list_index] = None

    return rad_server

def set_accounting_method(oc_system_aaa_accounting, config_leftover, accounting_dict):
    # AAA ACCOUNTING GROUPS
    acc_method = {"openconfig-system:accounting-method": []}
    acc_method_list = acc_method["openconfig-system:accounting-method"]
    group = group2 = group3 = None

    if accounting_dict.get("commands"):
        for i, command in enumerate(accounting_dict.get("commands")):
            if command.get("group"):
                if command.get("group") == 'tacacs+':
                    group = 'TACACS_ALL'
                else:
                    group = command.get("group")
                acc_method_list.append(group)
            if command.get("group2") and command.get("group2", {}).get("group"):
                if command.get("group2", {}).get("group") == 'tacacs+':
                    group2 = 'TACACS_ALL'
                elif command.get("group2", {}).get("group"):
                    group2 = command.get("group2", {}).get("group")
                acc_method_list.append(group2)
            if command.get("group3") and command.get("group3", {}).get("group"):
                if command.get("group2", {}).get("group") and command.get("group3", {}).get("group") == 'tacacs+':
                    group3 = 'TACACS_ALL'
                elif command.get("group2", {}).get("group") and command.get("group3", {}).get("group"):
                    group3 = command.get("group3", {}).get("group")
                acc_method_list.append(group3)
        del config_leftover["tailf-ned-cisco-ios:aaa"]["accounting"]["commands"]
    if accounting_dict.get("exec"):
        for i, exe in enumerate(accounting_dict.get("exec")):
            if exe.get("group"):
                if exe.get("group") == 'tacacs+':
                    group = 'TACACS_ALL'
                else:
                    group = exe.get("group")
                acc_method_list.append(group)
            if exe.get("group2") and exe.get("group2", {}).get("group"):
                if exe.get("group2", {}).get("group") == 'tacacs+':
                    group2 = 'TACACS_ALL'
                elif exe.get("group2", {}).get("group"):
                    group2 = exe.get("group2", {}).get("group")
                acc_method_list.append(group2)
            if exe.get("group3") and exe.get("group3", {}).get("group"):
                if exe.get("group2", {}).get("group") and exe.get("group3", {}).get("group") == 'tacacs+':
                    group3 = 'TACACS_ALL'
                elif exe.get("group2", {}).get("group") and exe.get("group3", {}).get("group"):
                    group3 = exe.get("group3", {}).get("group")
                acc_method_list.append(group3)
        del config_leftover["tailf-ned-cisco-ios:aaa"]["accounting"]["exec"]

    return acc_method

def set_accounting_event(oc_system_aaa_accounting, config_leftover, accounting_dict):
    acc_event = {"openconfig-system:event": []}
    acc_event_list = acc_event["openconfig-system:event"]
    # AAA ACCOUNTING EVENT-TYPE AND RECORD
    if accounting_dict.get("commands"):
        for key in accounting_dict.get("commands"):
            if key.get("level") == 15 and key.get("name") == 'default':
                event_type = 'AAA_ACCOUNTING_EVENT_COMMAND'
                if key.get("action-type") == 'stop-only':
                    action = 'STOP'
                elif key.get("action-type") == 'start-stop':
                    action = "START_STOP"
                temp_event = {"openconfig-system:event-type": f'{event_type}',
                            "openconfig-system:config": {
                                "openconfig-system:event-type": f'{event_type}',
                                "openconfig-system:record": f'{action}'
                            }}
                acc_event_list.append(temp_event)
    if accounting_dict.get("exec"):
        for key in accounting_dict.get("exec"):
            if key.get("name") == 'default':
                event_type = 'AAA_ACCOUNTING_EVENT_LOGIN'
                if key.get("action-type") == 'stop-only':
                    action = 'STOP'
                elif key.get("action-type") == 'start-stop':
                    action = "START_STOP"
                temp_event = {"openconfig-system:event-type": f'{event_type}',
                            "openconfig-system:config": {
                                "openconfig-system:event-type": f'{event_type}',
                                "openconfig-system:record": f'{action}'
                            }}
                acc_event_list.append(temp_event)

    return acc_event

def set_authorization_event(oc_system_aaa_authorization, config_leftover, authorization_dict):
    autho_event = {"openconfig-system:event": []}
    autho_event_list = autho_event["openconfig-system:event"]
    # AAA AUTHORIZATION EVENT-TYPE AND RECORD
    if authorization_dict.get("commands"):
        for key in authorization_dict.get("commands"):
            if key.get("level") == 15 and key.get("name") == 'default':
                event_type = 'AAA_AUTHORIZATION_EVENT_COMMAND'
                temp_event = {"openconfig-system:event-type": f'{event_type}',
                            "openconfig-system:config": {
                                "openconfig-system:event-type": f'{event_type}'
                            }}
                autho_event_list.append(temp_event)
        del config_leftover["tailf-ned-cisco-ios:aaa"]["authorization"]["commands"]
    if authorization_dict.get("exec"):
        for key in authorization_dict.get("exec"):
            if key.get("name") == 'default':
                event_type = 'AAA_AUTHORIZATION_EVENT_CONFIG'
                temp_event = {"openconfig-system:event-type": f'{event_type}',
                            "openconfig-system:config": {
                                "openconfig-system:event-type": f'{event_type}'
                            }}
                autho_event_list.append(temp_event)
        del config_leftover["tailf-ned-cisco-ios:aaa"]["authorization"]["exec"]

    return autho_event

def set_authorization_method(oc_system_aaa_authorization, config_leftover, authorization_dict):
    # AAA AUTHORIZATION GROUPS
    autho_method = {"openconfig-system:authorization-method": []}
    autho_method_list = autho_method["openconfig-system:authorization-method"]
    group = group2 = group3 = None

    if authorization_dict.get("commands"):
        for i, command in enumerate(authorization_dict.get("commands")):
            if command.get("tacacsplus"):
                group = 'TACACS_ALL'
            autho_method_list.append(group)
            if command.get("local"):
                group = 'LOCAL'
            autho_method_list.append(group)
            if command.get("group"):
                if command.get("group") == 'tacacs+':
                    group = 'TACACS_ALL'
                else:
                    group = command.get("group")
                autho_method_list.append(group)
            if command.get("group2") and command.get("group2", {}).get("group"):
                if command.get("group2", {}).get("group") == 'tacacs+':
                    group2 = 'TACACS_ALL'
                elif command.get("group2", {}).get("group"):
                    group2 = command.get("group2", {}).get("group")
                autho_method_list.append(group2)
            if command.get("group3") and command.get("group3", {}).get("group"):
                if command.get("group2", {}).get("group") and command.get("group3", {}).get("group") == 'tacacs+':
                    group3 = 'TACACS_ALL'
                elif command.get("group2", {}).get("group") and command.get("group3", {}).get("group"):
                    group3 = command.get("group3", {}).get("group")
                autho_method_list.append(group3)
    if authorization_dict.get("exec"):
        for i, exe in enumerate(authorization_dict.get("exec")):
            if exe.get("tacacsplus"):
                group = 'TACACS_ALL'
            autho_method_list.append(group)
            if exe.get("local"):
                group = 'LOCAL'
            autho_method_list.append(group)
            if exe.get("group"):
                if exe.get("group") == 'tacacs+':
                    group = 'TACACS_ALL'
                else:
                    group = exe.get("group")
                autho_method_list.append(group)
            if exe.get("group2") and exe.get("group2", {}).get("group"):
                if exe.get("group2", {}).get("group") == 'tacacs+':
                    group2 = 'TACACS_ALL'
                elif exe.get("group2", {}).get("group"):
                    group2 = exe.get("group2", {}).get("group")
                autho_method_list.append(group2)
            if exe.get("group3") and exe.get("group3", {}).get("group"):
                if exe.get("group2", {}).get("group") and exe.get("group3", {}).get("group") == 'tacacs+':
                    group3 = 'TACACS_ALL'
                elif exe.get("group2", {}).get("group") and exe.get("group3", {}).get("group"):
                    group3 = exe.get("group3", {}).get("group")
                autho_method_list.append(group3)
    return autho_method

def set_authentication_method(oc_system_aaa_authentication, config_leftover, authentication_dict):
    # AAA AUTHENTICATION GROUPS
    authe_method = {"openconfig-system:authentication-method": []}
    authe_method_list = authe_method["openconfig-system:authentication-method"]
    group = group2 = group3 = None

    if authentication_dict:
        if authentication_dict.get("login"):
            for i, login in enumerate(authentication_dict.get("login")):
                if login.get("local"):
                    group = 'LOCAL'
                authe_method_list.append(group)
                if login.get("tacacsplus"):
                    group = 'TACACS_ALL'
                authe_method_list.append(group)
                if login.get("group"):
                    if login.get("group") == 'tacacs+':
                        group = 'TACACS_ALL'
                    else:
                        group = login.get("group")
                    authe_method_list.append(group)
                if login.get("group2") and login.get("group2", {}).get("group"):
                    if login.get("group2", {}).get("group") == 'tacacs+':
                        group2 = 'TACACS_ALL'
                    elif login.get("group2", {}).get("group"):
                        group2 = login.get("group2", {}).get("group")
                    authe_method_list.append(group2)
                if login.get("group3") and login.get("group3", {}).get("group"):
                    if login.get("group2", {}).get("group") and login.get("group3", {}).get("group") == 'tacacs+':
                        group3 = 'TACACS_ALL'
                    elif login.get("group2", {}).get("group") and login.get("group3", {}).get("group"):
                        group3 = login.get("group3", {}).get("group")
                    authe_method_list.append(group3)
            del config_leftover["tailf-ned-cisco-ios:aaa"]["authentication"]["login"]

    return authe_method

def set_authentication_admin(oc_system_aaa_authentication, config_leftover, authentication_user_list):
    authe_admin = {"openconfig-system:config": {}}
    authe_admin_dict = authe_admin["openconfig-system:config"]
    pwd = pwd_hashed = ssh_key = None
    temp_user = {}
    # AAA AUTHENTICATION ADMIN-USER
    if authentication_user_list:
        for i, user in enumerate(authentication_user_list):
            if "admin" in user.get("name"):
                pwd_hashed = user.get("secret", {}).get("secret")
                temp_user = {"openconfig-system:admin-password": 'admin',
                                "openconfig-system:admin-password-hashed": f'{pwd_hashed}'
                            }
                config_leftover["tailf-ned-cisco-ios:username"][i] = None
        authe_admin_dict.update(temp_user)
    return authe_admin

def set_authentication_user(oc_system_aaa_authentication, config_leftover, authentication_user_list):
    authe_user = {"openconfig-system:user": []}
    authe_user_list = authe_user["openconfig-system:user"]
    pwd = pwd_hashed = ssh_key = None
    # AAA AUTHENTICATION USERS
    if authentication_user_list:
        for i, user in enumerate(authentication_user_list):
            if "admin" not in user.get("name"):
                role = 'SYSTEM_ROLE_ADMIN'
                pwd = user.get("secret", {}).get("secret")
                temp_user = {"openconfig-system:username": f'{user.get("name")}',
                            "openconfig-system:config": {
                                "openconfig-system:username": f'{user.get("name")}',
                                "openconfig-system:password": f'{pwd}',
                                "openconfig-system:password-hashed": f'{pwd_hashed}', # TODO
                                "openconfig-system:role": f'{role}',
                                "openconfig-system:ssh-key:": f'{ssh_key}' # TODO
                            }}
                authe_user_list.append(temp_user)
                config_leftover["tailf-ned-cisco-ios:username"][i] = None

    return authe_user

def cleanup_server_access(config_leftover, group_access_type, access_type):
    if len(config_leftover.get("tailf-ned-cisco-ios:aaa", {}).get("group", {}).get("server", {}).get(group_access_type, [])) < 1:
        return

    updated_server_list = []

    for group_access_type_server in config_leftover["tailf-ned-cisco-ios:aaa"]["group"]["server"][group_access_type]:
        updated_server_names = []

        for name in group_access_type_server.get("server", {}).get("name", []):
            if name and name.get("name"):
                updated_server_names.append(name)

        if len(updated_server_names) > 0:
            group_access_type_server["server"]["name"] = updated_server_names
        elif "name" in group_access_type_server.get("server", {}):
            del group_access_type_server["server"]["name"]

    for server in config_leftover.get(f"tailf-ned-cisco-ios:{access_type}", {}).get("server", []):
        if server and len(server) > 0:
            updated_server_list.append(server)

    if len(updated_server_list) > 0:
        config_leftover[f"tailf-ned-cisco-ios:{access_type}"]["server"] = updated_server_list
    elif "server" in config_leftover.get(f"tailf-ned-cisco-ios:{access_type}", {}):
        del config_leftover[f"tailf-ned-cisco-ios:{access_type}"]["server"]

def main(before: dict, leftover: dict, if_ip: dict, translation_notes: list = []) -> dict:
    """
    Translates NSO Device configurations to MDD OpenConfig configurations.

    Requires environment variables:
    NSO_URL: str
    NSO_USERNAME: str
    NSO_PASSWORD: str
    NSO_DEVICE: str
    TEST - If True, sends generated OC configuration to NSO Server: str

    :param before: Original NSO Device configuration: dict
    :param leftover: NSO Device configuration minus configs replaced with MDD OC: dict
    :param if_ip: Map of interface names to IP addresses: dict
    :return: MDD Openconfig System configuration: dict
    """
    xe_system_config(before, leftover)
    xe_system_services(before, leftover)
    xe_system_ssh_server(before, leftover)
    xe_system_ntp(before, leftover, if_ip)
    # xe_system_aaa(before, leftover, if_ip)
    translation_notes += system_notes

    return openconfig_system


if __name__ == "__main__":
    sys.path.append("../../")
    sys.path.append("../../../")

    if find_spec("package_nso_to_oc") is not None:
        from package_nso_to_oc.xe import common_xe
        from package_nso_to_oc import common
    else:
        import common_xe
        import common

    (config_before_dict, config_leftover_dict, interface_ip_dict) = common_xe.init_xe_configs()
    main(config_before_dict, config_leftover_dict, interface_ip_dict)
    config_name = "_system"
    config_remaining_name = "_remaining_system"
    oc_name = "_openconfig_system"
    common.print_and_test_configs("xe1", config_before_dict, config_leftover_dict, openconfig_system, 
        config_name, config_remaining_name, oc_name, system_notes)
else:
    # This is needed for now due to top level __init__.py.
    # We need to determine if contents in __init__.py is still necessary.
    if find_spec("package_nso_to_oc") is not None:
        from package_nso_to_oc.xe import common_xe
        from package_nso_to_oc import common
    else:
        from xe import common_xe
        import common
