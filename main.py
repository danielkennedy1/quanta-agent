import logging

from device.heater import Heater
from config.config import Config

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)
root_logger = logging.getLogger()

if __name__ == "__main__":
    config = Config("config/config.json")
    config.logging.configure_logger(root_logger)

    logger.info("Starting device.py")
    heater = Heater(config.devices.device_list[0].ip, config.devices.device_list[0].port)

    #heater.get_heartbeat()
    heater.get_system_time()
    #logger.warning(heater.get_avg_temperature_for_minute())
    #logger.warning(heater.get_uptime_for_minute())
    #heater.set_temperature_for_duration(25, 60)
    #heater.set_power_for_duration(True, 60)
