import struct
from datetime import datetime
import logging

from typing import Tuple
logger = logging.getLogger(__name__)

import socket
PROTOCOL_START_BYTE = 0x02

class Heater(object):
    protocol_function_table = {
        "heartbeat": 0x00,
        "get_system_time": 0x01,
        "set_temperature_for_duration": 0x02,
        "set_control_for_duration": 0x03,
        "get_avg_temperature_for_minute": 0x04,
        "get_uptime_for_minute": 0x05,
    }

    heartbeat = b"HEARTBEAT"


    def __init__(self, ip: str, port: int):
        logger.info(f"Creating device object with IP: {ip} and port: {port}")
        self.ip = ip
        self.port = port

    def get_heartbeat(self):
        logger.info("Getting heartbeat")
        packet = self.construct_packet(self.protocol_function_table["heartbeat"], b"")
        response_payload = self.send_packet(packet)
        logger.debug(f"Received response: {response_payload}")   

        if response_payload[:9] == self.heartbeat:
            logger.info("Received heartbeat response")
        else:
            logger.error("Received invalid response")


    def get_system_time(self) -> datetime:
        logger.info("Getting system time")
        packet = self.construct_packet(self.protocol_function_table["get_system_time"], b"")

        payload = self.send_packet(packet)

        logger.debug(f"Received response: {payload}")

        # clip null bytes from the end of the payload string
        payload = payload.rstrip(b'\x00')

        timestamp = datetime.fromisoformat(payload.decode('ascii'))

        logger.info(f"System time: {timestamp}")

        return timestamp


    def get_avg_temperature_for_minute(self) -> Tuple[float, datetime] | None:
        logger.info("Getting average temperature for the last minute")
        packet = self.construct_packet(self.protocol_function_table["get_avg_temperature_for_minute"], b"")

        payload = self.send_packet(packet)

        if len(payload) == 0:
            logger.error("No response received from ESP32")
            return None

        unix_timestamp: int = struct.unpack('<Q', payload[:8])[0]
        avg_temp = struct.unpack('<f', payload[8:12])[0]

        logger.debug(f"Unix Timestamp: {unix_timestamp}")

        timestamp = datetime.fromtimestamp(float(unix_timestamp))

        timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')

        logger.debug(f"  {timestamp_str} UTC")
        logger.debug(f"  Float Value: {avg_temp}")

        return avg_temp, timestamp


    def get_uptime_for_minute(self) -> Tuple[float, datetime] | None:
        logger.info("Getting uptime for the next available minute")
        packet = self.construct_packet(self.protocol_function_table["get_uptime_for_minute"], b"")

        payload = self.send_packet(packet)

        if len(payload) == 0:
            logger.error("No response received")
            return None

        unix_timestamp: int = struct.unpack('<Q', payload[:8])[0]
        uptime = struct.unpack('<f', payload[8:12])[0]

        logger.debug(f"Unix Timestamp: {unix_timestamp}")

        timestamp = datetime.fromtimestamp(float(unix_timestamp))

        timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')

        logger.debug("Payload Analysis:")
        logger.debug(f"  Unix Timestamp: {unix_timestamp} ({timestamp_str} UTC)")
        logger.debug(f"  Float Value: {uptime}")

        return uptime, timestamp


    def set_power_for_duration(self, power: bool, duration: int):
        logger.info(f"Setting power to {power} for {duration} seconds")
        payload = struct.pack('<?I', power, duration)
        packet = self.construct_packet(self.protocol_function_table["set_control_for_duration"], payload)

        logger.debug(f"complete packet: {packet.hex()}")
        
        self.send_packet(packet, expect_response=False)

    def set_temperature_for_duration(self, target_temp: float, duration: int):
        logger.info(f"Setting temperature to {target_temp} for {duration} seconds")
        payload = struct.pack('<fI', target_temp, duration)
        # Construct the packet to set the temperature for a duration
        packet = self.construct_packet(self.protocol_function_table["set_temperature_for_duration"], payload)

        logger.debug(f"complete packet: {packet.hex()}")
        
        # Send the packet to the ESP32
        self.send_packet(packet)



    def send_packet(self, packet: bytes, expect_response = True) -> bytes:
        try:
            # Create a socket and connect to the ESP32 server
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.ip, self.port))
                logger.info(f"Connected to {self.ip}:{self.port}")
                
                # Send the message
                s.sendall(packet)
                logger.debug(f"Sent: {packet.hex()}")

                # Receive the response
                if expect_response:
                    response = s.recv(260)
                    logger.info("Received response")
                    logger.debug(f"start_byte: {response[0]:02X}")
                    logger.debug(f"function_id: {response[1]:02X}")
                    logger.debug(f"length: {response[2]}")
                    length = response[2]
                    payload = response[3:-1]
                    logger.debug(f"payload (hex): {' '.join(f'{byte:02X}' for byte in payload)}")
                    try:
                        logger.debug(f"payload (ascii): {payload.decode('ascii')}")
                    except UnicodeDecodeError:
                        logger.debug("payload (ascii): <non-ascii data>")
                    return payload[:length]
        except Exception as e:
            logger.error(f"Error: {e}")
        return bytes()
    
    def construct_packet(self, function_id: int, payload: bytes, start_byte: int = PROTOCOL_START_BYTE) -> bytes:
        length = len(payload)
        message = bytes([start_byte, function_id, length]) + payload
        return message

