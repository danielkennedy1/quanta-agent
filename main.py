from config.config import Config
import logging
import sys
import json
from metrics import get_metrics
from model import SystemMetrics

logger = logging.getLogger(__name__)
conf = Config()
conf.configure_logger(logger)

logger.info(get_metrics()) # type: ignore

with open(conf.log_file) as f:
    deser = SystemMetrics.from_dict(json.load(f)) # type: ignore

logger.info(deser)



sys.exit()
