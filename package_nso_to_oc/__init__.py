"""
Translate NSO Device config to MDD OpenConfig

This package provides the tools to pull a device's configuration from an NSO server and
convert the NED structured configuration to MDD OpenConfig.

The package requires the following environment variables:
NSO_URL - URL for the NSO server
NSO_USERNAME
NSO_PASSWORD
NSO_DEVICE - NSO device name for configuration translation

Example of generating MDD OpenConfig System

import package_nso_to_oc
openconfig_json = package_nso_to_oc.xe.xe_system.main(package_nso_to_oc.config_before_dict,
                                                      package_nso_to_oc.configs_leftover,
                                                      package_nso_to_oc.interface_ip_name_dict)
print(openconfig_json)
"""
