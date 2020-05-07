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


device = {
    "id": "{}-{}".format(EnvVars.ModuleID.value, dc_conf.Devices.sensor_actuator_id),
    "name": "Sir Test Dyson",
    "device_type": dc_conf.DeviceTypes.sensor_actuator,
    "services": (
        "getDeviceState",
        "getSensorReadings",
        "setMonitoring",
        "setPower",
        "setOscillation"
    )
}
