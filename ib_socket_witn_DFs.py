import time
from ibapi.wrapper import EWrapper
from ibapi.client import EClient
from datetime import datetime
import pandas as pd
STL_MARGIN = 0.8
class IBapi(EWrapper, EClient):

    def __init__(self):
        EClient.__init__(self, self)
        self.under_price = 0
        self.entry_price = 0
        self.next_valid_id = []
        self.call_order_filled = True
        self.put_order_filled = True
        self.call_bid_prices = []
        self.max_call_bid = 0
        self.put_bid_prices = []
        self.max_put_bid = 0
        self.call_stl = 0
        self.put_stl = 0
        self.call_stl_triggered = False
        self.put_stl_triggered = False
        self.executions = pd.DataFrame()
        self.underlying_price_df = pd.DataFrame(columns=["time", "price"])
        self.call_bid_df = pd.DataFrame(columns=["time", "price"])
        self.call_bid_stl_df = pd.DataFrame(columns=["time", "max bid", "stl"])
        self.put_bid_df = pd.DataFrame(columns=["time", "price"])
        self.put_bid_stl_df = pd.DataFrame(columns=["time", "max bid", "stl"])
        self.put_bid_hist_df = pd.DataFrame(columns=["time", "open", "high", "low", "close"])

    def tickPrice(self, reqId, tickType, price, attrib):
        super().tickPrice(reqId, tickType, price, attrib)

        """underlying price"""
        if tickType == 4 and reqId == 1:
            self.under_price = price
            # print(f"underlying price: {price}")
            if price != -1:
                self.append_price(datetime.now().strftime("%H:%M:%S"), price, "underlying")

        """call option bids"""
        if tickType == 1 and reqId == 2:
            if price != -1:
                self.append_price(datetime.now().strftime("%H:%M:%S"), price, "call")
                self.append_stl(datetime.now().strftime("%H:%M:%S"), self.call_bid_df["price"].max(), "call")
            if self.call_order_filled:
                # print(f"CALL Option BID : {price}")
                self.call_bid_prices.append(price)
                self.update_max_call_bid(price)
                self.call_stl = self.max_call_bid * STL_MARGIN
                # print(f"CALL STl: {self.call_stl}")
                if self.is_stl_triggered(price, self.call_stl, self.call_bid_prices):
                    self.call_stl_triggered = True
                    print(f"CALL STL Triggered: {self.call_stl_triggered}")

        """put option bids"""
        if tickType == 1 and reqId == 3:
            if price != -1:
                self.append_price(datetime.now().strftime("%H:%M:%S"), price, "put")
                self.append_stl(datetime.now().strftime("%H:%M:%S"), self.put_bid_df["price"].max(), "put")
            if self.put_order_filled:
                print(f"PUT Option BID : {price}")
                self.put_bid_prices.append(price)
                self.update_max_put_bid(price)
                self.put_stl = self.max_put_bid * STL_MARGIN
                print(f"PUT STl: {self.put_stl}")
                if self.is_stl_triggered(price, self.put_stl, self.put_bid_prices):
                    self.put_stl_triggered = True
                    print(f"PUT STL Triggered: {self.put_stl_triggered}")

    def is_stl_triggered(self, price, stl, bid_prices):
        return price != -1 and price != 0 and price < stl \
               and bid_prices[-2] < stl and bid_prices[-3] < stl

    def is_call_stl_triggered(self):
        return bool(self.call_stl_triggered)

    def is_put_stl_triggered(self):
        return bool(self.put_stl_triggered)

    def update_max_call_bid(self, price):
        if self.max_call_bid < price:
            self.max_call_bid = price

    def update_max_put_bid(self, price):
        if self.max_put_bid < price:
            self.max_put_bid = price

    def nextValidId(self, orderId):
        super().nextValidId(orderId)
        self.next_valid_id.append(orderId)
        print(f"SOCKET next valid id: {self.next_valid_id[-1]}")

    def return_next_valid_id(self):
        return self.next_valid_id[-1]

    def execDetails(self, reqId, contract, execution):
        super().execDetails(reqId, contract, execution)
        # print(f"EXECUTION DETAILS: {execution.__dict__}")
        new_row = {'clientId': execution.clientId, 'orderId': execution.orderId,'right': contract.right,
                   'strike' : contract.strike,'side': execution.side, 'price':execution.price,
                   'avgPrice': execution.avgPrice}
        df = pd.DataFrame.from_dict(new_row, orient='index', columns=[execution.time]).T
        self.executions = self.executions._append(df)
        # print(self.executions)

    def return_entry_price(self):
        return self.entry_price

    def call_order_filled(self):
        self.call_order_filled = True

    def put_order_filled(self):
        self.put_order_filled = True
    def return_price(self):
        return self.under_price

    def reset_stl(self):
        self.call_bid_prices = []
        self.max_call_bid = 0
        self.put_bid_prices = []
        self.max_put_bid = 0
        self.call_stl = 0
        self.put_stl = 0
        self.call_stl_triggered = False
        self.put_stl_triggered = False

    def append_price(self, time, price, asset_type):
        new_row = {
            "time": time,
            "price": price,
        }
        if asset_type == "underlying":
            self.underlying_price_df = self.underlying_price_df._append(new_row, ignore_index=True)
        if asset_type == "call":
            self.call_bid_df = self.call_bid_df._append(new_row, ignore_index=True)
        if asset_type == "put":
            self.put_bid_df = self.put_bid_df._append(new_row, ignore_index=True)

    def append_stl(self, time, max_price, asset_type):
        stl = max_price * STL_MARGIN

        new_row = {
            "time": time,
            "stl": stl
        }
        if asset_type == "call":
            self.call_bid_stl_df = self.call_bid_stl_df._append(new_row, ignore_index=True)
        if asset_type == "put":
            self.put_bid_stl_df = self.put_bid_stl_df._append(new_row, ignore_index=True)

    def error(self, reqId, errorCode, errorString):
        print(errorCode)
        print(errorString)
