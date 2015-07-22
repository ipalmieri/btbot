
from mbrequest import *

# Bitcoin information class
class mbBitInfo:


    def lastPrice(self):
        
        quote = cached_api_request('ticker')

        if 'ticker' in quote:
            if 'last' in quote['ticker']:
                return quote['ticker']['last']

        return None

    
    def orderBook(self):

        pass


    def tradeList(self):

        pass
    
        



# Litecoin information class
class mbLiteInfo:
    
    pass
