from ibapi.execution import ExecutionFilter

from data_manager import Bot
from ibapi.order import Order
import time
from time import sleep
import math

def round_up_to_025(x):
    return math.ceil(x / 1) * 1
def round_down_to_025(x):
    return math.floor(x / 0.25) * 0.25


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

# class EntryOrder():
#     def __init__(self, leg, limit_price):
#         self.entry_order = Order()
#         self.entry_order.orderType = "LMT"
#         self.entry_order.action = leg
#         self.entry_order.totalQuantity = 1
#         self.entry_order.eTradeOnly = False
#         self.entry_order.firmQuoteOnly = False
#         self.entry_order.lmtPrice = limit_price

# class LimitOrder():
#     def __init__(self, parentId, somePrice):
#         self.order = Order()
#         self.order.action = "SELL"
#         self.order.orderType = "STP LMT"
#         self.order.lmtPrice = somePrice
#         self.order.auxPrice = round_up_to_025(somePrice * 0.80)
#         self.order.totalQuantity = 1
#         self.order.eTradeOnly = False
#         self.order.firmQuoteOnly = False
#         self.order.parentId = parentId
#         # print(f" aux Price: {self.order.auxPrice}")

# class RiskManagementOrder():
#     def __init__(self ,entry_price):
#         self.order = Order()
#         self.order.action = "SELL"
#         self.order.orderType = "TRAIL"
#         self.order.totalQuantity = 1
#         self.order.eTradeOnly = False
#         self.order.firmQuoteOnly = False
#         self.order.trailingPercent = 3
#         self.order.trailStopPrice = round_down_to_025(entry_price * 0.9)
#         print(f"Stop Price: {round_down_to_025(entry_price * 0.9)}")
        # self.order.lmtPriceOffset = 3
        # self.order.auxPrice = False  # to verify
        # self.order.parentId = parentId
        #self.order.transmit = True



#the Main module

bot = Bot()
time.sleep(1)
ORDER_ID = bot.ib.return_nextvalidid()
SUN_ID = ORDER_ID + 1
# GRAND_SUN_ID = SUN_ID + 1



entry_order = EntryOrder()
bot.ib.placeOrder(ORDER_ID, bot.o_m_d_c.contract, entry_order.entry_order)
time.sleep(1)
bot.ib.order_filled()

exit_order = ExitOrder()

while bot.ib.return_stl_triggered() == False:
    print(f"waiting")
    time.sleep(1)
else:
    print(f"EXIT EXIT EXIT ! placing EXIT order ! EXIT EXIT EXIT")
    bot.ib.placeOrder(SUN_ID, bot.o_m_d_c.contract, exit_order.exit_order)

print(bot.ib.call_bid_prices)


# ef = ExecutionFilter()
# ef.secType = "FOP"
# bot.ib.reqExecutions(1, ef)



# # if bot.ib.isFilled() == True :
# #     print(f"XXXX entry price: {bot.ib.return_entry_price()}")
#     long_leg_entry_price = bot.ib.return_entry_price()
    # stl_long_leg = RiskManagementOrder(long_leg_entry_price)
    # bot.ib.placeOrder(SUN_ID, bot.o_m_d_c.contract, stl_long_leg.order)



# bot.ib.reqPositions()




# short_leg = EntryOrder(short)
# bot.ib.placeOrder(7, bot.o_m_d_p, short_leg)
#
# short_leg_entry_price = 0 #to fix
# short_leg_id = 0 #to fix
# stl_short_leg = RiskManagementOrder(short, short_leg_entry_price, short_leg_id)
# bot.ib.placeOrder(7, bot.o_m_d_p, stl_short_leg)

#

















