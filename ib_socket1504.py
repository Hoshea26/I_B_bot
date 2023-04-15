import time

from ibapi.wrapper import EWrapper
from ibapi.client import EClient
import pandas as pd
import datetime





class IBapi(EWrapper, EClient):

    def __init__(self):
        EClient.__init__(self,self)
        self.under_price = 0
        self.list_of_under_price = [1.0, 2.0, 3.0]
        self.entry_price = 0
        self.next_valid_id = []
        self.call_order_filled = True
        self.put_order_filled = True
        # self.call_option_data = pd.read_csv("csv_directory/call_option_data.csv")
        # self.executions_df = pd.DataFrame()
        # self.executions_df.columns = ["orderId", "time","right", "strike", "side", "price"]
        self.call_bid_prices = []
        self.max_call_bid = 0
        self.put_bid_prices = []
        self.max_put_bid = 0
        self.call_stl = 0
        self.put_stl = 0
        self.call_stl_triggered = False
        self.put_stl_triggered = False

    def tickPrice(self, reqId, tickType, price, attrib):
        super().tickPrice(reqId, tickType, price, attrib)

        if tickType == 4 and reqId == 1:
            self.under_price = price
            # with open("csv_directory/underlying_price.csv", mode="a") as f:
            #     f.write(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')},{str(price)}\n")


        # elif tickType == 4 and reqId == 2:
        #     print(f"Call Option Price : {price}")

        # elif tickType == 2 and reqId == 2:
            # print(f"CALL Option ASK : {price}")


        # elif tickType == 4 and reqId == 3:
        #     print(f"put Option Price : {price}")

        # elif tickType == 2 and reqId == 3:
            # print(f"PUT Option ASK : {price}")


        if tickType == 1 and reqId == 2:
            if self.call_order_filled == True:
                # print(f"CALL Option BID : {price}")
                self.call_bid_prices.append(price)
                self.max_call_bid_price(self.max_call_bid, self.call_bid_prices)
                self.call_stl = self.max_call_bid * 0.9
                # print(f"CALL STl: {self.call_stl}")
                if price != -1 and price != 0 \
                        and price < self.call_stl \
                        and self.call_bid_prices[-2] < self.call_stl \
                        and self.call_bid_prices[-3] < self.call_stl:

                    self.call_stl_triggered = True
                    print(f"CALL STL Triggered: {self.call_stl_triggered}")

            """adding the data to the csv"""
            # if price != -1:
            #     with open("csv_directory/call_bid_prices.csv", mode="a") as f:
            #         f.write(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')},{str(price)}")
            """end"""


        if tickType == 1 and reqId == 3:
            if self.put_order_filled == True:
                # print(f"PUT Option BID : {price}")
                self.put_bid_prices.append(price)
                # print(f"bid prices list:", self.call_bid_prices)
                self.max_put_bid_price(self.max_put_bid, self.put_bid_prices)
                self.put_stl = self.max_put_bid * 0.9
                # print(f"PUT STl: {self.put_stl}")
                if price != -1 and price != 0 \
                        and price < self.put_stl \
                        and self.put_bid_prices[-2] < self.put_stl \
                        and self.put_bid_prices[-3] < self.put_stl:

                    self.put_stl_triggered = True
                    print(f"PUT STL Triggered: {self.put_stl_triggered}")
            """adding the data to the csv"""
            # if price != -1:
            #     with open("csv_directory/put_bid_prices.csv", mode="a") as f:
            #         f.write(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')},{str(price)}\n")
            """end"""
            pass

    def is_call_stl_triggered(self):
        return bool(self.call_stl_triggered)

    def is_put_stl_triggered(self):
        return bool(self.put_stl_triggered)
    def max_call_bid_price(self, last_bid, list_of_bids):
        if last_bid < list_of_bids[-1]:
            self.max_call_bid = list_of_bids[-1]
        # print(f"Max Call Bid: {self.max_call_bid}")

    def max_put_bid_price(self, last_bid, list_of_bids):
        if last_bid < list_of_bids[-1]:
            self.max_put_bid = list_of_bids[-1]
        # print(f"Max put Bid: {self.max_put_bid}")

    def nextValidId(self, orderId):
        super().nextValidId(orderId)
        self.next_valid_id.append(orderId)
        print(f"SOCKET next valid id: {self.next_valid_id[-1]}")

    def return_next_valid_id(self):
        return self.next_valid_id[-1]


    def execDetails(self, reqId, contract, execution):
        super().execDetails(reqId, contract, execution)
        if execution.orderId != 0:
            # print(f"order ID: {execution.orderId} entry price: {execution.price}")
            # print(execution.__dict__)
            pass

    def return_entry_price(self):
        return self.entry_price

    def call_order_filled(self):
        self.call_order_filled = True

    def put_order_filled(self):
        self.put_order_filled = True

    def error(self, reqId, errorCode, errorString):
        print(errorCode)
        print(errorString)

    # def tickSize(self, reqId, tickType, size):
    #     super().tickSize(reqId, tickType, size)
    #     if reqId == 2 and tickType == 0:
    #         # print(f"CALL Option Bid Size : {size}")
    #         pass
