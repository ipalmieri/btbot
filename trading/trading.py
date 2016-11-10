from abc import ABCMeta, abstractmethod


class baseTrader:
    """Base class for any trading bot
    """
    __metaclass__ = ABCMeta

    def __init__(self):
        self.name = ''
        
    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def serialize(self):
        pass

    @abstractmethod
    def deserialize(self, data):
        pass
