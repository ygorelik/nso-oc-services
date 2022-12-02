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

import ncs
import _ncs
import socket

import json


def get_device_ned_id(device):
    ned_id = ncs.application.get_ned_id(device)
    if ':' in ned_id:
        ned_id = ned_id.split(':')[0]
    pos = ned_id.rfind('-')
    if pos:
        ned_id = ned_id[:pos]
    return ned_id


# ---------------------------------------------------------
# Getting device running config
# ---------------------------------------------------------
def recv_all_and_close(c_sock):
    data = ''
    while True:
        buf = c_sock.recv(4096)
        if buf:
            data += buf.decode('utf-8')
        else:
            c_sock.close()
            return data


def read_config(m, th, path, dev_flag):
    dev_flags = (_ncs.maapi.CONFIG_CDB_ONLY +
                 _ncs.maapi.CONFIG_UNHIDE_ALL +
                 dev_flag)
    c_id = _ncs.maapi.save_config(m.msock, th, dev_flags, path)
    c_sock = socket.socket()
    (ncsip, ncsport) = m.msock.getpeername()
    _ncs.stream_connect(c_sock, c_id, 0, ncsip, ncsport)
    data = recv_all_and_close(c_sock)
    return data


def get_device_config(device_name):
    with ncs.maapi.Maapi() as m:
        with ncs.maapi.Session(m, 'admin', 'system'):
            with m.start_read_trans() as t:
                root = ncs.maagic.get_root(t)
                device = root.devices.device[device_name]
                dev_flag = _ncs.maapi.CONFIG_JSON
                dev_config = read_config(m, t.th, device.config._path, dev_flag)
                return json.loads(dev_config)['data']


def json_to_str(j: json) -> str:
    return json.dumps(j, indent=2)
