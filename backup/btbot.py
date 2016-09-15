#!/usr/local/bin/python2.7

import sys
import httplib
import urllib
import json
import time
import datetime
import hashlib
import hmac

#para debugar
#import pdb
#pdb.set_trace()
import random

#tirar isso daqui
mercado_tapi_chave = 'd8417bd0c0349ee530cc991e517aa1fc'
mercado_tapi_codigo = '70a0add15f2f60ea91f4e5f536195377de289f6610f3cc5b360a4996102cb5f7'
PIN = '0000'

pairLocal = 'btc_brl'
nameLocal = 'btc'
command_ticker = 'ticker'
command_book = 'orderbook'
command_trades = 'trades'

targetURL = "www.mercadobitcoin.com.br"

api_cache = {}
last_req_api = None 
last_req_trade = None

par_cost = 0.007
par_min_qnt = 0.01

logDir = "./logs"
logFile = "bitbot.log"
tstep = 0

min_dt_trade = 40
min_dt_api = 60

orderList = {}

def log(bt, msg):

	logAll("ID: " + str(bt.ident) + "    " + msg)
	
	pass
	

def logAll(msg):

	f = open(logDir + "/" + logFile, 'a')
	f.write(str(datetime.datetime.now()) + " " + msg + "\n")
	f.close()
	
	pass
	


class btParam:
	
	def __init__(self, quantity = 0.0, price = 0.0):
		self.qnt = float(quantity) 
		self.price = float(price)	


class btOrder:

	ident = '0000'
	qnt = 0.0
	money = 0.0
	cost = 0.0
	status = "new"	
	otype = ""
	bt = None
	target = btParam()


class btConfig:

	sell_margin = 0.004
	buy_margin = 0.004
	keep_ratio = 0.0
	keep_money = 0.00
	buy_timeout = 20.0
	sell_timeout = 60.0
	stop_loss = 0.5
	stop_gain = 5.0
	delta_loss = 0.0001


class btBot:
	
	config = btConfig()
	balance = btParam()
	money = 0.0	
	state = "SHORT"
	sellTarget = btParam()
	buyTarget = btParam()
	time = datetime.datetime.now()
	min_money = 0.0
	max_money = 0.0
	ident = 0
	order = 0








def processOrder(oid, order):

	if oid in orderList.keys():

		delta_qnt = 0.0
		delta_money = 0.0
		delta_cost = 0.0

		lorder = orderList[oid]

		if not len(order) > 0 and not 'operations' in order.keys(): return

		for oper in order['operations']:
		
			volume = float(order['operations'][oper]['volume'])
			price = float(order['operations'][oper]['price'])
			rate = float(order['operations'][oper]['rate'])/100.0

			if lorder.otype == 'buy':
				
				delta_qnt = delta_qnt + volume*(1.0 - rate)
				delta_money = delta_money - volume*price
				delta_cost = volume*rate*price

			elif lorder.otype == 'sell':

				delta_qnt = delta_qnt - volume
				delta_money = delta_money + volume*(1.0 - rate)*price
				delta_cost = volume*rate*price
	
		lorder.qnt = delta_qnt
		lorder.money = delta_money
		lorder.cost = delta_cost
		
		#melhorar aqui
		avgprice = lorder.target.price		

		bot = lorder.bt
		bot.balance = calcBalance(bot.balance, btParam(lorder.qnt, avgprice))
		bot.money = bot.money + lorder.money

		lorder.status = order['status']

	else:
		logAll("processOrder(): Ordem invalida " + oid)	
	

	pass



def addOrder(order):

	if order.ident in orderList.keys():

		log(order.bt, "addOrder(): Erro adicionando ordem")		
	else:

		orderList[order.ident] = order

	pass




def putOrder(bt, ortype, target):


	if ortype == "BID": 
		torder = 'buy'
		bt.buyTarget = target
		
	elif ortype == "ASK":
		torder = 'sell'
		bt.sellTarget = target

	else:
		return False


	# parametros. Coloque os demais parametros para outros metodos quando necessario.
	params = {
		'method': 'Trade',
		'tonce' : str(int(time.time())),
		'pair' : pairLocal,
		'type' : torder,	
		'volume': str(abs(float(target.qnt))),
		'price': str(target.price)
	 }

	resp = tradeRequest(params)
	
	if resp['success'] == 1:
	
		nid = resp['return'].keys()[0]
		norder = resp['return'][nid]
	
		order = btOrder()
		order.ident = str(nid)
		order.qnt = 0.0
		order.money = 0.0
		order.status = norder['status']
		order.otype = torder
		order.bt = bt
		order.target = target
		
		bt.order = order.ident

		msg = "++++ PUT ID: " + str(bt.order) + " " + torder
		msg = msg + " " + str(target.qnt) + " " + str(target.price)
		log(bt, msg)	

		addOrder(order)
		


		return True
	else:
	
		logAll("putOrder(): " + resp['error'])
		

	return False

	pass





