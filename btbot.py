from btorder import *
from ordermngr import *
from providers import mbitcoin
import time
import btools
import btmodels


logger = btools.logger

def main():

    btools.init_logging()
    dbcon.init_db()
    

    bt = orderManager()
    #bt.reload_added_orders()

    mbprov = mbitcoin.mbProvider()
    bt.set_broker(mbprov)
    
    
    ordm = order()
    ordm.otype = 'SELL'
    ordm.quantity = 0.009
    ordm.price = 2402.1
    ordm.asset = "BTC"
    ordm.provider = mbprov.name
    
    bt.add_order(ordm)
    bt.flush_all()
    
    while ordm.status == 'ADDED':
        time.sleep(1)
    
    while True:
        mbprov.update_order(ordm)
        time.sleep(10)
        if ordm.status == 'EXECUTED':
            break
        
    params = {
        'tapi_method': 'list_orders',
        'tapi_nonce': mbitcoin.get_nonce(),
        'coin_pair': 'BRLBTC'
    }

    #a = mbitcoin.trade_request(params)
    #mbitcoin.validate_response(a)
    #print a
    
if __name__ == '__main__':
    main()
