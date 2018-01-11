from abc import ABCMeta, abstractmethod


class rpcServer:
    """Base class for RPC between btbot actors"""
    
    __metaclass__ = ABCMeta

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    

class rcpClient:
    """Base class of RPC client connection"""
    __metaclass__ = ABCMeta

    @abstractmethod
    def is_ready(self):
        pass

    @abstractmethod
    def call(self, fuction, args):
        pass

    





