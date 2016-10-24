import btools
import collections
import btdata

logger = btools.logger
        

def validate_order(order):
    """Indicates if order is valid and why not if it isn't"""
    return True, ""


class orderManager():
    """Hub of orders to be sent to brokers
    Contains a queue of orders to be sent
    """

    def __init__(self):
        """Default constructor with empty structures"""
        self.main_queue = collections.deque()
        self.broker_hub = {}
        self.open_orders = []

        
    def add_broker(self, name, broker):
        """Adds broker to brokers dict"""
        self.broker_hub[name] = broker

        
    def add_order(self, order):
        """Adds order to queue, validating it before"""
        logger.info("Adding order to the queue for execution")
        if order.status != 'CREATED':
            logger.warning("Order " + str(order.oid) + " is in state " +
                           order.status + " and was not added")
            return False
        isvalid, msg = validate_order(order)
        if isvalid:
            order.status = 'ADDED'
            if order.save():
                self.main_queue.append(order)            
                logger.info("Order " + str(order.oid) + " added with success")
                return True
            else:
                logger.error("Error adding new order: " + str(e))
                order.status = 'CREATED'
        else:
            logger.warning("Order " + str(order.oid) + " is invalid: " + msg)
        return False

    
    def reset_queue(self):
        """Clears the queue and update orders status"""
        logger.info("Resetting order queue")
        for ordm in self.main_queue:
            ordm.status = 'CANCELLED'
            if not orderm.save():
                logger.error("Cannot cancel order " + str(ordm.oid) + " on database")
        self.main_queue.clear()
            

    def send_next(self):
        """Pops queue and tries to send next order"""
        if len(main_queue) > 0:
            order = self.main_queue.popleft()
            if order.provider in broker_hub:
                # TODO Criar nova thread para enviar ordem
                broker_hub[order.provider].execute_order(order)
                return
            else:
                logger.error("Broker " + order.provider + " not available in the hub")
            logger.warning("Restacking order " + str(order.oid) + " in main queue")
            main_queue.append(order)
        else:
            logger.info("No order to send, empty queue")
            
            
    def flush_all(self):
        """Tries to send all orders in the current queue"""
        count = len(main_queue)
        for i in range(0, count):
            self.send_next()

    
    def cancel_order(self, order):
        """Cancels order in queue and in provider"""
        logger.info("Cancelling order " + str(order.oid))
        if order.status != 'ADDED' and order.staus != 'OPEN':
            logger.warning("Order " + str(order.oid) + " not OPEN or ADDED")
            return 
        if order.status == 'OPEN':
            # If already open, let the broker cancel it
            if order.provider in broker_hub:
                # TODO criar nova thread para cancelar ordem
                broker_hub[order.provider].cancel_order(order)
            else:
                logger.error("No provider to cancel open order " + str(order.oid))
        else:
            last_status = order.status
            order.status = 'CANCELLED'
            if order.save():
                for ordm in self.main_queue:
                    if ordm.oid == oid:
                        self.main_queue.remove(ordm)
                        break
                logger.info("Order " + str(order.oid) + " cancelled")
            else:
                order.status = last_status
                logger.error("Can't cancel order " + str(order.oid) + ": " + str(e))


    def reload_added_orders(self):
        """Reloads all ADDED orders into queue"""
        if len(self.main_queue) > 0:
            logger.warning("Reloading non-empty order queue")

        orders = btdata.order.get_by_status('ADDED')

        if orders is not None:
            self.main_queue.clear()
            self.main_queue = collections.deque(orders)
            
        

    
