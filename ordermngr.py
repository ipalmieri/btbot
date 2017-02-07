import collections
import btools, btorder


logger = btools.logger

manager = orderManager()

class orderManager():
    """Hub of orders to be sent to brokers
    Contains a queue of orders to be sent
    """

    def __init__(self):
        """Default constructor with empty structures"""
        self.main_queue = collections.deque()
        self.provider_hub = {}

        
    def add_provider(self, broker):
         """Adds broker to brokers dict"""
         self.provider_hub[broker.name] = broker
         logger.info("Provider " + broker.name + " added to hub")

         
    def add_order(self, order):
        """Adds order to queue, validating it before"""
        logger.info("Adding order to the queue for execution")
        isvalid = self._validate_new_order(order)
        if isvalid:
            order.status = 'ADDED'
            if order.add():
                self.main_queue.append(order)            
                logger.info("Order " + str(order.oid) + " added with success")
                return True
        logger.error("Error adding new order")
        order.status = 'FAILED'
        return False

    
    def reset_queue(self):
        """Clears the queue and updates orders status"""
        logger.info("Resetting order queue")
        for ordm in self.main_queue:
            ordm.status = 'CANCELLED'
            if not ordm.save():
                logger.error("Cannot cancel order "
                             + str(ordm.oid) + " on database")
        self.main_queue.clear()
            

    def send_next(self):
        """Pops queue and tries to send next order"""
        if len(self.main_queue) > 0:
            order = self.main_queue.popleft()
            if order.provider in self.provider_hub:
                self.provider_hub[order.provider].execute_order(order)
                return
            else:
                logger.error("Broker " + str(order.provider)
                             + " not available in the hub")
            logger.info("Restacking order " + str(order.oid) + " in main queue")
            self.main_queue.append(order)
        else:
            logger.debug("No order to send, empty queue")
            
            
    def flush_all(self):
        """Tries to send all orders in the current queue"""
        count = len(self.main_queue)
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
            if order.provider in provider_hub:
                # TODO criar nova thread para cancelar ordem
                provider_hub[order.provider].cancel_order(order)
            else:
                logger.error("No provider to cancel open order "
                             + str(order.oid))
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
                logger.error("Can't cancel order " + str(order.oid)
                             + ": " + str(e))


    def reload_added_orders(self):
        """Reloads all ADDED orders into queue"""
        if len(self.main_queue) > 0:
            logger.warning("Reloading non-empty order queue")
        orders = btorder.order.get_by_status('ADDED')
        if orders is not None:
            self.main_queue.clear()
            self.main_queue = collections.deque(orders)
            

            
    def _validate_new_order(self, order):
        """Indicates if order is valid and why not if it isn't"""
        isvalid = True
        logger.info("Validating new order")

        # Check: order must be recently created
        if order.status != 'CREATED':
            logger.error("Order being added is in state " + order.status)
            isvalid = False

        # Check: buy or sell order type
        if order.otype != 'SELL' and order.otype != 'BUY':
            logger.error("Order has invalid type: " + str(order.otype))
            isvalid = False

        # Check: provider exists
        if order.provider not in self.provider_hub:
            logger.warning("Provider " + order.provider + " is not available")
            #isvalid = False

        if not isvalid:
            logger.warning("Order " + str(order.oid) + " is invalid")
        return isvalid



    
