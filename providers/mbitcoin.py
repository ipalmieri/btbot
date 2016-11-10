# -*- coding: utf-8 -*-

import threading
import time
import hashlib
import hmac
import httplib
import json
import urllib
import datetime
from collections import OrderedDict, deque
from decimal import Decimal
from mainprov import *
import btools, settings

#Global variables
logger = btools.logger
trade_timestamp = deque()

# Constants
REQUEST_HOST = 'www.mercadobitcoin.net'
REQUEST_PATH = '/tapi/v3/'
HTTPCON_TIMEOUT = 60 # http connection timeout in secs
MAX_TRADE_COUNT = 60 # maximum number of trades within interval
MAX_TRADE_INTERVAL = 60 # interval in secs for maximum trade count
DEF_REQ_TRIALS = 10 # maximum number of trials for a request
DEF_REQ_INTERVAL = 60  # interval between successive trials
MB_STATUS_TABLE = {2: 'OPEN',
                   3: 'CANCELLED',
                   4: 'EXECUTED'}


class mbProvider(baseProvider):
    """ Mercado Bitcoin provider
    """

    def __init__(self):
        baseProvider.__init__(self)
        self.name = 'MBITCOIN'
        self.currency = 'BRL'
        self.req_trials = DEF_REQ_TRIALS
        self.req_interval = DEF_REQ_INTERVAL
        self.threads = []

        
    def validate_order(self, ordr):
        return True

    
    def execute_order(self, ordr):

        if not self.validate_order(ordr):
            return 

        tmethod = ''
        if ordr.otype == 'BUY':
            tmethod = 'place_buy_order'
        elif ordr.otype == 'SELL':
            tmethod = 'place_sell_order'

        params = {
            'tapi_method': tmethod,
            'tapi_nonce': get_nonce(),
            'coin_pair': 'BRL' + ordr.asset,
            'quantity': str(ordr.quantity),
            'limit_price': str(ordr.price)
        }

        logger.info("Starting new thread to execute order " + str(ordr.oid))
        t = threading.Thread(target=request_and_update,
                             args=[params, ordr,
                                   self.req_trials, self.req_interval])
        self.threads.append(t)
        t.start()
        

    def cancel_order(self, ordr):

        rinfo = ordr.decode_remote_info()

        if 'order_id' not in rinfo:
            logger.error("Error canceling order " + str(ordr.oid)
                         + ": missing order_id in remote_info")
            return
    
        params = {
            'tapi_method': 'cancel_order',
            'tapi_nonce': get_nonce(),
            'coin_pair': self.currency + ordr.asset,
            'order_id': rinfo['order_id']
        }

        logger.info("Starting new thread to cancel order " + str(ordr.oid))
        t = threading.Thread(target=request_and_update,
                             args=[params, ordr,
                                   self.req_trials, self.req_interval])
        self.threads.append(t)
        t.start()

        
    def update_order(self, ordr):

        rinfo = ordr.decode_remote_info()

        if 'order_id' not in rinfo:
            logger.error("Error updating order " + str(ordr.oid)
                         + ": missing order_id in remote_info")
            return
    
        params = {
            'tapi_method': 'get_order',
            'tapi_nonce': get_nonce(),
            'coin_pair': self.currency + ordr.asset,
            'order_id': rinfo['order_id']
        }

        logger.info("Starting new thread to update order " + str(ordr.oid))
        t = threading.Thread(target=request_and_update,
                             args=[params, ordr,
                                   self.req_trials, self.req_interval])
        self.threads.append(t)
        t.start()


            
def get_nonce():
    new_nonce = int(time.time())
    if new_nonce <= get_nonce.last:
        new_nonce = get_nonce.last + 1
    get_nonce.last = new_nonce
    return str(new_nonce)
get_nonce.last = 0



def request_and_update(params, ordr, trials, interval):
    
    resp = request_until_fail(params, trials, interval)
    updated = False
    if validate_response(resp):
        if 'response_data' in resp:
            if 'order' in resp['response_data']:
                if process_mb_order(resp['response_data']['order'], ordr):
                    ordr.save()
                    updated = True
    else:
        logger.error("Request failed")
        if ordr.status == 'ADDED':
            ordr.status = 'FAILED'
            ordr.save()
    if updated:
        logger.info("Order " + str(ordr.oid) + " updated")
    else:
        logger.warning("Order " + str(ordr.oid) + " not updated")
                    

        
