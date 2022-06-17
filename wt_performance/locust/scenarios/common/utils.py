import logging
import os

#Logger function initialization

logger = logging.getLogger(__name__)

logger.setLevel(getattr(logging, os.getenv("LOG_LEVEL")))