##########################################################################



# import time
# from ibapi.wrapper import EWrapper
# from ibapi.client import EClient
# import pandas as pd
# import datetime
#
# class IBapi(EWrapper, EClient):
#
#     def __init__(self):
#         EClient.__init__(self,self)
#         self.under_price = 0
#         self.list_of_under_price = [1.0, 2.0, 3.0]
#         self.entry_price = 0
#         self.next_valid_id = []
#         self.call_order_filled = True
#         self.put_order_filled = True
#         # self.call_option_data = pd.read_csv("csv_directory/call_option_data.csv")
#         # self.executions_df = pd.DataFrame()
#         # self.executions_df.columns = ["orderId", "time","right", "strike", "side", "price"]
#         self.call_bid_prices = []
#         self.max_call_bid = 0
#         self.put_bid_prices = []
#         self.max_put_bid = 0
#         self.call_stl = 0
#         self.put_stl = 0
#         self.call_stl_triggered = False
#         self.put_stl_triggered = False
#
#     def tickPrice(self, reqId, tickType, price, attrib):
#         super().tickPrice(reqId, tickType, price, attrib)
#
#         if tickType == 4 and reqId == 1:
#             self.under_price = price
#             # with open("csv_directory/underlying_price.csv", mode="a") as f:
#             #     f.write(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')},{str(price)}\n")
#
#         # elif tickType == 4 and reqId == 2:
#         #     print(f"Call Option Price : {price}")
#
#         # elif tickType == 2 and reqId == 2:
#             # print(f"CALL Option ASK : {price}")
#
#
#         # elif tickType == 4 and reqId == 3:
#         #     print(f"put Option Price : {price}")
#
#         # elif tickType == 2 and reqId == 3:
#             # print(f"PUT Option ASK : {price}")
#
#
#         if tickType == 1 and reqId == 2:
#             if self.call_order_filled == True:
#                 # print(f"CALL Option BID : {price}")
#                 self.call_bid_prices.append(price)
#                 self.max_call_bid_price(self.max_call_bid, self.call_bid_prices)
#                 self.call_stl = self.max_call_bid * 0.98
#                 # print(f"CALL STl: {self.call_stl}")
#                 if price != -1 and price != 0 \
#                         and price < self.call_stl \
#                         and self.call_bid_prices[-2] < self.call_stl \
#                         and self.call_bid_prices[-3] < self.call_stl:
#
#                     self.call_stl_triggered = True
#                     print(f"CALL STL Triggered: {self.call_stl_triggered}")
#
#             """adding the data to the csv"""
#             # if price != -1:
#             #     with open("csv_directory/call_bid_prices.csv", mode="a") as f:
#             #         f.write(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')},{str(price)}")
#             """end"""
#
#
#         if tickType == 1 and reqId == 3:
#             if self.put_order_filled == True:
#                 print(f"PUT Option BID : {price}")
#                 self.put_bid_prices.append(price)
#                 # print(f"bid prices list:", self.call_bid_prices)
#                 self.max_put_bid_price(self.max_put_bid, self.put_bid_prices)
#                 self.put_stl = self.max_put_bid * 0.98
#                 print(f"PUT STl: {self.put_stl}")
#                 if price != -1 and price != 0 \
#                         and price < self.put_stl \
#                         and self.put_bid_prices[-2] < self.put_stl \
#                         and self.put_bid_prices[-3] < self.put_stl:
#
#                     self.put_stl_triggered = True
#                     print(f"PUT STL Triggered: {self.put_stl_triggered}")
#             """adding the data to the csv"""
#             # if price != -1:
#             #     with open("csv_directory/put_bid_prices.csv", mode="a") as f:
#             #         f.write(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')},{str(price)}\n")
#             """end"""
#             pass
#
#     def is_call_stl_triggered(self):
#         return bool(self.call_stl_triggered)
#
#     def is_put_stl_triggered(self):
#         return bool(self.put_stl_triggered)
#     def max_call_bid_price(self, last_bid, list_of_bids):
#         if last_bid < list_of_bids[-1]:
#             self.max_call_bid = list_of_bids[-1]
#         # print(f"Max Call Bid: {self.max_call_bid}")
#
#     def max_put_bid_price(self, last_bid, list_of_bids):
#         if last_bid < list_of_bids[-1]:
#             self.max_put_bid = list_of_bids[-1]
#         # print(f"Max put Bid: {self.max_put_bid}")
#
#     def nextValidId(self, orderId):
#         super().nextValidId(orderId)
#         self.next_valid_id.append(orderId)
#         print(f"SOCKET next valid id: {self.next_valid_id[-1]}")
#
#     def return_next_valid_id(self):
#         return self.next_valid_id[-1]
#
#
#     def execDetails(self, reqId, contract, execution):
#         super().execDetails(reqId, contract, execution)
#         if execution.orderId != 0:
#             # print(f"order ID: {execution.orderId} entry price: {execution.price}")
#             # print(execution.__dict__)
#             pass
#
#     def return_entry_price(self):
#         return self.entry_price
#
#     def call_order_filled(self):
#         self.call_order_filled = True
#
#     def put_order_filled(self):
#         self.put_order_filled = True
#
#     def return_price(self):
#         return self.under_price
#     def error(self, reqId, errorCode, errorString):
#         print(errorCode)
#         print(errorString)
#
#     # def tickSize(self, reqId, tickType, size):
#     #     super().tickSize(reqId, tickType, size)
#     #     if reqId == 2 and tickType == 0:
#     #         # print(f"CALL Option Bid Size : {size}")
#     #         pass
#
