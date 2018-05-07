from abc import ABCMeta, abstractmethod
import queue
import threading
from . import btools
import settings
import time

logger = btools.logger
RPC_TIMEOUT = 10.0  # Thread join timeout in seconds
RPC_LTIME = 1.0     # RPC send/receive loop time


class RpcAgent():
    """RPC agent class, server and client communication"""
    
    def __init__(self, port):
        self.rproxy = RpcProxy(None)

    def start(self):
        pass
    
    def stop(self):
        pass

    
class RpcProxy():
    """Manages send and receipt of RPC messages"""

    def __init__(self, channel):
        self.inqueue = queue.Queue()
        self.ouqueue = queue.Queue()
        self.channel = channel
        self.send_thread = None
        self.recv_thread = None
        self.started = threading.Event() 
        self.started.clear()

    def start(self):
        if self.started.is_set():
            logger.warning("Tried to start RPC proxy that is already started")
        if not self.channel:
            logger.error("Set a channel before starting RPC proxy")
            return
        logger.debug("Starting RPC Proxy threads")
        self.started.set()
        self.send_thread = threading.Thread(target=self.send_loop)
        self.recv_thread = threading.Thread(target=self.recv_loop)
        self.send_thread.start()
        self.recv_thread.start()

    def stop(self):
        if not self.started.is_set():
            logger.warning("Tried to stop a RPC proxy that is already stopped")
            return
        logger.debug("Stopping RPC Proxy threads")
        self.started.clear()
        self.send_thread.join(RPC_TIMEOUT)
        if self.send_thread.is_alive():
            logger.error("RPC Proxy send thread still alive")
        self.recv_thread.join(RPC_TIMEOUT)
        if self.recv_thread.is_alive():
            logger.error("RPC Proxy receive thread still alive")

    def send_loop(self):
        while self.started.is_set():
            try:
                msg = self.ouqueue.get(True, RPC_LTIME)
            except Exception as e:
                pass
            else:
                if not self.channel.send(msg):
                    logger.debug("Failed to send message on channel")
                    if not self.send(msg):
                        logger.error("Cannot push message back to send")

    def recv_loop(self):
        while self.started.is_set():
            msg = self.channel.recv()
            if msg:
                try:
                    self.inqueue.put(msg, False)
                except Exception as e:
                    logger.debug("Cannot push message to receive queue: " + 
                                 str(e))

    def send(self, msg):
        logger.debug("Pushing message to send queue")
        try:
            self.ouqueue.put(msg, False)
        except Exception as e:
            logger.info("Cannot push message on send queue: " + str(e))
            return False
        else:
            return True

    def recv(self):
        logger.debug("Popping message from receive queue")
        msg = None
        try:
            msg = self.inqueue.get(False)
        except Exception as e:
            logger.debug("Cannot pop message on receive queue: " + str(e))
        return msg
    

            

class RpcChannel(metaclass=ABCMeta):
    """Base class for socket communication"""

    @abstractmethod
    def send(self, msg):
        pass

    @abstractmethod
    def recv(self):
        pass

class TcpChannel(RpcChannel):
    pass


