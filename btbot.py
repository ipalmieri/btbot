from btorder import *
from ordermngr import *
import btools
import btmodels

logger = btools.logger

def main():

    btools.init_logging()
    dbcon.init_db()
    
    logger.info("teste info")
    logger.warning("teste warn")
    logger.error("teste error")
    logger.debug("teste debug")

    bt = orderManager()

  
    ordm = order()
    ordm.otype = 'BUY'
    ordm.quantity = 1.056
    ordm.price = 0.0001
    ordm.asset = "BTC"


    bt.reload_added_orders()

    print str(ordm.oid) + ":" + ordm.status

    s = dbcon.session()
    
    #s.add(ordm)
    #s.commit()
    bt.add_order(ordm)
    
    ordm2 = order.get_by_id(ordm.oid)

    ordm2.status = 'CREATED'
    #bt.add_order(ordm)

    ordm2.oid = 1
    ordm2 = ordm2.reload()
    
    print str(ordm.oid) + ":" + ordm.status
    print str(ordm2.oid) + ":" + ordm2.status

    
    #bt.reset_queue()

    
if __name__ == '__main__':
    main()
