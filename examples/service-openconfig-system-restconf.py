#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json

import requests
from requests.auth import HTTPBasicAuth


url = "http://X.X.X.X:8080/restconf/data/oc-system-nso:oc-system-nso"

payload = {
    "oc-system-nso:oc-system-nso": [
        {"name": "hq-rtr1",
         "device": "hq-rtr1",
         "openconfig-system": {
             "system": {
                 "config": {
                     "hostname": "hq-rtr1",
                     "domain-name": "cisco.com",
                     "login-banner": "This is line 1.\nThis is line 2.\nThis is the last line.",
                     "motd-banner": "This is line 1.\nThis is line 2.\nThis is the last line."
                 }
             }
         }
         }
    ]
}

headers = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json"
}

response = requests.request("PATCH", url, data=json.dumps(payload), headers=headers,
                            auth=HTTPBasicAuth('admin', 'xxx'))

print(response.status_code)
