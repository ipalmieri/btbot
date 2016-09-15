from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.url import URL
import datetime
import logging
import logging.config
import json
import os
import settings

engine = create_engine(URL(**settings.BTDATA_PARAMS))
session = sessionmaker(bind=engine)

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


