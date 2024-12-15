import json
import logging
import sys
import coloredlogs
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class DeviceConfig:
    ip: str
    port: int

class Config:
    _instance = None

    def __new__(cls, config_file_path: str):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls) # use the type constructor to create the instance
            cls._instance._initialize(config_file_path) # initialize the instance using metaclass member function
        return cls._instance

    def _initialize(self, config_file_path: str):
        with open(config_file_path) as config_file:
            self.config = json.load(config_file)

        if not self.config:
            raise ValueError("Config file is empty")

        if not self.config.get('log'):
            logger.warning("No logging configuration found in config file")
        
        self.logging = self.LoggingConfig(self.config.get('log', {}))

        if not self.config.get('server'):
            logger.warning("No server configuration found in config file")

        self.server = self.ServerConfig(self.config.get('server', {}))
        
        if not self.config.get('devices'):
            logger.warning("No devices configuration found in config file")

        self.devices = self.DeviceConfig(self.config.get('devices', []))

    def get(self, key):
        """Access configuration settings by key."""
        return self.config.get(key)

    class LoggingConfig:
        def __init__(self, log_config):
            self.log_file = log_config.get('file', 'default.log')
            self.log_level = log_config.get('level', 'INFO')

        def configure_logger(self, logger: logging.Logger):
            logger.handlers = []

            # File handler
            file_handler = logging.FileHandler(self.log_file)
            file_handler.setLevel(logging._nameToLevel[self.log_level.upper()])
            logger.addHandler(file_handler)

            # Standard output handler
            stdout_handler = logging.StreamHandler(sys.stdout)
            stdout_handler.setLevel(logging._nameToLevel[self.log_level.upper()])
            logger.addHandler(stdout_handler)

            coloredlogs.install(level=self.log_level.upper(), logger=logger)

    class ServerConfig:
        def __init__(self, server_config):
            logger.info("Server config: %s", server_config)
            self.protocol = server_config.get('protocol', 'http')
            self.host = server_config.get('host', 'localhost')
            self.port = server_config.get('port', 8000)
            self.path = server_config.get('path', '/')
            self.base_url = f"{self.protocol}://{self.host}:{self.port}{self.path}"

    class DeviceConfig:
        def __init__(self, devices_config_list):
            self.device_list = [DeviceConfig(device_config["ip"], device_config["port"]) for device_config in devices_config_list]
            self.device_count = len(self.device_list)



config = Config("config/config.json")
