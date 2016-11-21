from abc import ABCMeta, abstractmethod
import btorder



class baseProvider:
    """ Base class for broker service providers
    """
    __metaclass__ = ABCMeta

    def __init__(self):
        self.name = ''
        self.currency = ''
        self.fundsTable = {}
        
    @abstractmethod
    def validate_order(self, ordr):
        pass
        
    @abstractmethod
    def execute_order(self, ordr):
        pass

    @abstractmethod
    def cancel_order(self, ordr):
        pass
    
    @abstractmethod
    def update_order(self, ordr):
        pass

    @abstractmethod
    def update_funds(self):
        pass

    def recalculate_funds(self):

        for asset, funds in self.fundsTable.iteritems():
            funds.tradable = funds.available
            funds.expected = funds.available
        

        added_list = btorder.order.get_by_status('ADDED')
        open_list = btorder.order.get_by_status('OPEN')

        ordr_list = added_list + open_list
        
        for ordr in ordr_list:
            if ordr.provider == self.name:
                asset_origin = self.currency
                asset_target = ordr.asset

                if asset_origin in self.fundsTable:
                    if asset_target in self.fundsTable:
                        forigin = fundsTable[asset_origin]
                        ftarget = fundsTable[asset_target]
                        qnt = ordr.quantity - ordr.exec_quantity
                        value = ordr.price*qnt

                        if ordr.otype == 'BUY':
                            forigin.tradable = forigin.tradable - value
                            forigin.expected = forigin.expected - value
                            ftarget.expected = ftarget.expected + qnt
                        elif ordr.otype == 'SELL':
                            ftarget.tradable = ftarget.tradable - qnt
                            ftarget.expected = ftarget.expected - qnt
                            forigin.expected = forigin.expected + value


    
class baseInfo:
    """ Base class for broker quote data
    """
    __metaclass__ = ABCMeta

    def __init__(self):
        self.name = ''
        self.currency = ''
        
    @abstractmethod
    def last_quote(self, asset):
        pass

