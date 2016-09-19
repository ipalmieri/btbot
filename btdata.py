import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
import settings

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
    try:
        s.commit()
    except Exception, e:
        logger.error("Error commiting changes: " + str(e))
    else:
        return True
    return False
        

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
