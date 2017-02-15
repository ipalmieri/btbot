from btorder import *
from ordermngr import *
from providers import mbinfo, mbtrade
import btarena
import time
import btools
import btmodels


logger = btools.logger

def main():

    btools.init_logging()
    dbcon.init_db()

    btarena.start_arena()

    
    
    
if __name__ == '__main__':
    main()
