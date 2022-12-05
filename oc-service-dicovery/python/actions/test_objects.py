device_config = """
<config xmlns="http://tail-f.com/ns/config/1.0">
  <devices xmlns="http://tail-f.com/ns/ncs">
    <device>
      <name>ios</name>
      <config>
        <tailfned xmlns="urn:ios">
          <police>cirmode</police>
        </tailfned>
        <aaa xmlns="urn:ios">
          <accounting>
            <delay-start/>
          </accounting>
        </aaa>
        <ip xmlns="urn:ios">
          <source-route>true</source-route>
          <gratuitous-arps-conf>
            <gratuitous-arps>false</gratuitous-arps>
          </gratuitous-arps-conf>
          <finger/>
          <http>
            <server>false</server>
            <secure-server>false</secure-server>
          </http>
        </ip>
        <interface xmlns="urn:ios">
          <Loopback>
            <name>0</name>
            <description>Interface Loopback0</description>
            <ip>
              <address>
                <primary>
                  <address>127.0.0.1</address>
                  <mask>255.0.0.0</mask>
                </primary>
              </address>
            </ip>
          </Loopback>
          <Ethernet>
            <name>0/0/0</name>
            <ip>
              <no-address>
                <address>false</address>
              </no-address>
            </ip>
          </Ethernet>
          <FastEthernet>
            <name>0</name>
            <description>Interface FastEthernet0</description>
            <ip>
              <no-address>
                <address>false</address>
              </no-address>
            </ip>
          </FastEthernet>
          <FastEthernet>
            <name>0/0</name>
            <description>Interface FastEthernet0/0</description>
            <ip>
              <no-address>
                <address>false</address>
              </no-address>
            </ip>
          </FastEthernet>
          <FastEthernet>
            <name>1/0</name>
            <ip>
              <no-address>
                <address>false</address>
              </no-address>
            </ip>
          </FastEthernet>
          <FastEthernet>
            <name>1/1</name>
            <description>Interface FastEthernet1/1</description>
            <ip>
              <no-address>
                <address>false</address>
              </no-address>
            </ip>
          </FastEthernet>
          <GigabitEthernet>
            <name>0</name>
            <ip>
              <no-address>
                <address>false</address>
              </no-address>
            </ip>
          </GigabitEthernet>
          <GigabitEthernet>
            <name>0/0</name>
            <ip>
              <no-address>
                <address>false</address>
              </no-address>
            </ip>
          </GigabitEthernet>
          <GigabitEthernet>
            <name>0/0.100</name>
            <description>Interface GigabitEthernet0/0.100</description>
            <encapsulation>
              <dot1Q>
                <vlan-id>100</vlan-id>
              </dot1Q>
            </encapsulation>
            <ip>
              <address>
                <primary>
                  <address>10.20.30.33</address>
                  <mask>255.255.255.0</mask>
                </primary>
              </address>
            </ip>
            <service-policy>
              <output>ford</output>
            </service-policy>
          </GigabitEthernet>
          <GigabitEthernet>
            <name>0/1</name>
            <ip>
              <no-address>
                <address>false</address>
              </no-address>
            </ip>
          </GigabitEthernet>
          <GigabitEthernet>
            <name>1/1.101</name>
            <description>Interface GigabitEthernet1/1.101</description>
            <encapsulation>
              <dot1Q>
                <vlan-id>101</vlan-id>
              </dot1Q>
            </encapsulation>
            <ip>
              <address>
                <primary>
                  <address>10.20.40.40</address>
                  <mask>255.255.255.0</mask>
                </primary>
              </address>
            </ip>
            <service-policy>
              <output>volvo</output>
            </service-policy>
          </GigabitEthernet>
        </interface>
      </config>
    </device>
  </devices>
</config>
"""

