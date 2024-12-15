import logging

import psutil
import screen_brightness_control as sbc

from device.executor import CommandExecutor

logger = logging.getLogger(__name__)

class Computer(CommandExecutor):
    def get_cpu_usage(self) -> float:
        return psutil.cpu_percent(interval=1)

    def get_memory_percent(self) -> float:
        return psutil.virtual_memory().percent

    def execute(self, command: str):
        logger.info(f"Executing command: {command}")

        command_args = command.split(" ")

        if command_args[0] == "brightness":
            return self.set_brightness(int(command_args[1]))
        if command_args[0] == "exit":
            return self.exit_program()

        logger.error("Invalid command")
        return

    def set_brightness(self, brightness: int):
        if brightness < 0 or brightness > 100:
            return
        sbc.set_brightness(brightness)

    def exit_program(self):
        logger.info("Exiting program...")
        exit(0)
