import httplib
import urllib
import json
import datetime
from collections import OrderedDict
import btools
from btprovider import *

REQUEST_HOST = 'www.mercadobitcoin.net'
REQUEST_PATH = '/api/v2/'  # v2 = last 24h | v1 = since past midnight

logger = btools.logger
api_cache = {}
api_last_req = None
api_min_dt = 30


class mbInfo(baseInfo):
    """ Mercado Bitcoin data provider
    """

    def __init__(self):
        baseInfo.__init__(self)
        self.name = 'MBITCOIN'
        self.currency = 'BRL'


    def last_price(self, asset):
        pass
        

    
def cached_info_request(command):

    global api_cache
    global api_last_req
    global api_min_dt
    
    if api_last_req is not None:

        dnow = datetime.datetime.now()
        dt = (dnow - api_last_req).total_seconds()

        if dt < api_min_dt:
            if command in api_cache:
                return api_cache[command]

    ret = info_request(command)

    if len(ret) > 0:
        api_last_req = datetime.datetime.now()
        api_cache[command] = ret
    
    return ret
           
            

# Returns a dict containing the web API response
def info_request(command):

    ret = None
    conn = None
    try:
        conn = httplib.HTTPSConnection(REQUEST_HOST)
        conn.request('GET', REQUEST_PATH + command + '/')
        
        # Pre-process response
        resp = conn.getresponse()
        data = resp.read()
        
        # E' fundamental utilizar a classe OrderedDict para preservar a ordem dos elementos
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
    

