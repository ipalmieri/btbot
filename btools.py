import datetime
import logging
import logging.config
import json
import os


logger = logging.getLogger("btbot")


def init_logging():

    config_file = "logconf.json"
    default_level = logging.INFO

    if os.path.exists(config_file):
        with open(config_file, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)


