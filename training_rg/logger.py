import os
import logging
from logging import Formatter

from training_rg.constants import BASE_DIR, LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)
logger.setLevel(logging.DEBUG)

fh = logging.FileHandler(os.path.join(BASE_DIR, f'{LOGGER_NAME}.log'))
fh.setFormatter(Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)
