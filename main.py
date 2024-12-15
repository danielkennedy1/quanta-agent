import logging

from quanta_client.models.device import Device
from quanta_client.configuration import Configuration
from quanta_client.api_client import ApiClient
from quanta_client.api.default_api import DefaultApi
from quanta_client.exceptions import ApiException

from device.heater import Heater
from config.config import Config

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)
root_logger = logging.getLogger()

if __name__ == "__main__":
    config = Config("config/config.json")
    config.logging.configure_logger(root_logger)

    heater = Heater(config.devices.device_list[0].ip, config.devices.device_list[0].port)

    logger.info(f"Base URL: {config.server.base_url}")

    quanta_config = Configuration(host=config.server.base_url)
    client = ApiClient(quanta_config)
    api = DefaultApi(client)

    # Create a device
    device = Device.from_dict({"description": "Heater"})

    if device is None:
        logger.error("Device is None")
        exit(1)

    logger.info(f"Device: {device}")

    try:
        created_device = api.device_create(device)

        logger.info(f"Created device: {created_device}")
    except ApiException as e:
        logger.error(f"Exception when calling DefaultApi->create_device: {e}")


    #logger.warning(heater.get_avg_temperature_for_minute())
    #logger.warning(heater.get_uptime_for_minute())
    #heater.set_temperature_for_duration(25, 60)
    #heater.set_power_for_duration(True, 60)


