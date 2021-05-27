import logging

import pandas as pd

# from data.utils import upload_blob
# from settings import BUCKET_LOGS

common_log_filename = "logs/game_run.log"
current_log_filename = "logs/game run {}.log".format(pd.Timestamp.now().strftime("%Y-%m-%d %H_%M_%S"))

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create handlers
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler(common_log_filename, mode="w")
c_handler.setLevel(logging.WARNING)
f_handler.setLevel(logging.DEBUG)

# Create formatters and add it to handlers
c_format = logging.Formatter("%(message)s")
f_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)

# Add handlers to the logger
logger.addHandler(c_handler)
logger.addHandler(f_handler)

logger.info("started logging")


def save_current_log():
    pass
