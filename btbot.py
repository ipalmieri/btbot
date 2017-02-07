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
    

    
if __name__ == '__main__':
    main()
