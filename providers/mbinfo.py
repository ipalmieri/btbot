import httplib
import urllib
import json
import datetime
from collections import OrderedDict
import btools
from btprovider import *
from btmodels import dataQuote

# Global variables
logger = btools.logger
api_cache = {}
api_last_req = None
api_min_dt = 30

# Constants
REQUEST_HOST = 'www.mercadobitcoin.net'
REQUEST_PATH = '/api/'  # /api/v2/ = last 24h | /api/v1/ = since past midnight
HTTPCON_TIMEOUT = 60 # http connection timeout in secs


class mbInfo(baseInfo):
    """ Mercado Bitcoin data provider
    """

    def __init__(self):
        baseInfo.__init__(self)
        self.name = 'MBITCOIN'
        self.currency = 'BRL'


    def last_quote(self, asset):

        tcmd = ""
        if asset == 'BTC':
            tcmd = 'trades'
        elif asset == 'LTC':
            tcmd = 'trades_litecoin'
        else:
            logger.error("Invalid asset " + str(asset))
            return None

        ilist = cached_info_request(tcmd)
        
        if len(ilist) > 0:
            if 'date' in ilist[0] and 'price' in ilist[0]:
                rdate = datetime.datetime.fromtimestamp(ilist[0]['date'])
                rprice = ilist[0]['price']
                return dataQuote(rdate, rprice)
        logger.error("Error reading info response")
        return None


    def trade_list(self, asset, maxlen=1):

        ret = []
        
        if asset == 'BTC':
            tcmd = 'trades'
        elif asset == 'LTC':
            tcmd = 'trades_litecoin'
        else:
            logger.error("Invalid asset " + str(asset))
            return ret

        ilist = cached_info_request(tcmd)

        count = 0
        for l in ilist:
            if len(ret) >= maxlen:
                break

            if 'date' in l and 'price' in l:
                rdate = datetime.datetime.fromtimestamp(l['date'])
                rprice = l['price']
                ret.append(dataQuote(rdate, rprice))
            
        if len(ret) != maxlen:
            logger.warning("Returning " + str(len(ret)) + "/" + str(maxlen)
                           + " points")
        return ret


        
    
def cached_info_request(command):

    global api_cache
    global api_last_req
    global api_min_dt
    
    if api_last_req is not None:

        dnow = datetime.datetime.now()
        dt = (dnow - api_last_req).total_seconds()
        
        if dt < api_min_dt:
            if command in api_cache:
                logger.debug("Cached info request with command \'" + command + "\'")
                return api_cache[command]


    ret = info_request(command)
    
    if ret:
        api_last_req = datetime.datetime.now()
        api_cache[command] = ret
    
    return ret
           
            

# Returns a dict containing the web API response
def info_request(command):

    logger.debug("Making api request to " + REQUEST_HOST + REQUEST_PATH + command + '/')

    ret = None
    conn = None
    try:
        conn = httplib.HTTPSConnection(REQUEST_HOST, timeout=HTTPCON_TIMEOUT)
        conn.request('GET', REQUEST_PATH + command + '/')
        
        # Pre-process response
        resp = conn.getresponse()
        data = resp.read()

        # Utilizar a classe OrderedDict para preservar a ordem dos elementos
        response_json = json.loads(data, object_pairs_hook=OrderedDict)
        logger.debug("info_request status: " + str(resp.status) + " " + str(resp.reason))
    except Exception as e:
        logger.error("Failed api request: " + str(e))
    else:
        ret = response_json
    finally:
        if conn:
            conn.close()
    return ret
    

