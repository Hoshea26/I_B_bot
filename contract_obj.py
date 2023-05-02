from ibapi.client import EClient
from ibapi.wrapper import Contract

class UnderlyingContract():
    def __init__(self):
        self.contract = Contract()
        self.contract.symbol = "MES"
        self.contract.secType = "FUT"
        self.contract.exchange = "CME"
        self.contract.currency = "USD"
        self.contract.lastTradeDateOrContractMonth = "202306"  # Change this to the desired expiration date

class OptionContract():
    def __init__(self, option_e_date, strike, right):
        self.contract = Contract()
        self.contract.symbol = "MES"
        self.contract.secType = "FOP"
        self.contract.exchange = "CME"
        self.contract.currency = "USD"
        self.contract.lastTradeDateOrContractMonth = option_e_date
        self.contract.strike = strike
        self.contract.right = right
        self.contract.multiplier = 5

