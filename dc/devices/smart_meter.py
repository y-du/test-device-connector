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


from ..configuration import dc_conf, EnvVars
import datetime
import random
import time


def getMeasurements():
    current_time = time.time()
    diff = random.uniform(1, dc_conf.Sensor.delay / 2)
    obis_1_8_0 = current_time - diff
    obis_16_7 = 1000 * diff / 24
    msg = {
        "OBIS_1_8_0": {
            "value": obis_1_8_0,
            "unit": "kWh"
        },
        "OBIS_16_7": {
            "value": obis_16_7,
            "unit": "W"
        },
        "time": "{}Z".format(datetime.datetime.utcnow().isoformat())
    }
    time.sleep(dc_conf.Sensor.delay)
    return msg


device = {
    "id": "{}-{}".format(EnvVars.ModuleID.value, dc_conf.Devices.sensor_id),
    "name": dc_conf.Devices.sensor_name,
    "device_type": dc_conf.DeviceTypes.sensor,
    "services": {
        "getMeasurements": getMeasurements
    }
}
