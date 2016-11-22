from btorder import *
from ordermngr import *
from providers import mbinfo, mbtrade
import time
import btools
import btmodels


logger = btools.logger

def main():

    btools.init_logging()
    dbcon.init_db()

    mng = orderManager()
    bif = mbinfo.mbInfo()
    btd = mbtrade.mbProvider()
    mng.add_provider(btd)
    
    ordm = order()
    ordm.otype = 'SELL'
    ordm.quantity = 0.009
    ordm.price = 2602.1
    ordm.asset = 'BTC'
    ordm.currency = 'BRL' 
    ordm.provider = btd.name

    time.sleep(5)

    for asset, funds in btd.funds_table.iteritems():
        print asset, funds.total, funds.available, funds.tradable, funds.expected

    mng.add_order(ordm)
    mng.flush_all()

    btd.update_funds()

    time.sleep(5)
    
    for asset, funds in btd.funds_table.iteritems():
        print asset, funds.total, funds.available, funds.tradable, funds.expected


    
if __name__ == '__main__':
    main()