def process_mb_order(mbdata, ordr):

    rinfo = ordr.decode_remote_info()

    if 'order_id' not in mbdata:
        logger.error(
            "process_mb_order(): data does not contain order information")
        return False

    if 'order_id' in rinfo:
        if rinfo['order_id'] != mbdata['order_id']:
            logger.error("Remote order_id does not match for order " +
                         str(ordr.oid) +
                         " Local: " + str(rinfo['order_id']) +
                         " Remote: " + str(mbdata['order_id']))
            return False

    # Read all relevant data
    try:
        status = mbdata['status']
        quantity = mbdata['quantity']
        price = mbdata['limit_price']
        exec_quantity = mbdata['executed_quantity']
        exec_price = mbdata['executed_price_avg']
        fees = mbdata['fee']
    except Exception, e:
        logger.error("Error reading order data: " + str(e))
        return False

    # Conversion and validation
    if status in MB_STATUS_TABLE:
        ordr.status = MB_STATUS_TABLE[status]
    else:
        logger.error("Invalid status code provided: " + str(status) +
                     " for order " + str(ordr.oid))

    ordr.exec_quantity = Decimal(exec_quantity)
    ordr.exec_price = Decimal(exec_price)
    ordr.fees = Decimal(fees)

    # Extra validation
    if ordr.price != Decimal(price):
        logger.warning("Order " + str(ordr.oid) + " price does not match:" +
                       " Local: " + str(ordr.price) +
                       " Remote: " + str(price))
    if ordr.quantity != Decimal(quantity):
        logger.warning("Order " + str(ordr.oid) + " quantity does not match:" +
                       " Local: " + str(ordr.quantity) +
                       " Remote: " + str(quantity))

    # Save remote information for reference
    ordr.encode_remote_info(mbdata)
    return True



def validate_response(resp):

    ret = False
    errormsg = "no error_message"
    
    if resp and 'status_code' in resp:
        if resp['status_code'] == 100:
            logger.debug("HTTP response validated")
            ret = True
        else:
            if 'error_message' in resp:
                errormsg = str(resp['status_code']) + " " + resp['error_message']
    if not ret:
        logger.warning("Invalid response: " + errormsg)
    return ret



def request_until_fail(params, trials, tstep):

    ret = None
    for i in range(0, trials):
        logger.debug("Request trial " + str(i+1) + "/" + str(trials))
        ret = delayed_trade_request(params)
        if ret is None:
            if i + 1 < trials:
                time.sleep(tstep)
        else:
            break
    return ret


    
def delayed_trade_request(params):
    # Update deque removing all expired timestamps
    while trade_timestamp:
        last_ts = trade_timestamp.popleft()
        dnow = datetime.datetime.utcnow()
        dt = (dnow - last_ts).total_seconds()

        if dt < MAX_TRADE_INTERVAL:
            if len(trade_timestamp) + 1 >= MAX_TRADE_COUNT:
                logger.debug("Sleeping till next possible trade")
                time.sleep(dt)
            else:
                trade_timestamp.appendleft(last_ts)
                break

    ret = trade_request(params)
    trade_timestamp.append(datetime.datetime.utcnow())
    
    return ret

    
    
def trade_request(params):

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

    logger.debug("Making tapi request to " + REQUEST_HOST + params_string)
    # Realizar requisição POST
    ret = None
    conn = None
    try:
        conn = httplib.HTTPSConnection(REQUEST_HOST, timeout=HTTPCON_TIMEOUT)
        conn.request("POST", REQUEST_PATH, eparams, headers)

        # Print response data to console
        response = conn.getresponse()
        response = response.read()
        
        # É fundamental utilizar a classe OrderedDict para preservar a ordem dos elementos
        response_json = json.loads(response, object_pairs_hook=OrderedDict)
        logger.debug("Response status: " + str(response_json['status_code']))
        #print "status: %s" % response_json['status_code']
        #print(json.dumps(response_json, indent=4))
    except Exception as e:
        logger.error("Failed tapi request: " + str(e))
    else:
        ret = response_json
    finally:
        if conn:
            conn.close()
    return ret
