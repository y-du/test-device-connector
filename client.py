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

from dc.logger import initLogger, getLogger
from dc.configuration import dc_conf, EnvVars
from dc.mqtt_client import Client
from dc.devices import smart_meter
from dc.devices import smart_plug
import json
import queue
import threading
import sys
import signal


initLogger(dc_conf.Logger.level)


logger = getLogger("client")


def sigtermHandler(_signo, _stack_frame):
    logger.warning("got SIGTERM - exiting ...")
    sys.exit(0)


class DeviceState:
    online = "online"
    offline = "offline"


class Method:
    set = "set"
    delete = "delete"


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


devices = dict()


def addToDevices(devices: dict, device: dict):
    devices[device["id"]] = {
        "name": device["name"],
        "device_type": device["device_type"],
        "services": device["services"]
    }


if dc_conf.Devices.sensor_id:
    addToDevices(devices, smart_meter.device)


if dc_conf.Devices.actuator_id:
    addToDevices(devices, smart_plug.device)


def onConnect(client):
    for key, device in devices.items():
        setDevice(client, key, device, Method.set, DeviceState.online)
        subDevice(client, key)


def onDisconnect():
    pass


commands = queue.Queue()


def onMessage(topic, payload):
    topic = topic.split("/")
    msg = {
        "device_id": topic[1],
        "service_id": topic[2],
        "cmd": json.loads(payload)
    }
    commands.put(msg)


def sender(client: Client, device_id, srv_id, func):
    while True:
        data = func()
        client.publish("{}/{}/{}".format(dc_conf.Client.event_topic, device_id, srv_id), json.dumps(data), 1)


client = Client(client_id=EnvVars.ModuleID.value, clean_session=dc_conf.Client.clean_session)
client.connectClbk = onConnect
client.disconnectClbk = onDisconnect
client.messageClbk = onMessage


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, sigtermHandler)
    client.start()
    if dc_conf.Devices.sensor_id:
        thread = threading.Thread(
            name=smart_meter.device["id"],
            target=sender,
            args=(
            client, smart_meter.device["id"], "getMeasurements", smart_meter.device["services"]["getMeasurements"]),
            daemon=True
        )
        thread.start()
    try:
        while True:
            msg = commands.get()
            try:
                if msg["cmd"]["data"]:
                    resp = devices[msg["device_id"]]["services"][msg["service_id"]](**json.loads(msg["cmd"]["data"]))
                else:
                    resp = devices[msg["device_id"]]["services"][msg["service_id"]]()
                msg["cmd"]["data"] = json.dumps(resp)
                client.publish("{}/{}/{}".format(dc_conf.Client.response_topic, msg["device_id"], msg["service_id"]), json.dumps(msg["cmd"]), 1)
            except KeyError as ex:
                logger.error("service {} not found for '{}'".format(ex, msg["device_id"]))
            except Exception as ex:
                logger.error("error handling command - {}".format(ex))
    finally:
        pass