def cancelOrder(oid):

	if int(oid) <= 0: return False

	params = {
		'method': 'CancelOrder',
		'tonce' : str(int(time.time())),
		'pair' : pairLocal,
		'order_id' : str(oid)
	 }

	resp = tradeRequest(params)
	
	if resp['success'] == 1:
	
		msg = "---- CANCEL ID: " + str(oid) 
		log(orderList[oid].bt, msg)
	
		order = getOrder(oid)
		processOrder(oid, order)
		orderList[oid].bt.order = '0000'

		return True
	else:

		logAll("cancelOrder(): " + resp['error'])


	return False

	pass


def getOrder(oid):

	ret = {}

	params = {
		'method': 'OrderList',
		'tonce' : str(int(time.time())),
		'pair' : pairLocal
	 }

	resp = tradeRequest(params)
	
	if resp['success'] == 1:
	
		if str(oid) in resp['return'].keys():

			ret = resp['return'][str(oid)]
						
	else:
		logAll("getOrder(): " + resp['error'])


	return ret

	pass
	


def checkOrder(oid):

	order = getOrder(oid)

	if len(order) > 0:
	
		if order['status'] == 'completed': 

			processOrder(oid, order)
						
			return True

	return False

	pass

	



def resetBuyOrder(bt):

	#cancel old order
	if cancelOrder(bt.order):
		changeState(bt, "SHORT")
	else:
		changeState(bt, "DEAD")

	pass
	

def resetSellOrder(bt):

	if cancelOrder(bt.order):
		changeState(bt, "LONG")
	else:
		changeState(bt, "DEAD")

	pass



def checkBid(bt):

	ckorder = checkOrder(bt.order)

	dnow = datetime.datetime.now()
	dt = (dnow - bt.time).total_seconds()

	if ckorder:

		changeState(bt, "LONG")


	elif dt >= bt.config.buy_timeout*60:
		
		resetBuyOrder(bt)

	pass



	
def checkAsk(bt):

	ckorder = checkOrder(bt.order)

	dnow = datetime.datetime.now()
	dt = (dnow - bt.time).total_seconds()

	if ckorder:

		changeState(bt, "SHORT")

	elif dt >= bt.config.sell_timeout*60:
		
		resetSellOrder(bt)


	pass



def calcBalance(balance, delta):
 
	ret = btParam()

	ret.qnt = balance.qnt + delta.qnt
	
	if ret.qnt > 0:
		if delta.qnt > 0:
			ret.price = (balance.qnt*balance.price + delta.qnt*delta.price)/ret.qnt
		else:
			ret.price = balance.price
	else:
		ret.price = 0.0
	
	return ret



def clampTarget(target):

	params = {
		'method': 'getInfo',
		'tonce' : str(int(time.time())),
	 }

	resp = tradeRequest(params)
	
	if resp['success'] == 1:
	
		max_money = resp['return']['funds']['brl']
		max_qnt =  resp['return']['funds'][nameLocal]

		if target.qnt > 0.0:			

			if target.qnt*target.price >= max_money:

				target.qnt = max_money*(1.0 - keep_money)/target.price
		else:

			if -target.qnt > max_qnt:
			
				target.qnt = -max_qnt*(1.0 - keep_ratio) 
			

	else:
		logAll("clampTarget(): " + resp['error'])

	pass
	
	


def setSellTarget(balance, money, btconf):

	ret = btParam()

	lquote = apiRequest(command_ticker)
	baseline_price = balance.price 
	floor_price = lquote['ticker']['buy'] 
	peer_price = lquote['ticker']['sell']

	markup = par_cost + btconf.sell_margin
	target_price = baseline_price*(1.0 + markup)

	#parametrizar isso aqui
	#if target_price < peer_price:
	#	target_price = (target_price + peer_price)/2.0 


	price = max(floor_price, target_price)

	ret.price = price
	ret.qnt = -balance.qnt*(1.0 - btconf.keep_ratio)	
	


	clampTarget(ret)

	return ret





def setBuyTarget(balance, money, btconf):

	ret = btParam()

	lquote = apiRequest(command_ticker)
        baseline_price = lquote['ticker']['last']  
	ceil_price = lquote['ticker']['sell']
	peer_price = lquote['ticker']['buy']
	
	


	markdown = par_cost + btconf.buy_margin
	target_price = baseline_price*(1.0 - markdown)

	#parametrizar isso aqui
	#if target_price > peer_price:
	#	target_price = (target_price + peer_price)/2.0


	price = min(ceil_price, target_price)

	ret.price = price
	ret.qnt = (1.0 - btconf.keep_money)*money/ret.price 

	clampTarget(ret)

	return ret



