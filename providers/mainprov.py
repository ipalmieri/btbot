from abc import ABCMeta, abstractmethod


class baseProvider:
    """ Base class for broker service providers
    """
    __metaclass__ = ABCMeta

    def __init__():
        self.ordmap = {}
    
    @abstractmethod
    def execute_order(self, ordr):
        pass

    @abstractmethod
    def cancel_order(self, ordr):
        pass
    
    @abstractmethod
    def update_order(self, ordr):
        pass



def reload_pending_orders(provdr):
    pass
