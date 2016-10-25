from sqlalchemy import *
import datetime
import btools, dbcon
from btorder import btqntType


class bsheet(dbcon.baseModel):
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