oc_interfaces = '''{
  "mdd:openconfig": {
    "openconfig-interfaces:interfaces": {
      "openconfig-interfaces:interface": [
        {
          "openconfig-interfaces:name": "Loopback0",
          "openconfig-interfaces:config": {
            "openconfig-interfaces:name": "Loopback0",
            "openconfig-interfaces:type": "softwareLoopback"
          },
          "openconfig-interfaces:subinterfaces": {
            "openconfig-interfaces:subinterface": [
              {
                "openconfig-interfaces:index": 0,
                "openconfig-interfaces:config": {
                  "openconfig-interfaces:index": 0,
                  "openconfig-interfaces:description": "Test",
                  "openconfig-interfaces:enabled": true
                },
                "openconfig-if-ip:ipv4": {
                  "openconfig-if-ip:addresses": {
                    "openconfig-if-ip:address": [
                      {
                        "openconfig-if-ip:ip": "10.10.10.20",
                        "openconfig-if-ip:config": {
                          "openconfig-if-ip:ip": "10.10.10.20",
                          "openconfig-if-ip:prefix-length": 32
                        }
                      }
                    ]
                  },
                  "openconfig-if-ip:config": {
                    "openconfig-if-ip:dhcp-client": false
                  }
                }
              }
            ]
          }
        },
        {
          "openconfig-interfaces:name": "Ethernet0/0/0",
          "openconfig-interfaces:config": {
            "openconfig-interfaces:name": "Ethernet0/0/0",
            "openconfig-interfaces:type": "ethernetCsmacd",
            "openconfig-interfaces:enabled": true
          },
          "openconfig-interfaces:subinterfaces": {
            "openconfig-interfaces:subinterface": [
              {
                "openconfig-interfaces:index": 0,
                "openconfig-interfaces:config": {
                  "openconfig-interfaces:index": 0,
                  "openconfig-interfaces:enabled": true
                }
              }
            ]
          },
          "openconfig-if-ethernet:ethernet": {
            "openconfig-if-ethernet:config": {}
          }
        },
        {
          "openconfig-interfaces:name": "FastEthernet0",
          "openconfig-interfaces:config": {
            "openconfig-interfaces:name": "FastEthernet0",
            "openconfig-interfaces:type": "ethernetCsmacd",
            "openconfig-interfaces:enabled": true
          },
          "openconfig-interfaces:subinterfaces": {
            "openconfig-interfaces:subinterface": [
              {
                "openconfig-interfaces:index": 0,
                "openconfig-interfaces:config": {
                  "openconfig-interfaces:index": 0,
                  "openconfig-interfaces:enabled": true
                }
              }
            ]
          },
          "openconfig-if-ethernet:ethernet": {
            "openconfig-if-ethernet:config": {}
          }
        },
        {
          "openconfig-interfaces:name": "FastEthernet0/0",
          "openconfig-interfaces:config": {
            "openconfig-interfaces:name": "FastEthernet0/0",
            "openconfig-interfaces:type": "ethernetCsmacd",
            "openconfig-interfaces:enabled": true
          },
          "openconfig-interfaces:subinterfaces": {
            "openconfig-interfaces:subinterface": [
              {
                "openconfig-interfaces:index": 0,
                "openconfig-interfaces:config": {
                  "openconfig-interfaces:index": 0,
                  "openconfig-interfaces:enabled": true
                }
              }
            ]
          },
          "openconfig-if-ethernet:ethernet": {
            "openconfig-if-ethernet:config": {}
          }
        },
        {
          "openconfig-interfaces:name": "FastEthernet1/0",
          "openconfig-interfaces:config": {
            "openconfig-interfaces:name": "FastEthernet1/0",
            "openconfig-interfaces:type": "ethernetCsmacd",
            "openconfig-interfaces:enabled": true
          },
          "openconfig-interfaces:subinterfaces": {
            "openconfig-interfaces:subinterface": [
              {
                "openconfig-interfaces:index": 0,
                "openconfig-interfaces:config": {
                  "openconfig-interfaces:index": 0,
                  "openconfig-interfaces:enabled": true
                }
              }
            ]
          },
          "openconfig-if-ethernet:ethernet": {
            "openconfig-if-ethernet:config": {}
          }
        },
        {
          "openconfig-interfaces:name": "FastEthernet1/1",
          "openconfig-interfaces:config": {
            "openconfig-interfaces:name": "FastEthernet1/1",
            "openconfig-interfaces:type": "ethernetCsmacd",
            "openconfig-interfaces:enabled": true
          },
          "openconfig-interfaces:subinterfaces": {
            "openconfig-interfaces:subinterface": [
              {
                "openconfig-interfaces:index": 0,
                "openconfig-interfaces:config": {
                  "openconfig-interfaces:index": 0,
                  "openconfig-interfaces:enabled": true
                }
              }
            ]
          },
          "openconfig-if-ethernet:ethernet": {
            "openconfig-if-ethernet:config": {}
          }
        },
        {
          "openconfig-interfaces:name": "GigabitEthernet0",
          "openconfig-interfaces:config": {
            "openconfig-interfaces:name": "GigabitEthernet0",
            "openconfig-interfaces:type": "ethernetCsmacd",
            "openconfig-interfaces:enabled": true
          },
          "openconfig-interfaces:subinterfaces": {
            "openconfig-interfaces:subinterface": [
              {
                "openconfig-interfaces:index": 0,
                "openconfig-interfaces:config": {
                  "openconfig-interfaces:index": 0,
                  "openconfig-interfaces:enabled": true
                }
              }
            ]
          },
          "openconfig-if-ethernet:ethernet": {
            "openconfig-if-ethernet:config": {}
          }
        },
        {
          "openconfig-interfaces:name": "GigabitEthernet0/0",
          "openconfig-interfaces:config": {
            "openconfig-interfaces:name": "GigabitEthernet0/0",
            "openconfig-interfaces:type": "ethernetCsmacd",
            "openconfig-interfaces:enabled": true
          },
          "openconfig-interfaces:subinterfaces": {
            "openconfig-interfaces:subinterface": [
              {
                "openconfig-interfaces:index": 0,
                "openconfig-interfaces:config": {
                  "openconfig-interfaces:index": 0,
                  "openconfig-interfaces:enabled": true
                }
              }
            ]
          },
          "openconfig-if-ethernet:ethernet": {
            "openconfig-if-ethernet:config": {}
          }
        },
        {
          "openconfig-interfaces:name": "GigabitEthernet0/1",
          "openconfig-interfaces:config": {
            "openconfig-interfaces:name": "GigabitEthernet0/1",
            "openconfig-interfaces:type": "ethernetCsmacd",
            "openconfig-interfaces:enabled": true
          },
          "openconfig-interfaces:subinterfaces": {
            "openconfig-interfaces:subinterface": [
              {
                "openconfig-interfaces:index": 0,
                "openconfig-interfaces:config": {
                  "openconfig-interfaces:index": 0,
                  "openconfig-interfaces:enabled": true
                }
              }
            ]
          },
          "openconfig-if-ethernet:ethernet": {
            "openconfig-if-ethernet:config": {}
          }
        }
      ]
    }
  }
}
'''

