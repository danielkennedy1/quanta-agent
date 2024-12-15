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


if __name__ == "__main__":
    config = Config("config/config.json")
    config.logging.configure_logger(root_logger)

    heater = Heater(config.devices.device_list[0].ip, config.devices.device_list[0].port)

    quanta_config = Configuration(host=config.server.base_url)
    client = ApiClient(quanta_config)
    api = DefaultApi(client)

    heater_id, temperature_id, uptime_id = register_to_server()

    while True:
        try:
            temperature_result = heater.get_avg_temperature_for_minute()
            uptime_result = heater.get_uptime_for_minute()

            if temperature_result is None or uptime_result is None:
                logger.error("No response received from ESP32")
                continue

            temperature, temperature_timestamp = temperature_result
            uptime, uptime_timestamp = uptime_result

            logger.info(f"Temperature: {temperature} at {temperature_timestamp}")
            logger.info(f"Uptime: {uptime} at {uptime_timestamp}")

            logger.info("Sending data to server")
            temperature_message = Message(device_id=heater_id, metric_id=temperature_id, metric_value=str(temperature), timestamp=temperature_timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'))
            uptime_message = Message(device_id=heater_id, metric_id=uptime_id, metric_value=str(uptime), timestamp=uptime_timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'))

            api.message_create(temperature_message)
            api.message_create(uptime_message)

            logger.info("Data sent to server")


            logger.info("Sleeping..")
            sleep(5)
        except ApiException as e:
            logger.error(f"Exception when calling DefaultApi->message_create: {e}")






    #logger.warning(heater.get_avg_temperature_for_minute())
    #logger.warning(heater.get_uptime_for_minute())
    #heater.set_temperature_for_duration(25, 60)
    #heater.set_power_for_duration(True, 60)


