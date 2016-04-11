
from mbrequest import *
from mbinfo import *
import time


if __name__ == '__main__':

    b = mbBitInfo()
    
    print b.lastPrice().datetime, b.lastPrice().value

    blist = b.tradeList(2)

    for t in blist:

        print t.date, t.price, t.volume, t.id, t.type
    
    pass
