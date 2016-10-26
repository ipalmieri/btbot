# -*- coding: utf-8 -*-

import hashlib
import hmac
import httplib
import json
import urllib
from collections import OrderedDict
from mainprov import *
import btools, settings

logger = btools.logger

# Constantes
REQUEST_HOST = 'www.mercadobitcoin.net'
REQUEST_PATH = '/tapi/v3/'

class mbProvider():
    """ Mercado Bitcoin provider
    """
    
    def execute_order(self, ordr):
        pass

    def cancel_order(self, ordr):
        pass

    def update_order(self, ordr):
        pass
    

    
def trade_request(params):

    ret = None
    eparams = urllib.urlencode(params)
    
    # Gerar MAC
    params_string = REQUEST_PATH + '?' + eparams
    H = hmac.new(settings.MBTC_PARAMS['tapi_secret'], digestmod=hashlib.sha512)
    H.update(params_string)
    tapi_mac = H.hexdigest()

    # Gerar cabeçalho da requisição
    headers = {
        'Content-type': 'application/x-www-form-urlencoded',
        'TAPI-ID': settings.MBTC_PARAMS['tapi_id'],
        'TAPI-MAC': tapi_mac
    }

    # Realizar requisição POST
    try:
        conn = httplib.HTTPSConnection(REQUEST_HOST)
        conn.request("POST", REQUEST_PATH, eparams, headers)

        # Print response data to console
        response = conn.getresponse()
        response = response.read()
        
        # É fundamental utilizar a classe OrderedDict para preservar a ordem dos elementos
        response_json = json.loads(response, object_pairs_hook=OrderedDict)
        #print "status: %s" % response_json['status_code']
        #print(json.dumps(response_json, indent=4))
    except Exception as e:
        logger.error("Error sending tapi request: " + str(e))
    else:
        ret = response_json
    finally:
        if conn:
            conn.close()
    return ret
