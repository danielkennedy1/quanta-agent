import logging
from time import sleep

from quanta_client.configuration import Configuration
from quanta_client.api_client import ApiClient
from quanta_client.api.default_api import DefaultApi
from quanta_client.exceptions import ApiException

from device.heater import Heater
from config.config import Config
from comms.client import Client

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)
root_logger = logging.getLogger()

if __name__ == "__main__":
    config = Config("config/config.json")
    config.logging.configure_logger(root_logger)

    heater = Heater(config.devices.device_list[0].ip, config.devices.device_list[0].port)

    quanta_config = Configuration(host=config.server.base_url)
    client = ApiClient(quanta_config)
    api = DefaultApi(client)

    client = Client(api)

    sleep_time = 5

    while True:
        try:
            temperature_result = heater.get_avg_temperature_for_minute()
            if temperature_result is not None:
                client.send_temperature_to_server(*temperature_result)

            uptime_result = heater.get_uptime_for_minute()
            if uptime_result is not None:
                client.send_uptime_to_server(*uptime_result)

            try:
                heater_commands = client.get_heater_commands_from_server()
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
