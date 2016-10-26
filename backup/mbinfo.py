import datetime
from mbrequest import *
from btdata import *


# Bitcoin information class
class mbBitInfo:

    # return the price of the last trade
    def lastPrice(self):

        ltrade = self.tradeList(1)

        if ltrade:
            val = ltrade[0].price
            dt = ltrade[0].date
            return btQuote(dt, val)

        return None

    
    # return last count trades
    def tradeList(self, count=1):

        ret = []
        
        tlist = cached_api_request('trades')

        for t in reversed(tlist[-count:]):

            tr = btTrade()
            tr.date = datetime.datetime.fromtimestamp(t['date'])
            tr.price = t['price']
            tr.volume = t['amount']
            tr.id = t['tid']
            tr.type = t['type']
            
            ret.append(tr)
        
        return ret


    
    # return list of orders
    def orderBook(self):
        pass

    


# Litecoin information class
class mbLiteInfo:
    
    pass
