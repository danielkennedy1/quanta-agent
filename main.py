import logging

from device.device import Device
from config.config import Config

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)
root_logger = logging.getLogger()

if __name__ == "__main__":
    config = Config("config/config.json")
    config.logging.configure_logger(root_logger)

    logger.info("Starting device.py")
    device = Device(config.devices.device_list[0].ip, config.devices.device_list[0].port)

    device.get_heartbeat()
    device.get_system_time()
