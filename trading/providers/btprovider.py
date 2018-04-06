from abc import ABCMeta, abstractmethod
import btorder, btools
import btmodels

logger = btools.logger


class baseProvider(metaclass=ABCMeta):
    """ Base class for broker service providers
    """

    def __init__(self):
        self.name = ''
        self.funds_table = {}

        
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

    
    def validate_order(self, ordr):
        """Returns True if order is expected to succeed"""
        is_valid = True
        # Check: provider has needed funds
        if ordr.otype == 'SELL':
            asset_needed = ordr.asset
            funds_needed = ordr.quantity
        else:
            asset_needed = ordr.currency
            funds_needed = ordr.price * ordr.quantity
        funds_tradable = self.get_funds(asset_needed).tradable
        if ordr.asset not in self.funds_table:
            logger.warning("Asset " + ordr.asset + " not available at provider")
            is_valid = False
        if ordr.currency not in self.funds_table:
            logger.warning("Currency " + ordr.currency +
                           " not available at provider")
            is_valid = False
        if funds_needed > funds_tradable:
            logger.warning("Provider doesn't have funds for order")
            is_valid = False
        if not is_valid:
            logger.warning("Order " + str(ordr.oid) +
                           " is not valid at provider" + ordr.provider)
        return is_valid

    
    
    def get_funds(self, asset):
        """Returns the funds available of a given asset"""
        if asset in self.funds_table:
            return self.funds_table[asset]
        return btmodels.fundValues()

    
    def recalculate_funds(self):
        """Recalculate tradable and expected funds"""
        for asset, funds in self.funds_table.items():
            funds.tradable = funds.available
            funds.expected = funds.available
        added_list = btorder.order.get_by_status('ADDED')
        for ordr in added_list:
            if ordr.provider == self.name:
                asset_origin = ordr.currency
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
                asset_origin = ordr.currency
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

    
class baseInfo(metaclass=ABCMeta):
    """ Base class for broker quote data
    """

    def __init__(self):
        self.name = ''
        self.currency = ''
        
    @abstractmethod
    def last_quote(self, asset):
        pass

