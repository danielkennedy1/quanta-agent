import logging
from time import sleep

from quanta_client.models.device import Device
from quanta_client.configuration import Configuration
from quanta_client.api_client import ApiClient
from quanta_client.api.default_api import DefaultApi
from quanta_client.exceptions import ApiException
from quanta_client.models.message import Message
from quanta_client.models.metric import Metric

from device.heater import Heater
from config.config import Config

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)
root_logger = logging.getLogger()

def register_to_server():
    # Register the device and metrics
    try:
        device = api.device_create(Device(description="ESP32 Heater"))
        logger.info(f"Device created: {device}")

        if device.id is None:
            logger.error("Device ID is None")
            exit(1)

        heater_id = device.id

        temperature = api.metric_create(Metric(name="Temperature", data_type="float"))

        if temperature.id is None:
            logger.error("Temperature ID is None")
            exit(1)

        temperature_id = temperature.id

        uptime = api.metric_create(Metric(name="Uptime", data_type="float"))

        if uptime.id is None:
            logger.error("Uptime ID is None")
            exit(1)

        uptime_id = uptime.id
        
        return heater_id, temperature_id, uptime_id
    except ApiException as e:
        logger.error(f"Exception when calling DefaultApi->device_create: {e}")
        exit(1)

def send_temperature_to_server(temperature, timestamp):
    try:
        logger.info(f"Sending temperature: {temperature} at {timestamp}")
        temperature_message = Message(device_id=heater_id, metric_id=temperature_id, metric_value=str(temperature), timestamp=timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'))
        api.message_create(temperature_message)
    except ApiException as e:
        logger.error(f"Exception when calling DefaultApi->message_create: {e}")

def send_uptime_to_server(uptime, timestamp):
    try:
        logger.info(f"Sending uptime: {uptime} at {timestamp}")
        uptime_message = Message(device_id=heater_id, metric_id=uptime_id, metric_value=str(uptime), timestamp=timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'))
        api.message_create(uptime_message)
    except ApiException as e:
        logger.error(f"Exception when calling DefaultApi->message_create: {e}")

if __name__ == "__main__":
    config = Config("config/config.json")
    config.logging.configure_logger(root_logger)

    heater = Heater(config.devices.device_list[0].ip, config.devices.device_list[0].port)

    quanta_config = Configuration(host=config.server.base_url)
    client = ApiClient(quanta_config)
    api = DefaultApi(client)

    heater_id, temperature_id, uptime_id = register_to_server()

    sleep_time = 5

    while True:
        try:
            temperature_result = heater.get_avg_temperature_for_minute()
            if temperature_result is not None:
                send_temperature_to_server(*temperature_result)

            uptime_result = heater.get_uptime_for_minute()
            if uptime_result is not None:
                send_uptime_to_server(*uptime_result)

            try:
                heater_commands = api.command_get_by_device_id(heater_id)
                for command in heater_commands:
                    logger.info(f"Received command: {command}")
                    heater.execute(command.command)
            except ApiException as e:
                logger.error(f"Exception when calling DefaultApi->command_get_by_device_id: {e}")
                heater_commands = []


            logger.info("Sleeping..")
            sleep(sleep_time)
        except ApiException as e:
            logger.error(f"Exception when calling DefaultApi->message_create: {e}")
