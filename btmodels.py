from sqlalchemy import *
import datetime
import btools, dbcon
from btorder import btqntType


class bsheet(dbcon.baseModel):
    __tablename__ = 'bsheet'
    asset = Column(String, primary_key=True)
    qnt_real = Column(btqntType)
    qnt_comm = Column(btqntType)

        
class dataQuote:
    def __init__(self, dt, value):
        self.datetime = dt
        self.value = value

    def __str__(self):
        return str(self.datetime) + " " + str(self.value)
