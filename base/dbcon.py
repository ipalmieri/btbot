from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import make_transient
from sqlalchemy.engine.url import URL
from contextlib import contextmanager
from . import btools
import settings

logger = btools.logger
engine = create_engine(URL(**settings.BTDATA_PARAMS))
session = sessionmaker(bind=engine)
baseModel = declarative_base()


def init_db():
    """Starts database operations."""
    logger.info("Starting database operations")
    baseModel.metadata.create_all(engine)



def safe_commit(s):
    """Provides a safe commit with rollback."""
    try:
        s.commit()
    except Exception as e:
        s.rollback()
        logger.error("Failed commit at safe_commit(): " + str(e))
    else:
        return True
    return False


@contextmanager
def session_scope():
    """Provides a transactional scope around a series of operations."""
    sess = session()
    try:
        yield sess
        sess.commit()
    except Exception as e:
        sess.rollback()
        logger.error("Failed commit at session_scope(): " + str(e))
    finally:
        sess.close()
