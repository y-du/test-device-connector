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

__all__ = ("dc_conf", "EnvVars")


import simple_env_var
import os


@simple_env_var.configuration
class TDCConf:

    @simple_env_var.section
    class MB:
        host = "message-broker"
        port = 1883

    @simple_env_var.section
    class Logger:
        level = "info"
        mqtt_level = "info"

    @simple_env_var.section
    class Client:
        clean_session = False
        device_topic = "device"
        lw_topic = "lw"
        event_topic = "event"
        command_topic = "command"
        response_topic = "response"
        keep_alive = 10

    @simple_env_var.section
    class Sensor:
        delay = 10

    @simple_env_var.section
    class DeviceTypes:
        actuator = None
        sensor = None
        sensor_actuator = None

    @simple_env_var.section
    class Devices:
        actuator_id = None
        actuator_name = None
        sensor_id = None
        sensor_name = None
        sensor_actuator_id = None
        sensor_actuator_name = None


dc_conf = TDCConf()


class EnvVars:

    class GatewayLocalIP:
        name = "GATEWAY_LOCAL_IP"
        value = os.getenv("GATEWAY_LOCAL_IP")

    class ModuleID:
        name = "MODULE_ID"
        value = os.getenv("MODULE_ID")
