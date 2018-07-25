from abc import ABCMeta, abstractmethod
import settings
from . import rpcchannel
from . import btools

logger = btools.logger


class RpcAgent(metaclass=ABCMeta):
    """RPC agent class, server and client communication"""
    
    def __init__(self):
        self.rchannel = None

    @abstractmethod
    def start(self):
        pass
    
    @abstractmethod
    def stop(self):
        pass

    
            





