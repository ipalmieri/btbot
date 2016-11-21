from btorder import *
from ordermngr import *
from providers import mbtrade, mbinfo
import time
import btools
import btmodels


logger = btools.logger

def main():

    btools.init_logging()
    dbcon.init_db()
    
    bif = mbinfo.mbInfo()
    btd = mbtrade.mbProvider()
    
    #btd.update_funds()

    time.sleep(10)

    for asset, funds in btd.fundsTable.iteritems():
        print asset, funds.total, funds.available, funds.tradable, funds.expected


    
if __name__ == '__main__':
    main()
