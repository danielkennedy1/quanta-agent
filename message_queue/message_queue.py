import threading
import quanta_client
from queue import Queue
import logging
from config.config import Config
from time import sleep

logger = logging.getLogger(__name__)
config = Config("config/config.json")
config.logging.configure_logger(logger)


class MessageQueue(object):

    def __init__(self, api: quanta_client.DefaultApi):
        self.api_client = api
        self.queue = Queue()
        self.stop_event = threading.Event()  # Used to stop the background thread

    def post_message(self, message: quanta_client.Message):
        """Post a message to the message queue"""
        self.queue.put(message)

    def start(self):
        """Start the background thread"""
        self.stop_event.clear()
        self.thread = threading.Thread(target=self._run)
        self.thread.start()

    def stop(self):
        """Stop the background thread"""
        self.stop_event.set()
        self.thread.join()

    def _run(self):
        """Background thread that posts messages to the API"""
        while not self.stop_event.is_set():
            logger.info("Posting message, Queue size: %d", self.queue.qsize())
            message = self.queue.get()
            if message:
                try:
                    self.api_client.message_create(message)
                except Exception as e:
                    logger.error(f"Error posting message: {e}")
                    self.queue.put(message)
                    sleep(5)
            else:
                logger.info("No message to post")
    

    
