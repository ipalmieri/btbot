import datetime
import logging
import logging.config
import json
import os


logger = logging.getLogger("btbot")
config_file = 'logconf.json'
default_level = logging.INFO

def init_logging():
    """Loads config file and starts logger"""
    global config_file
    global default_level

    if os.path.exists(config_file):
        with open(config_file, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)


