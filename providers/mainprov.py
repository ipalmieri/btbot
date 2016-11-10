from abc import ABCMeta, abstractmethod
import btorder

class baseProvider:
    """ Base class for broker service providers
    """
    __metaclass__ = ABCMeta

    def __init__(self):
        self.name = ''
        self.currency = ''
        
    @abstractmethod
    def execute_order(self, ordr):
        pass

    @abstractmethod
    def cancel_order(self, ordr):
        pass
    
    @abstractmethod
    def update_order(self, ordr):
        pass

    @abstractmethod
    def validate_order(self, ordr):
        pass
    
