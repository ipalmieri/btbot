from abc import ABCMeta, abstractmethod
import asyncio
import queue
import threading
import janus
import time
import settings
from . import btools

CONNECT_RETRY_SLEEP = 5
logger = btools.logger
    
class RpcChannel(metaclass=ABCMeta):
    """Base class for interprocess communication"""
    @abstractmethod
    def start():
        pass

    @abstractmethod
    def stop():
        pass

    @abstractmethod
    def send(self, msg):
        pass

    @abstractmethod
    def recv(self):
        pass


class AsyncClientProtocol(asyncio.Protocol):
    def __init__(self, rpc_channel):
        self.transport = None
        self.rpc_channel = rpc_channel
        self.send_loop_future = None

    def connection_made(self, transport):
        self.transport = transport
        self.send_loop_future = self.rpc_channel.aioloop.create_task( \
                                    self.send_loop())

    def data_received(self, data):
        msg = data.decode()
        self.rpc_channel.aioloop.create_task( \
                self.rpc_channel.inqueue.async_q.put(msg))

    def connection_lost(self, exc):
        logger.info("Connection lost: " + str(exc))
        self.send_loop_future.cancel()
        self.rpc_channel.connected.clear()
        if self.rpc_channel.started.is_set():
            asyncio.ensure_future(self.rpc_channel._connect(), 
                                  loop=self.rpc_channel.aioloop)

    async def send_loop(self):
        while self.rpc_channel.started.is_set():
            try:
                msg = await self.rpc_channel.ouqueue.async_q.get()
                data = msg.encode()
                self.transport.write(data)
            except Exception as e:
                logger.warning("Send loop failed: " + str(e))
                

class RpcAsyncClient(RpcChannel):
    """RPC Channel based on asyncio TCP client"""
    connect_retry_sleep = CONNECT_RETRY_SLEEP
    
    def __init__(self, hostname, port):
        self.servername = hostname
        self.serverport = port
        self.started = threading.Event()
        self.connected = threading.Event()
        self.started.clear()
        self.connected.clear()
        self.locthread = None
        self.aioloop = None
        self.inqueue = None
        self.ouqueue = None

    async def _connect(self):
        logger.info("Starting connection loop to " + self.servername + \
                    ":" + str(self.serverport))
        while not self.connected.is_set():
            try:
                con_coro = await self.aioloop.create_connection(
                                lambda: AsyncClientProtocol(self),
                                self.servername,
                                self.serverport)
            except OSError as e:
                logger.warning("Error connecting: " + str(e))
                logger.warning("Reconnecting in " + \
                               str(self.connect_retry_sleep) + " seconds")
                await asyncio.sleep(self.connect_retry_sleep)
            else:
                self.connected.set()
                logger.info("Connected successfully")
     
    def local_start(self):
       self.aioloop.run_until_complete(self._connect())
       self.aioloop.run_forever()

    def start(self):
        if self.started.is_set():
            logger.warning("Tried to start a channel that is already started")
            return
        self.started.set()
        self.aioloop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.aioloop)
        self.inqueue = janus.Queue(loop=self.aioloop)
        self.ouqueue = janus.Queue(loop=self.aioloop)
        self.locthread = threading.Thread(target=self.local_start) 
        #self.locthread.daemon = True 
        self.locthread.start()

    def stop(self):
        if not self.started.is_set():
            logger.warning("Tried to stop a channel that is already stopped")
            return
        logger.debug("Stopping RPC channel")    
        self.started.clear()
        self.connected.clear()
        self.aioloop.call_soon_threadsafe(self.aioloop.stop)
        self.locthread.join()
        self.inqueue = None
        self.ouqueue = None
        self.locthread = None
        self.aioloop = None

    def send(self, msg):
        if not self.started.is_set():
            logger.error("Channel is not started, cannot send message")
            return False    
        try:
            self.ouqueue.sync_q.put_nowait(msg)
        except Exception as e:
            logger.error("Error pushing message to queue: " + str(e))
            return False
        return True     

    def recv(self):
        if not self.started.is_set():
            logger.error("Channel is not started, cannot receive message")
            return None    
        try:
            msg = self.inqueue.sync_q.get_nowait()
        except Exception as e:
            #logger.debug("Error popping message from queue:" + str(e))
            return None
        else:
            return msg
        return None    


