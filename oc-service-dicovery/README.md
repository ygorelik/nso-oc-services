# Openconfig Service Discovery

## Overview

The Openconfig Service Discovery is the NSO package, which extends capabilities of NSO Openconfig Services (NOS)
package. It allows discovering and reconciling of openconfig services supported by NOS in NSO managed devices. 
It relies on capabilities of translators included into NOS _package_nso_to_oc_ directory. 

### Limitations

The service discovery capabilities are limited by the _package_nso_to_oc_ translators, which can be extended in the future.
Supported NEDs and services:
  - cisco-ios-cli: interfaces and vlans, system, acl, network-instances, stp
  - cisco-iosxr-cli: system, interfaces and vlans 
