import logging
import sys
import json
from metrics import get_metrics
from model import SystemMetrics
from config.config import config

config.logging.configure_logger(logging.getLogger())

logger = logging.getLogger(__name__)

logger.info(get_metrics()) # type: ignore

with open(config.logging.log_file) as f:
    deser = SystemMetrics.from_dict(json.load(f)) # type: ignore

logger.info(deser)

sys.exit()
