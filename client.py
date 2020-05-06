"""
   Copyright 2020 Yann Dumont

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

from dc.logger import initLogger
from dc.configuration import dc_conf, EnvVars
from dc.mqtt_client import Client
import json
import time
import queue
import threading
import random
import datetime


initLogger(dc_conf.Logger.level)


def printer(d_id, msg):
    print("'{}' says: {}".format(d_id, msg))


def reader(client: Client, d_id, s_id):
    while True:
        time.sleep(5)
        msg = {
            "temperature": random.uniform(24.0, 25.0),
            "timestamp": '{}Z'.format(datetime.datetime.utcnow().isoformat())
        }
        client.publish("{}/{}/{}".format(dc_conf.Client.event_topic, d_id, s_id), json.dumps(msg), 1)

devices = {
    "{}-23434fgd".format(EnvVars.ModuleID.value): {
        "name": "Sensor",
        "device_type": "sensor",
        "services": {
            "read": reader
        }
    },
    "{}-4565j89d".format(EnvVars.ModuleID.value): {
        "name": "Actuator",
        "device_type": "actuator",
        "services": {
            "print": printer
        }
    },
    "{}-8ojm564h".format(EnvVars.ModuleID.value): {
        "name": "Sensor Actuator",
        "device_type": "sensor-actuator",
        "services": {
            "read": reader,
            "print": printer
        }
    }
}


class DeviceState:
    online = "online"
    offline = "offline"


class Method:
    set = "set"
    delete = "delete"


commands = queue.Queue()


def setDevice(client: Client, device_id: str, data: dict, method: str, state=None):
    msg = {
        "method": method,
        "device_id": device_id,
        "data": {
            "name": data["name"],
            "state": state,
            "device_type": data["device_type"]
        }
    }
    client.publish("{}/{}".format(dc_conf.Client.device_topic, EnvVars.ModuleID.value), json.dumps(msg), 2)


def subDevice(client: Client, device_id: str):
    client.subscribe("{}/{}/+".format(dc_conf.Client.command_topic, device_id), 0)


def onConnect(client):
    for key, device in devices.items():
        setDevice(client, key, device, Method.set, DeviceState.online)
        subDevice(client, key)


def onDisconnect():
    pass


def onMessage(topic, payload):
    topic = topic.split("/")
    msg = {
        "device_id": topic[1],
        "service_id": topic[2],
        "data": payload.decode()
    }
    commands.put(msg)


client = Client(client_id=EnvVars.ModuleID.value, clean_session=dc_conf.Client.clean_session)
client.connectClbk = onConnect
client.disconnectClbk = onDisconnect
client.messageClbk = onMessage

client.start()

for key, device in devices.items():
    if "sensor" in device["device_type"]:
        sensor = threading.Thread(name="sensor-{}".format(key), target=reader, args=(client, key, "read"), daemon=True)
        sensor.start()

while True:
    msg = commands.get()
    try:
        devices[msg["device_id"]]["services"][msg["service_id"]](msg["device_id"], msg["data"])
    except KeyError as ex:
        print("service {} not found for '{}'".format(ex, msg["device_id"]))
