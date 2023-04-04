import time

from ibapi.wrapper import EWrapper
from ibapi.client import EClient





class IBapi(EWrapper, EClient):

    def __init__(self):
        EClient.__init__(self,self)
        self.under_price = 0
        self.entry_price = 0
        self.nextvalidid = 0
        self.is_parent_order_filled = False
        self.call_bid_prices = []
        self.max_call_bid = 0
        self.call_stl = 0
        self.stl_triggered = False

    def tickPrice(self, reqId, tickType, price, attrib):
        super().tickPrice(reqId, tickType, price, attrib)
        # if reqId == 2:
        #     # print(f"TickType: {tickType}, Price: {price}")

        if tickType == 4 and reqId == 1:
            self.under_price = price
            # print(f"Under Lynig Price : {self.under_price}")

        # elif tickType == 4 and reqId == 2:
        #     print(f"Call Option Price : {price}")

        elif tickType == 2 and reqId == 2:
            # print(f"CALL Option ASK : {price}")
            pass

        # elif tickType == 4 and reqId == 3:
        #     print(f"put Option Price : {price}")

        elif tickType == 2 and reqId == 3:
            # print(f"PUT Option ASK : {price}")
            pass

        if tickType == 1 and reqId == 2:
            print(f"CALL Option BID : {price}")
            self.call_bid_prices.append(price)
            # print(f"bid prices list:", self.call_bid_prices)
            self.max_bid_price(self.max_call_bid, self.call_bid_prices)
            self.call_stl = self.max_call_bid * 0.8
            print(f"CALL STl: {self.call_stl}")
            if price != -1 and price != 0 and price < self.call_stl \
                    and self.call_bid_prices[-2] < self.call_stl \
                    and self.call_bid_prices[-3] < self.call_stl \
                    and self.isFilled() == True:
                self.stl_triggered = True
                print(f"STL Triggered: {self.stl_triggered}")

    def return_stl_triggered(self):
        return self.stl_triggered

    def max_bid_price(self, last_bid, list_of_bid):
        if last_bid < list_of_bid[-1]:
            self.max_call_bid = list_of_bid[-1]
        print(f"Max Call Bid: {self.max_call_bid}")

    def tickSize(self, reqId, tickType, size):
        super().tickSize(reqId, tickType, size)
        if reqId == 2 and tickType == 0:
            # print(f"CALL Option Bid Size : {size}")
            pass



    def nextValidId(self, orderId):
        super().nextValidId(orderId)
        self.nextvalidid = orderId

    def return_nextvalidid(self):
        return self.nextvalidid

    # def position(self, account, contract, position, avgCost):
    #     super().position(account, contract, position, avgCost)
    #     # if position != 0:
    #     print(f"Number of positions: {position}")
    #     if position != 0:
    #         print(f"Position: {contract.right} ")
    #         print(f"          {contract.strike}")

    def execDetails(self, reqId, contract, execution):
        super().execDetails(reqId, contract, execution)
        if execution.orderId != 0:
            print(f"oreder ID: {execution.orderId} entry price: {execution.price}")
    #     self.entry_price = execution.price
    #     print(f"VAR print : ############## :{self.entry_price}")

    def orderStatus(self, orderId, status, filled, remaining, avgFillPrice, permId,
                    parentId, lastFillPrice, clientId, whyHeld, mktCapPrice ):
        if orderId == self.return_nextvalidid() and avgFillPrice != 0.0 :
            self.entry_price = avgFillPrice
        if status == "Filled":
            self.is_parent_order_filled = True
        if avgFillPrice != 0.0 :
            # print(f"orderId : {orderId}")
            # print(f"entry price : {avgFillPrice}")
            # print(f"status : {status}")
            pass
    def return_entry_price(self):
        return self.entry_price

    def isFilled(self):
        return self.is_parent_order_filled

    def order_filled(self):
        self.is_parent_order_filled = True

    def error(self, reqId, errorCode, errorString):
        print(errorCode)
        print(errorString)
