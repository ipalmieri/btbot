from abc import ABCMeta, abstractmethod
import btorder, btmodels



class baseProvider:
    """ Base class for broker service providers
    """
    __metaclass__ = ABCMeta

    def __init__(self):
        self.name = ''
        self.currency = ''
        self.funds_table = {}
        
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

    def get_funds(self, asset):
        """Returns the funds available of a given asset"""
        if asset in self.funds_table:
            return funds_table[asset]
        return btmodels.fundValues()

    
    def recalculate_funds(self):
        """Recalculate tradable and expected funds"""
        for asset, funds in self.funds_table.iteritems():
            funds.tradable = funds.available
            funds.expected = funds.available
        added_list = btorder.order.get_by_status('ADDED')
        for ordr in added_list:
            if ordr.provider == self.name:
                asset_origin = self.currency
                asset_target = ordr.asset
                if asset_origin in self.funds_table:
                    if asset_target in self.funds_table:
                        forigin = self.funds_table[asset_origin]
                        ftarget = self.funds_table[asset_target]
                        qnt = ordr.quantity
                        value = ordr.price*qnt
                        if ordr.otype == 'BUY':
                            forigin.tradable = forigin.tradable - value
                            forigin.expected = forigin.expected - value
                            ftarget.expected = ftarget.expected + qnt
                        elif ordr.otype == 'SELL':
                            ftarget.tradable = ftarget.tradable - qnt
                            ftarget.expected = ftarget.expected - qnt
                            forigin.expected = forigin.expected + value
        open_list = btorder.order.get_by_status('OPEN')
        for ordr in open_list:
            if ordr.provider == self.name:
                asset_origin = self.currency
                asset_target = ordr.asset
                if asset_origin in self.funds_table:
                    if asset_target in self.funds_table:
                        forigin = self.funds_table[asset_origin]
                        ftarget = self.funds_table[asset_target]
                        qnt = ordr.quantity - ordr.exec_quantity
                        value = ordr.price*qnt
                        if ordr.otype == 'BUY':
                             ftarget.expected = ftarget.expected + qnt
                        elif ordr.otype == 'SELL':
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

