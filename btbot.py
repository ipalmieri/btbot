from ordermngr import *
import btools

logger = btools.logger

def main():

    btools.init_logging()
    
    logger.info("teste info")
    logger.warning("teste warn")
    logger.error("teste error")
    logger.debug("teste debug")

    bt = orderManager()

    btools.engine.connect().execute("SELECT 1")
    
if __name__ == '__main__':
    main()
