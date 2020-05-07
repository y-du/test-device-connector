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


from ..logger import getLogger
from ..configuration import dc_conf, EnvVars
import datetime
import time
import random
import threading


logger = getLogger(__name__.split(".", 1)[-1])


block = threading.Event()


state = {
    "power": False,
    "oscillation": False,
    "speed": 1,
    "monitoring": False,
    "filter_life": 100
}


def setMonitoring(monitoring: bool):
    state["monitoring"] = monitoring
    if state["monitoring"]:
        if not block.is_set():
            block.set()
        logger.info("Monitoring On")
    else:
        if block.is_set():
            block.clear()
        logger.info("Monitoring Off")
    return {"status": 0}


def setSpeed(speed: int):
    state["speed"] = "{:04d}".format(speed)
    logger.info("Speed {}".format(state["speed"]))
    return {"status": 0}


def setOscillation(oscillation: bool):
    state["oscillation"] = oscillation
    if state["oscillation"]:
        logger.info("Oscillation On")
    else:
        logger.info("Oscillation Off")
    return {"status": 0}


def setPower(power: bool):
    state["power"] = power
    if state["power"]:
        logger.info("Power On")
    else:
        logger.info("Power Off")
    return {"status": 0}


def getDeviceState():
    st = state.copy()
    st["status"] = 0
    st["time"] = "{}Z".format(datetime.datetime.utcnow().isoformat())
    return st


def getSensorReadings():
    block.wait()
    msg = {
        "tact": random.uniform(298.15, 300.15),
        "hact": random.randrange(49, 51),
        "pact": random.randrange(0, 5),
        "vact": random.randrange(0, 3),
        "time": "{}Z".format(datetime.datetime.utcnow().isoformat())
    }
    time.sleep(dc_conf.Sensor.delay)
    return msg


device = {
    "id": "{}-{}".format(EnvVars.ModuleID.value, dc_conf.Devices.sensor_actuator_id),
    "name": dc_conf.Devices.sensor_actuator_name,
    "device_type": dc_conf.DeviceTypes.sensor_actuator,
    "services": {
        "getDeviceState": getDeviceState,
        "getSensorReadings": getSensorReadings,
        "setMonitoring": setMonitoring,
        "setPower": setPower,
        "setOscillation": setOscillation,
        "setSpeed": setSpeed
    }
}
