from ordermngr import *
import btools
import btdata

logger = btools.logger

def main():

    btools.init_logging()
    
    logger.info("teste info")
    logger.warning("teste warn")
    logger.error("teste error")
    logger.debug("teste debug")

    bt = orderManager()

    btdata.base.metadata.create_all(btdata.engine)

    ordm = btdata.order()
    ordm.otype = 'BUY'
    ordm.quantity = 1.056
    ordm.price = 0.0001
    ordm.asset = "BTC"


    #bt.reload_added_orders()

    print ordm.oid
    s = btdata.session()
    
    #s.add(ordm)
    #s.commit()
    bt.add_order(ordm)
    
    print ordm.oid

    ordm2 = bt.get_order(ordm.oid)

    ordm2.status = 'CREATED'
    bt.add_order(ordm)
    
    print ordm.status, ordm2.status

    
    
if __name__ == '__main__':
    main()
