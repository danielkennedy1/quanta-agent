from dotenv import load_dotenv
import os
from logging import Logger
import logging
import coloredlogs
import sys

class Config(object):
    def __init__(self):
        load_dotenv()
        self.greeting = os.getenv("GREETING", "default greeting")

        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.log_file = os.getenv("LOG_FILE", "default_log.txt")

    def configure_logger(self, logger: Logger):
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging._nameToLevel[self.log_level])
        logger.addHandler(file_handler)
        
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setLevel(logging._nameToLevel[self.log_level])
        logger.addHandler(stdout_handler)
        
        coloredlogs.install(level=self.log_level, logger=logger)

