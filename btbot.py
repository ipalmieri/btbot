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

    dat = bif.last_quote('BTC')
    
    print dat


    
if __name__ == '__main__':
    main()
