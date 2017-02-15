import btools
import providers
import ordermngr
logger = btools.logger

_providers_list = {}
_ordrmngr = None

def start_arena():
    """Starts all required objects"""
    logger.info("Starting bot arena")

    # Load available providers
    logger.info("Loading providers")
    _ordmngr = ordermngr.orderManager()
    for pcl in providers.prvclass_list:
        newpcl = pcl()
        _providers_list[newpcl.name] = newpcl
        _ordmngr.add_provider(newpcl)

    # Update orders information
    logger.info("Updating live orders")
    _ordmngr.reload_added_orders()
    _ordmngr.update_open_orders()
    
    # Recalculate current funds
    logger.info("Recalculating all funds")
    # update funds    


def add_bot(bot):
    pass

def stop_arena():

    # kill remaining requests/threads
    
    pass


class btArena:
    """Class to hold and host all strategies and bots
    """
    def __init(self):
        pass
    
    def start(self):
        pass

    def stop(self):
        pass


    
