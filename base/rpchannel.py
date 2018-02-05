from abc import ABCMeta, abstractmethod
import zmq

TCP_DEFPORT=9999

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

    

class zmqServer(rpcServer):
    """ZeroMQ pull-push server"""
    self.port = TCP_DEFPORT
    self.addr = '0.0.0.0'
    def __init__(self, addr, port = TCP_DEFPORT):
        self.addr = addr
        self.port = port


    def start():
        context = zmq.Context()
        zmq_socket = context.socket(zmq.PUSH)
        zmq_socket.bind("tcp://127.0.0.1:5557")
        # Start your result manager and workers before you start your producers
        for num in xrange(20000):
            work_message = { 'num' : num }
            zmq_socket.send_json(work_message)
            