oc_system = '''{
  "mdd:openconfig": {
    "openconfig-system:system": {
      "openconfig-system:aaa": {},
      "openconfig-system:clock": {},
      "openconfig-system:config": {
        "openconfig-system:hostname": "Router"
      },
      "openconfig-system:dns": {},
      "openconfig-system:logging": {},
      "openconfig-system:ntp": {
        "openconfig-system:config": {},
        "openconfig-system:ntp-keys": {
          "openconfig-system:ntp-key": []
        },
        "openconfig-system:servers": {
          "openconfig-system:server": []
        }
      },
      "openconfig-system:ssh-server": {
        "openconfig-system:config": {
          "openconfig-system:protocol-version": "V2"
        }
      },
      "openconfig-system-ext:services": {
        "openconfig-system-ext:http": {
          "openconfig-system-ext:config": {
            "openconfig-system-ext:http-enabled": true
          }
        },
        "openconfig-system-ext:config": {
          "openconfig-system-ext:ip-domain-lookup": true,
          "openconfig-system-ext:archive-logging": false,
                      "openconfig-system-ext:boot-network": "DISABLED",
          "openconfig-system-ext:ip-bootp-server": true,
          "openconfig-system-ext:ip-dns-server": false,
          "openconfig-system-ext:ip-identd": false,
          "openconfig-system-ext:ip-rcmd-rcp-enable": false,
          "openconfig-system-ext:ip-rcmd-rsh-enable": false,
          "openconfig-system-ext:finger": false,
          "openconfig-system-ext:service-config": false,
          "openconfig-system-ext:service-tcp-small-servers": false,
          "openconfig-system-ext:service-udp-small-servers": false,
          "openconfig-system-ext:service-pad": false,
          "openconfig-system-ext:service-password-encryption": false
        },
        "openconfig-system-ext:login-security-policy": {
          "openconfig-system-ext:config": {
            "openconfig-system-ext:on-success": true,
            "openconfig-system-ext:on-failure": false
          },
          "openconfig-system-ext:block-for": {
            "openconfig-system-ext:config": {}
          }
        }
      }
    }
  }
}
'''

dry_run_param = '''{"input":{"dry-run":{"outformat":"native"}}}'''
reconcile_param = '''{"input":{"reconcile":{"keep-non-service-config":null}}}'''
reconcile_discard_param = '''{"input":{"reconcile":{"discard-non-service-config":null}}}'''


if __name__ == '__main__':
    import ncs
    import _ncs

    import json
    from utilities import json_to_str

    device_name = 'xe-65'
    oc_service_json = json.loads(oc_system)
    service_config = {"tailf-ncs:devices": {"device": [{"name": device_name}]}}
    service_config["tailf-ncs:devices"]["device"][0].update(oc_service_json)

    with ncs.maapi.Maapi() as m:
        with ncs.maapi.Session(m, 'admin', 'system'):
            with m.start_write_trans() as t:
                _ncs.maapi.load_config_cmds(m.msock, t.th,
                                       (_ncs.maapi.CONFIG_JSON +
                                        _ncs.maapi.CONFIG_UNHIDE_ALL +
                                        _ncs.maapi.CONFIG_MERGE),
                                       json_to_str(service_config), '/')
                cp = ncs.maapi.CommitParams()
                cp.dry_run_cli()
                cp.set_dry_run_outformat(ncs.maapi.DryRunOutformat.CLI)
                r = t.apply_params(False, cp)
                if 'local-node' in r:
                    print(r['local-node'])
                else:
                    print(r)
