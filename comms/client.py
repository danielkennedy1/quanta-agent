from datetime import datetime
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
            self.heater_id, self.temperature_id, self.uptime_id = self.register_heater()
            self.state.set('heater_id', self.heater_id)
            self.state.set('temperature_id', self.temperature_id)
            self.state.set('uptime_id', self.uptime_id)


        self.computer_id = self.state.get('computer_id')
        self.cpu_id = self.state.get('cpu_id')
        self.memory_id = self.state.get('memory_id')

        if not self.computer_id or not self.cpu_id or not self.memory_id:
            logger.info("State data insufficient, registering computer to server")
            self.computer_id, self.cpu_id, self.memory_id = self.register_computer()
            self.state.set('computer_id', self.computer_id)
            self.state.set('cpu_id', self.cpu_id)
            self.state.set('memory_id', self.memory_id)

    def register_heater(self):
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

    def register_computer(self):
        # Register the device and metrics
        try:
            device = self.api.device_create(Device(description="Computer"))
            logger.info(f"Device created: {device}")

            if device.id is None:
                logger.error("Device ID is None")
                exit(1)

            computer_id = device.id

            cpu = self.api.metric_create(Metric(name="CPU", data_type="float"))

            if cpu.id is None:
                logger.error("CPU ID is None")
                exit(1)

            cpu_id = cpu.id

            memory = self.api.metric_create(Metric(name="Memory", data_type="float"))

            if memory.id is None:
                logger.error("Memory ID is None")
                exit(1)

            memory_id = memory.id
            
            return computer_id, cpu_id, memory_id
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

    def get_computer_commands_from_server(self):
        return self.api.command_get_by_device_id(self.computer_id)

    def send_cpu_to_server(self, cpu: float, timestamp: datetime):
        try:
            logger.info(f"Sending CPU: {cpu} at {timestamp}")
            cpu_message = Message(device_id=self.computer_id, metric_id=self.cpu_id, metric_value=str(cpu), timestamp=timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'))
            self.api.message_create(cpu_message)
        except ApiException as e:
            logger.error(f"Exception when calling DefaultApi->message_create: {e}")

    def send_memory_to_server(self, memory: float, timestamp: datetime):
        try:
            logger.info(f"Sending memory: {memory} at {timestamp}")
            memory_message = Message(device_id=self.computer_id, metric_id=self.memory_id, metric_value=str(memory), timestamp=timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'))
            self.api.message_create(memory_message)
        except ApiException as e:
            logger.error(f"Exception when calling DefaultApi->message_create: {e}")
