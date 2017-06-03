from sqlalchemy import *
from decimal import *
import datetime
import btools, dbcon
from btorder import btqntType


class bsheet(dbcon.baseModel):
    __tablename__ = 'bsheet'
    asset = Column(String, primary_key=True)
    provider = Column(String, primary_key=True)
    available = Column(btqntType)
    total = Column(btqntType)
    tradable = Column(btqntType)
    expected = Column(btqntType)


class fundValues():
    def __init__(self):
        self.total = Decimal(0)
        self.available = Decimal(0)
        self.tradable = Decimal(0)
        self.expected = Decimal(0)
    
        
class dataQuote:
    def __init__(self, dt, value):
        self.datetime = dt
        self.value = value

    def __str__(self):
        return str(self.datetime) + " " + str(self.value)


