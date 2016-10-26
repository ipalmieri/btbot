import httplib
import urllib
import json
import datetime

from tools import *


target_url = "www.mercadobitcoin.net"
#target_ver = "v2"  # v2 = last 24h | v1 = since past midnight
api_cache = {}
api_last_req = None
api_min_dt = 30

# Returns a cached copy of the response if timeout hasn't expired
def cached_api_request(command):

    global api_cache
    global api_last_req
    global api_min_dt
    
    if api_last_req is not None:

        dnow = datetime.datetime.now()
        dt = (dnow - api_last_req).total_seconds()

        if dt < api_min_dt:
            if command in api_cache:
                return api_cache[command]

    ret = api_request(command)

    if len(ret) > 0:
        api_last_req = datetime.datetime.now()
        api_cache[command] = ret
    
    return ret
           
            

# Returns a dict containing the web API response
def api_request(command):

    ret = {}
    conn = httplib.HTTPSConnection(target_url)


    try:
        conn.request("GET", "/api/" + command + "/")
    except Exception as e:
        logMsg("ERROR api_request(): " + str(e))
    else:
        response = conn.getresponse()
    
        if response.status != 200:
            logMsg("ERROR api_request(): " + str(response.status) + " " + response.reason)
        else:
            try:
                ret = json.load(response)
            except ValueError as e:
                logMsg("ERROR api_request(): " + str(e))
    
    conn.close()

    return ret
    

