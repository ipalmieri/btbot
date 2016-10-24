import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
from contextlib import contextmanager
import btools
import settings

logger = btools.logger
engine = create_engine(URL(**settings.BTDATA_PARAMS))
session = sessionmaker(bind=engine)

base = declarative_base()

moneyType = DECIMAL(10, 8)
btqntType = DECIMAL(10, 8)

statusEnum = Enum('CREATED',
                  'ADDED',
                  'OPEN',
                  'EXECUTED',
                  'CANCELLED',
                  'INVALID',
                  name='ordstat')


def safe_commit(s):
    """Provides a safe commit with rollback."""
    try:
        s.commit()
    except Exception, e:
        s.rollback()
        logger.error("Failed commit at safe_commit(): " + str(e))
    else:
        return True
    return False


@contextmanager
def session_scope():
    """Provides a transactional scope around a series of operations."""
    session = btdata.session()
    try:
        yield session
        session.commit()
    except Exception, e:
        session.rollback()
        logger.error("Failed commit at session_scope(): " + str(e))
    finally:
        session.close()
        

class order(base):
    """ Buy/Sell order to be tracked
    """
    __tablename__ = 'orders'
    oid = Column(Integer, primary_key=True, autoincrement=True)
    otype = Column(Enum('BUY','SELL', name="ordtype"), nullable=False)
    provider = Column(String)
    quantity = Column(btqntType, nullable=False)
    price = Column(moneyType, nullable=False)
    asset = Column(String, ForeignKey('bsheet.asset'), nullable=False)
    exec_quantity = Column(btqntType, default=0)
    exec_price = Column(moneyType, default=0)
    fees = Column(moneyType, default=0)
    status = Column(statusEnum, nullable=False)
    updated_ts = Column(TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp())
    created_ts = Column(TIMESTAMP, server_default=func.now())
    target_date = Column(Date, server_default=func.now())
    remote_info = Column(String)
    
    def __init__(self):
        self.status = 'CREATED'

        
    def save(self):
        s = session()
        s.add(self)
        ret = safe_commit(s)
        s.refresh(self)
        s.expunge(self)
        s.close()
        return ret

    
    @classmethod
    def get_by_id(cls, oid):
        s = session()
        try:
            ordr = s.query(order).filter(order.oid == oid).one()
            s.expunge(ordr)
        except Exception, e:
            logger.debug("Order " + str(oid) + " not found in database: " + str(e))
            ordr = None
        finally:
            s.close()
        return ordr
      
    
    @classmethod
    def get_by_status(cls, status):
        s = session()
        try:
            qry = s.query(order).filter(order.status == 'ADDED')
            orders = qry.order_by(order.updated_ts).all()
        except Exception, e:
            logger.error("Error getting order list: " + str(e))
            orders = None
        finally:
            s.expunge_all()
            s.close()
        return orders
        
    
class bsheet(base):
    __tablename__ = 'bsheet'
    asset = Column(String, primary_key=True)
    qnt_real = Column(btqntType)
    qnt_comm = Column(btqntType)


        
class btQuote:
    def __init__(self, dt, value):
        self.datetime = dt
        self.value = value
        


class btTrade:
    def __init__(self):
        self.date = None
        self.price = None
        self.volume = None
        self.id = None
        self.type = None
