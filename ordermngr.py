import btools
import btorder
import collections

logger = btools.logging.getLogger("btbot")

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
        self.live_orders = []
        
    def add_broker(self, name, broker):
        """Adds broker to brokers dict"""
        self.broker_hub[name] = broker

    def add_order(self, order):
        """Adds order to queue, validating it before"""
        logger.info("Adding order to the queue for execution")
        isvalid, msg = validate_order(order)
        if isvalid:
            main_queue.append(order)
            # TODO change status and save to db
            logger.info("Order added with success")
            return True
        else:
            logger.warning("Invalid order: " + msg + " order: " + order.code)
            
        return False

    def reset_queue(self):
        """Clears the queue and update orders status"""
        logger.info("Resetting order queue")
        # TODO update status of all orders as deleted and save
        self.main_queue.clear()

    def send_next(self):
        """Pops queue and tries to send next order"""
        if len(main_queue) > 0:
            order = self.main_queue.popleft()
            provider = order.provider

            if provider in broker_hub:
                # TODO Criar nova thread para enviar ordem
                # ver se foi ok, se nao, nao voltar
                return
            else:
                logger.error("Broker " + provider + " not available in the hub.")

            logger.warning("Restacking order in main queue")
            main_queue.append(order)

    def flush_all(self):
        """Tries to send all orders in the current queue"""
        count = len(main_queue)
        for i in range(0, count):
            self.sendNext()
        pass

    def cancel_order(self, ordernum):
        # have to search everywhere
        pass

    def get_order(self, ordernum):
        pass
