import logging
from time import sleep
import datetime
import uuid

from quanta_client.configuration import Configuration
from quanta_client.api_client import ApiClient
from quanta_client.api.default_api import DefaultApi
from quanta_client.exceptions import ApiException

from device.heater import Heater
from device.computer import Computer

from config.config import Config
from comms.client import Client

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)
root_logger = logging.getLogger()

if __name__ == "__main__":
    mac = uuid.getnode()
    mac_address_str = ':'.join(f'{(mac >> i) & 0xff:02x}' for i in range(0, 8*6, 8)[::-1])

    config = Config("config/config.json")
    config.logging.configure_logger(root_logger)

    heater = Heater(config.devices.device_list[0].ip, config.devices.device_list[0].port)
    computer = Computer()



    quanta_config = Configuration(host=config.server.base_url)
    client = ApiClient(quanta_config, header_name="Agent_MAC", header_value=mac_address_str)
    api = DefaultApi(client)

    client = Client(api)

    sleep_time = 5

    while True:
        try:
            logger.info("Dealing with heater")
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

            logger.info("Dealing with computer")


            cpu_usage = computer.get_cpu_usage()
            client.send_cpu_to_server(cpu_usage, datetime.datetime.now())

            memory_usage = computer.get_memory_percent()
            client.send_memory_to_server(memory_usage, datetime.datetime.now())

            try:
                computer_commands = client.get_computer_commands_from_server()
                for command in computer_commands:
                    logger.info(f"Received command: {command}")
                    computer.execute(command.command)
            except ApiException as e:
                logger.error(f"Exception when calling DefaultApi->command_get_by_device_id: {e}")
                computer_commands = []


            logger.info("Sleeping..")
            sleep(sleep_time)
        except ApiException as e:
            logger.error(f"Exception when calling DefaultApi->message_create: {e}")
