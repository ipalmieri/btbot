from abc import ABCMeta, abstractmethod

class RPCChannel(metaclass=ABCMeta):
    """Base class for socket communication"""

    @abstractmethod
    def send(self, msg):
        pass

    @abstractmethod
    def recv(self):
        pass


class RPCAgent(metaclass=ABCMeta):
    """Base class for RPC between btbot actors"""
    self.rproxy = None

    __init__(self, port):
        self.rproxy = RPCProxy(port)

    @abstractmethod
    def start(self):
        pass
    
    @abstractmethod
    def stop(self):
        pass

    
class RPCProxy(metaclass=ABCMeta):

    self.inqueue = None
    self.ouqueue = None
    self.port = 0

    __init__(self, port):

    @abstractmethod
    def is_ready(self):
        pass

    @abstractmethod
    def send(self, msg):
        pass

    @abstractmethod
    def recv(self):
        pass
    

            

