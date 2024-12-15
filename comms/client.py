import logging

from quanta_client.api.default_api import DefaultApi
from quanta_client.exceptions import ApiException
from quanta_client.models.device import Device
from quanta_client.models.metric import Metric
from quanta_client.models.message import Message

from state.state import AgentState

logger = logging.getLogger(__name__)


class Client(object):
    def __init__(self, api: DefaultApi):
        logger.info("Initializing client")
        self.api = api

        self.state = AgentState()

        self.heater_id = self.state.get('heater_id')
        self.temperature_id = self.state.get('temperature_id')
        self.uptime_id = self.state.get('uptime_id')

        if not self.heater_id or not self.temperature_id or not self.uptime_id:
            logger.info("State data insufficient, registering to server")
            self.heater_id, self.temperature_id, self.uptime_id = self.register_to_server()
            self.state.set('heater_id', self.heater_id)
            self.state.set('temperature_id', self.temperature_id)
            self.state.set('uptime_id', self.uptime_id)

    def register_to_server(self):
        # Register the device and metrics
        try:
            device = self.api.device_create(Device(description="ESP32 Heater"))
            logger.info(f"Device created: {device}")

            if device.id is None:
                logger.error("Device ID is None")
                exit(1)

            heater_id = device.id

            temperature = self.api.metric_create(Metric(name="Temperature", data_type="float"))

            if temperature.id is None:
                logger.error("Temperature ID is None")
                exit(1)

            temperature_id = temperature.id

            uptime = self.api.metric_create(Metric(name="Uptime", data_type="float"))

            if uptime.id is None:
                logger.error("Uptime ID is None")
                exit(1)

            uptime_id = uptime.id
            
            return heater_id, temperature_id, uptime_id
        except ApiException as e:
            logger.error(f"Exception when calling DefaultApi->device_create: {e}")
            exit(1)

    def get_heater_commands_from_server(self):
        return self.api.command_get_by_device_id(self.heater_id)

    def send_temperature_to_server(self, temperature, timestamp):
        try:
            logger.info(f"Sending temperature: {temperature} at {timestamp}")
            temperature_message = Message(device_id=self.heater_id, metric_id=self.temperature_id, metric_value=str(temperature), timestamp=timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'))
            self.api.message_create(temperature_message)
        except ApiException as e:
            logger.error(f"Exception when calling DefaultApi->message_create: {e}")

    def send_uptime_to_server(self, uptime, timestamp):
        try:
            logger.info(f"Sending uptime: {uptime} at {timestamp}")
            uptime_message = Message(device_id=self.heater_id, metric_id=self.uptime_id, metric_value=str(uptime), timestamp=timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'))
            self.api.message_create(uptime_message)
        except ApiException as e:
            logger.error(f"Exception when calling DefaultApi->message_create: {e}")
