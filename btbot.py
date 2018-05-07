from base import *
import time

logger = btools.logger

def main():

    btools.init_logging()
    #dbcon.init_db()

    logger.error("Log test")

    rpt = rpcagent.RpcProxy(None)

    rpt.send("")

    rpt.start()

    time.sleep(10)

    rpt.stop()

if __name__ == '__main__':
    main()
