import json
import logging
from copy import deepcopy
from datetime import datetime

import pandas as pd

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


def serialize(data_to_serialize):
    data = deepcopy(data_to_serialize)
    if isinstance(data, (int, float, str, bool)):
        return data
    if isinstance(data, datetime):
        return data.isoformat()
    if isinstance(data, list):
        return [serialize(i) for i in data]
    if isinstance(data, dict):
        return {key: serialize(value) for key, value in data.items()}
    if data is None:
        return data
    raise NotImplementedError(
        f"Serialisation is not implemented for {data_to_serialize} of type {type(data_to_serialize)}"
    )


def dump_locally(data, name):
    with open(f"{name}.json", "w") as f:
        f.write(json.dumps(serialize(data)))
        f.write("\n")
