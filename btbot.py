from btorder import *
from ordermngr import *
from providers import mbinfo, mbtrade
from btarena import btArena
import time
import btools
import btmodels


logger = btools.logger

def main():

    btools.init_logging()
    dbcon.init_db()

    bta = btArena()

    mng = orderManager()
    bif = mbinfo.mbInfo()
    btd = mbtrade.mbProvider()
    mng.add_provider(btd)

    while not btd.funds_table:
        time.sleep(1)

    for asset, funds in btd.funds_table.iteritems():
        print asset, funds.total, funds.available, funds.tradable, funds.expected
                                                            



    
if __name__ == '__main__':
    main()