def changeState(bt, state):

	bt.time = datetime.datetime.now()
	bt.state = state


	msg = str(bt.state) + "  $:" + str(bt.money) 
	msg = msg + "  M:" + str(bt.balance.qnt) + "  P:" + str(bt.balance.price)

 	log(bt, msg)




def orderBid(bt):

	if(bt.min_money > 0 and bt.money < bt.min_money): 
		
		changeState(bt, "DEAD")

	elif(bt.max_money > 0 and bt.money > bt.max_money):

		changeState(bt, "DEAD")

	else:

		target = setBuyTarget(bt.balance, bt.money, bt.config)

		if putOrder(bt, "BID", target): 
			changeState(bt, "BID")
	
		 
def orderAsk(bt):

	target = setSellTarget(bt.balance, bt.money, bt.config)

	if putOrder(bt, "ASK", target):	
		changeState(bt, "ASK")





def initBot(bt, money):

	bt.money = money
	bt.max_money = bt.config.stop_gain*money
	bt.min_money = bt.config.stop_loss*money
	bt.ident = 1

	log(bt, "Started")

	changeState(bt, "SHORT")



def clearOrders(bt):

	cleared = False

	log(bt, "Clearing Orders...")

	while not cleared:
		
		cleared = True

		for i in orderList:
		
			if orderList[i].status == 'active' and orderList[i].bt.ident == bt.ident:

				cleared = cleared and cancelOrder(i)
		


	log(bt, "Clearing Done.")




def resetBot(bt):


	clearOrders(bt)

	if bt.balance.qnt > par_min_qnt:	
		changeState(bt, "LONG")
	
	elif bt.money > bt.min_money:	
		changeState(bt, "SHORT")		
	




def main_loop():

	bt = btBot()
	initBot(bt, float(sys.argv[1]))

	while True:

		if bt.state == "SHORT":
					
			orderBid(bt)	
			
		elif bt.state == "BID":

			checkBid(bt)

		elif bt.state == "LONG":

			orderAsk(bt)

		elif bt.state == "ASK":

			checkAsk(bt)

		elif bt.state == "DEAD":

			resetBot(bt)

		else:
			print "Invalid state. Exiting"
			exit()
		

		time.sleep(tstep)


def apiRequest(command):

	global last_req_api
	global api_cache

	if last_req_api is not None:
		dnow = datetime.datetime.now()
		dt = (dnow - last_req_api).total_seconds()

		if dt < min_dt_api:
			if command in api_cache:
				return api_cache[command]
			else:
				time.sleep(max(0, min_dt_api - dt))

	last_req_api = datetime.datetime.now()





        conn = httplib.HTTPConnection(targetURL)
        conn.request("GET", "/api/" + command + "/")

        dnow = datetime.datetime.now()

        response = conn.getresponse()

        ret = json.load(response)
	
	#print response.status, response.reason
	if response.status != 200 or len(ret) == 0:
		logAll("Erro no apiRequest()")

	conn.close()

	api_cache[command] = ret

	return ret
	



def tradeRequest(parlist):

	global last_req_trade

	if last_req_trade is not None:
		dnow = datetime.datetime.now()
		dt = (dnow - last_req_trade).total_seconds()
		time.sleep(max(0, min_dt_trade - dt))

	parlist['tonce'] = str(int(time.time()))
	last_req_trade = datetime.datetime.now()





	params = urllib.urlencode(parlist)
	# criando a assinatura
	H = hmac.new(mercado_tapi_codigo, digestmod=hashlib.sha512)
	H.update(parlist['method'] + ':' + PIN + ':' + parlist['tonce'])
	sign = H.hexdigest()

	#cria o cabecalho
	headers = {"Content-type": "application/x-www-form-urlencoded",
	   "Key":mercado_tapi_chave,
	   "Sign":sign}

	#realiza a chamada
	conn = httplib.HTTPSConnection(targetURL)
	conn.request("POST", "/tapi/", params, headers)

	#mostra resultado
	response = conn.getresponse()
	
	ret = json.load(response)

	#print response.status, response.reason
	if response.status != 200 or len(ret) == 0:
		logAll("Erro no tradeRequest()")

	conn.close()

	return ret





if __name__ == '__main__':

	if len(sys.argv) != 2:
		print "Uso: " + sys.argv[0] + " [money]" 	
	else:
		PIN = str(input("Digite seu PIN:"))
		main_loop()

