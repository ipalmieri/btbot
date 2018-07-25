from base import *
import time

logger = btools.logger

def main():

    btools.init_logging()
    #dbcon.init_db()

    logger.error("Log test")

    rpt = rpcchannel.RpcAsyncClient("localhost", 6666)

    rpt.send("test send")

    rpt.start()

    time.sleep(2)
    rpt.send("test")

    time.sleep(20)
 
    while True:
        msg = rpt.recv()
        if msg is None:
            break;
        else:
            logger.debug(msg)

    rpt.stop()

if __name__ == '__main__':
    main()
