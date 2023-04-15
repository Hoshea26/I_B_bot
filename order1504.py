import threading
from ibapi.execution import ExecutionFilter
from data_manager import Bot
from ibapi.order import Order
import time
import math
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

"""the order classes"""
class EntryOrder():
    def __init__(self):
        self.entry_order = Order()
        self.entry_order.orderType = "BOX TOP"
        self.entry_order.action = "BUY"
        self.entry_order.totalQuantity = 1
        self.entry_order.eTradeOnly = False
        self.entry_order.firmQuoteOnly = False

class ExitOrder():
    def __init__(self):
        self.exit_order = Order()
        self.exit_order.orderType = "BOX TOP"
        self.exit_order.action = "SELL"
        self.exit_order.totalQuantity = 1
        self.exit_order.eTradeOnly = False
        self.exit_order.firmQuoteOnly = False


"""the main logic of the strategy"""
"""(the main module)"""
bot = Bot()
time.sleep(1)
# CALL_ORDER_ID = bot.ib.return_next_valid_id()
# print(f"CALL_ORDER_ID : {CALL_ORDER_ID}")
# PUT_ORDER_ID = CALL_ORDER_ID + 1
# print(f"PUT_ORDER_ID : {PUT_ORDER_ID}")
# CALL_SUN_ID = PUT_ORDER_ID + 1
# print(f"CALL_SUN_ID : {CALL_SUN_ID}")
# PUT_SUN_ID = CALL_SUN_ID + 1
# print(f"PUT_SUN_ID : {PUT_SUN_ID}")

entry_order = EntryOrder()
exit_order = ExitOrder()

"""placing the call entry order"""
CALL_ORDER_ID = bot.ib.return_next_valid_id()
print(f"CALL_ORDER_ID : {CALL_ORDER_ID}")
bot.ib.placeOrder(CALL_ORDER_ID, bot.call_contract.contract, entry_order.entry_order)
print("CALL ORDER WAS PLACED")

"""requesting the next valid order ID and placing the 
   put entry order"""

PUT_ORDER_ID = CALL_ORDER_ID + 1
print(f"PUT_ORDER_ID : {PUT_ORDER_ID}")
bot.ib.placeOrder(PUT_ORDER_ID, bot.put_contract.contract, entry_order.entry_order)
print("PUT ORDER WAS PLACED")


"""req execution section"""
# ef = ExecutionFilter()
# ef.secType = "FOP"
# bot.ib.reqExecutions(1,ef)
"""END req execution section"""

"""section 1 suppose to be here"""

# """
# two function that suppose to work in the background
# and check if the STL was triggered
# """
# def exit_call():
#     while True:
#         c_is_true = bot.ib.is_call_stl_triggered()
#         if c_is_true == True:
#             print(f"EXIT EXIT EXIT ! CALL ! EXIT EXIT EXIT")
#             bot.ib.placeOrder(PUT_SUN_ID, bot.o_m_d_c.contract, exit_order.exit_order)
#             break
#
# def exit_put():
#     while True:
#         p_is_true = bot.ib.is_put_stl_triggered()
#         if p_is_true == True:
#             print(f"EXIT EXIT EXIT ! PUT ! EXIT EXIT EXIT")
#             bot.ib.placeOrder(CALL_SUN_ID, bot.o_m_d_p.contract, exit_order.exit_order)
#             break
#
# time.sleep(1)
# put_exit = threading.Thread(target=exit_put(),daemon=True)
# put_exit.start()
# call_exit = threading.Thread(target=exit_call(),daemon=True)
# call_exit.start()
call_count = 0
put_count = 0
CALL_SUN_ID = 0
PUT_SUN_ID = 0
while True:
    c_is_true = bot.ib.is_call_stl_triggered()
    p_is_true = bot.ib.is_put_stl_triggered()
    if c_is_true == True and call_count == 0:
        if put_count == 0:
            CALL_SUN_ID = PUT_ORDER_ID + 1
            print(f"EXIT CALL order ID {CALL_SUN_ID}")
            bot.ib.placeOrder(CALL_SUN_ID, bot.call_contract.contract, exit_order.exit_order)
            print("CALL EXIT ORDER WAS PLACED")
        elif put_count == 1:
            CALL_SUN_ID = PUT_SUN_ID + 1
            print(f"EXIT CALL order ID {CALL_SUN_ID}")
            bot.ib.placeOrder(CALL_SUN_ID, bot.call_contract.contract, exit_order.exit_order)
            print("CALL EXIT ORDER WAS PLACED")
        call_count = 1

    if p_is_true == True and put_count == 0:
        if call_count == 0:
            PUT_SUN_ID = PUT_ORDER_ID + 1
            print(f"EXIT PUT order ID {PUT_SUN_ID}")
            bot.ib.placeOrder(PUT_SUN_ID, bot.put_contract.contract, exit_order.exit_order)
            print("PUT EXIT ORDER WAS PLACED")
        elif call_count == 1:
            PUT_SUN_ID = CALL_SUN_ID + 1
            print(f"EXIT PUT order ID {PUT_SUN_ID}")
            bot.ib.placeOrder(PUT_SUN_ID, bot.put_contract.contract, exit_order.exit_order)
            print("PUT EXIT ORDER WAS PLACED")
        put_count = 1

    if c_is_true == True and p_is_true == True:
        break


"""live dashboard code"""
# def animate_underlying_price(i):
#     data = pd.read_csv("csv_directory/underlying_price.csv")
#     x_values = data["time"]
#     y_values = data["price"]
#     plt.cla()
#     plt.plot(x_values, y_values, label="MES price")
#     plt.legend(loc="upper left")
#     plt.tight_layout()
#
# underlying_price_animation = FuncAnimation(plt.gcf(), animate_underlying_price, interval=500)
# plt.tight_layout()
# plt.show()
#
# def animate_call_bid_price(i):
#     data = pd.read_csv("csv_directory/call_bid_prices.csv")
#     x_values = data["time"]
#     y_values = data["bid price"]
#     plt.cla()
#     plt.plot(x_values, y_values, label="call best bid")
#     plt.legend(loc="upper left")
#     plt.tight_layout()
#
# call_bids_animation = FuncAnimation(plt.gcf(), animate_call_bid_price, interval=500)
# plt.tight_layout()
# plt.show()


# def animate_put_bid_price(i):
#     data = pd.read_csv("csv_directory/put_bid_prices.csv")
#     x_values = data["time"]
#     y_values = data["bid price"]
#     plt.cla()
#     plt.plot(x_values, y_values, label="put best bid")
#     plt.legend(loc="upper left")
#     plt.tight_layout()
#
#
# put_bids_animation = FuncAnimation(plt.gcf(), animate_put_bid_price, interval=500)
# plt.tight_layout()
# plt.show()



"""
checking if the BUY orders were filled (section 1)
"""
##req executions to check if orders are filled
# ef = ExecutionFilter()
# ef.secType = "FOP"
# bot.ib.reqExecutions(1, ef)
# if bot.ib.executions_df.empty == False:
#     if bot.ib.executions_df.loc[-1] == CALL_ORDER_ID:
#         bot.ib.call_order_filled()
#     elif bot.ib.executions_df.loc[-2] == CALL_ORDER_ID:
#         bot.ib.call_order_filled()
#     if bot.ib.executions_df.loc[0, "orderId"] == PUT_ORDER_ID:
#         bot.ib.put_order_filled()
#     elif bot.ib.executions_df.loc[1, "orderId"] == PUT_ORDER_ID:
#         bot.ib.put_order_filled()
# print("*************************************")
# print(bot.ib.executions_df)

"""end"""





