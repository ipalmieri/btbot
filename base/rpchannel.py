from abc import ABCMeta, abstractmethod

TCP_DEFPORT=9999

class rpcServer(metaclass=ABCMeta):
    """Base class for RPC between btbot actors"""

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    

class rcpClient(metaclass=ABCMeta):
    """Base class of RPC client connection"""

    @abstractmethod
    def is_ready(self):
        pass

    @abstractmethod
    def call(self, fuction, args):
        pass

    

            

