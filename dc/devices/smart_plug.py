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


logger = getLogger(__name__.split(".", 1)[-1])


plug_state = False


def getStatus():
    return {
        "status": 0,
        "on": plug_state,
        "time": "{}Z".format(datetime.datetime.utcnow().isoformat())
    }


def setPower(power):
    global plug_state
    plug_state = power
    if plug_state:
        logger.info("Power On")
    else:
        logger.info("Power Off")
    return {"status": 0}


device = {
    "id": "{}-{}".format(EnvVars.ModuleID.value, dc_conf.Devices.actuator_id),
    "name": dc_conf.Devices.actuator_name,
    "device_type": dc_conf.DeviceTypes.actuator,
    "services": {
        "getStatus": getStatus,
        "setPower": setPower
    }
}
