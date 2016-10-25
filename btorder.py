from sqlalchemy.orm.session import make_transient
from sqlalchemy import *
import btools, dbcon, arpersist

logger = btools.logger

moneyType = DECIMAL(10, 8)
btqntType = DECIMAL(10, 8)

statusEnum = Enum('CREATED',
                  'ADDED',
                  'OPEN',
                  'EXECUTED',
                  'CANCELLED',
                  'INVALID',
                  name='ordstat')


class order(dbcon.baseModel, arpersist.baseAR):
    """ Buy/Sell order to be tracked.
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

        
    @classmethod
    def get_by_id(cls, oid):
        s = dbcon.session()
        try:
            ordr = s.query(order).filter(order.oid == oid).one()
            make_transient(ordr)
        except Exception, e:
            logger.debug("Order " + str(oid) + " not found in database: " + str(e))
            ordr = None
        finally:
            s.close()
        return ordr

    
    @classmethod
    def get_by_status(cls, status):
        s = dbcon.session()
        try:
            qry = s.query(order).filter(order.status == 'ADDED')
            orders = qry.order_by(order.updated_ts).all()
        except Exception, e:
            logger.error("Error getting order list: " + str(e))
            orders = None
        else:
            map(make_transient, orders)            
        finally:
            s.expunge_all()
            s.close()
        return orders
        
