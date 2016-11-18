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
    

    dat = mbinfo.info_request('ticker')

    print dat


    
if __name__ == '__main__':
    main()
