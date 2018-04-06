import threading
import time
import hashlib
import hmac
import http.client
import json
import urllib.request, urllib.parse, urllib.error
import datetime
from collections import OrderedDict, deque
from decimal import Decimal
from .btprovider import *
import btools, settings
import btmodels

#Global variables
logger = btools.logger
trade_timestamp = deque()

# Constants
REQUEST_HOST = 'www.mercadobitcoin.net'
REQUEST_PATH = '/tapi/v3/'
HTTPCON_TIMEOUT = 60 # http connection timeout in secs
MAX_TRADE_COUNT = 60 # maximum number of trades within interval
MAX_TRADE_INTERVAL = 60 # interval in secs for maximum trade count
REQ_TRIALS = 10 # maximum number of trials for a request
REQ_INTERVAL = 60  # interval between successive trials
MB_STATUS_TABLE = {2: 'OPEN',
                   3: 'CANCELLED',
                   4: 'EXECUTED'}


class mbProvider(baseProvider):
    """ Mercado Bitcoin provider
    """

    def __init__(self):
        baseProvider.__init__(self)
        self.name = 'MBITCOIN'
        self.threads = []
        #self.funds_table = {}
        #self.update_funds()

    
    def execute_order(self, ordr):
        if not self.validate_order(ordr):
            logger.warning("Order " + str(ordr.oid) + " failed at provider "
                           + self.name)
            ordr.status='FAILED'
            ordr.save()
            return
        logger.info("Starting new thread to execute order " + str(ordr.oid))
        t = threading.Thread(target=execute_order_thread, args=[ordr])
        self.threads.append(t)
        t.start()
        

    def cancel_order(self, ordr):
        logger.info("Starting new thread to cancel order " + str(ordr.oid))
        t = threading.Thread(target=cancel_order_thread, args=[ordr])
        self.threads.append(t)
        t.start()

        
    def update_order(self, ordr):
        logger.info("Starting new thread to update order " + str(ordr.oid))
        t = threading.Thread(target=update_order_thread, args=[ordr])
        self.threads.append(t)
        t.start()


    def update_funds(self):
        logger.info("Starting new thread to update funds information")
        t = threading.Thread(target=update_funds_thread, args=[self])
        self.threads.append(t)
        t.start()


        
def execute_order_thread(ordr):
    
    tmethod = ''
    if ordr.otype == 'BUY':
        tmethod = 'place_buy_order'
    elif ordr.otype == 'SELL':
        tmethod = 'place_sell_order'
        
    params = {
        'tapi_method': tmethod,
        'tapi_nonce': get_nonce(),
        'coin_pair': ordr.currency + ordr.asset,
        'quantity': str(ordr.quantity),
        'limit_price': str(ordr.price)
    }

    resp = request_until_fail(params, REQ_TRIALS, REQ_INTERVAL)
    
    if validate_response(resp):
        logger.info("Order " + str(ordr.oid) + " sent for execution")
        if 'response_data' in resp:
            if 'order' in resp['response_data']:
                process_and_update(resp['response_data']['order'], ordr)
    else:
        logger.error("Execution of order " + str(ordr.oid) + " failed")
        ordr.status = 'FAILED'
        ordr.save()



def cancel_order_thread(ordr):

    rinfo = ordr.decode_remote_info()
    
    if 'order_id' not in rinfo:
        logger.error("Error canceling order " + str(ordr.oid)
                     + ": missing order_id in remote_info")
        return
        
    params = {
        'tapi_method': 'cancel_order',
        'tapi_nonce': get_nonce(),
        'coin_pair': ordr.currency + ordr.asset,
        'order_id': rinfo['order_id']
    }
    
    resp = request_until_fail(params, REQ_TRIALS, REQ_INTERVAL)

    if validate_response(resp):
        logger.info("Order " + str(ordr.oid) + " cancelled")
        if 'response_data' in resp:
            if 'order' in resp['response_data']:
                process_and_update(resp['response_data']['order'], ordr)
    else:
        logger.error("Order " + str(ordr.oid) + " not cancelled")        
                
                    
        
def update_order_thread(ordr):

    rinfo = ordr.decode_remote_info()
    
    if 'order_id' not in rinfo:
        logger.error("Error updating order " + str(ordr.oid)
                     + ": missing order_id in remote_info")
        return
    
    params = {
        'tapi_method': 'get_order',
        'tapi_nonce': get_nonce(),
        'coin_pair': ordr.currency + ordr.asset,
        'order_id': rinfo['order_id']
    }
    
    resp = request_until_fail(params, REQ_TRIALS, REQ_INTERVAL)

    if validate_response(resp):
        if 'response_data' in resp:
            if 'order' in resp['response_data']:
                process_and_update(resp['response_data']['order'], ordr)



def update_funds_thread(provider):
    
    params = {
        'tapi_method': 'get_account_info',
        'tapi_nonce': get_nonce()
    }

    ftable = provider.funds_table
    resp = request_until_fail(params, REQ_TRIALS, REQ_INTERVAL)

    if validate_response(resp):
        if 'response_data' in resp:
            if 'balance' in resp['response_data']:
                fund_dict = resp['response_data']['balance']
                for a, ainfo in fund_dict.items():
                    asset = a.upper()
                    if 'total' in ainfo and 'available' in ainfo:
                        ftable[asset] = btmodels.fundValues()
                        ftable[asset].total = Decimal(ainfo['total'])
                        ftable[asset].available = Decimal(ainfo['available'])
                        ftable[asset].tradable = Decimal(0)
                        ftable[asset].expected = Decimal(0)
    provider.recalculate_funds()
    logger.info("Funds recalculated for provider " + provider.name)

        
            
def get_nonce():
    new_nonce = int(time.time())
    if new_nonce <= get_nonce.last:
        new_nonce = get_nonce.last + 1
    get_nonce.last = new_nonce
    return str(new_nonce)
get_nonce.last = 0



def process_and_update(mbdata, ordr):
    
    if process_order_data(mbdata, ordr):
        ordr.save()
        logger.info("Order " + str(ordr.oid) + " updated")
    else:
        logger.warning("Order " + str(ordr.oid) + " not updated")

        
        
def process_order_data(mbdata, ordr):

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
    except Exception as e:
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

    eparams = urllib.parse.urlencode(params)
    
    # Gerar MAC
    params_string = REQUEST_PATH + '?' + eparams
    H = hmac.new(settings.MBTC_PARAMS['tapi_secret'], digestmod=hashlib.sha512)
    H.update(params_string)
    tapi_mac = H.hexdigest()

    # Create request header
    headers = {
        'Content-type': 'application/x-www-form-urlencoded',
        'TAPI-ID': settings.MBTC_PARAMS['tapi_id'],
        'TAPI-MAC': tapi_mac
    }

    logger.debug("Making tapi request to " + REQUEST_HOST + params_string)

    ret = None
    conn = None
    try:
        conn = http.client.HTTPSConnection(REQUEST_HOST, timeout=HTTPCON_TIMEOUT)
        conn.request('POST', REQUEST_PATH, eparams, headers)

        # Pre-process response
        resp = conn.getresponse()
        data = resp.read()
        
        # Utilizar a classe OrderedDict para preservar a ordem dos elementos
        response_json = json.loads(data, object_pairs_hook=OrderedDict)
        logger.debug("trade_request status: " + str(resp.status) + " " + str(resp.reason))
    except Exception as e:
        logger.error("Failed tapi request: " + str(e))
    else:
        ret = response_json
    finally:
        if conn:
            conn.close()
    return ret
