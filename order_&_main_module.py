from data_manager import Bot
from ibapi.order import Order
import time
from time import sleep

class EntryOrder():
    def __init__(self, leg):
        self.entry_order = Order()
        self.entry_order.orderType = "BOX TOP"
        self.entry_order.action = leg
        self.entry_order.totalQuantity = 1
        self.entry_order.eTradeOnly = False
        self.entry_order.firmQuoteOnly = False

class limit_order():
    def __init__(self, parentId, somePrice):
        self.order = Order()
        self.order.action = "SELL"
        self.order.orderType = "STL LMT"
        self.order.lmtPrice = somePrice
        self.order.auxPrice = somePrice * 0.95
        self.order.totalQuantity = 1
        self.order.eTradeOnly = False
        self.order.firmQuoteOnly = False
        self.order.parentId = parentId


class RiskManagementOrder():
    def __init__(self, leg ,entry_price, parentId):
        self.order = Order()
        self.order.action = "SELL"  # if leg == "BUY" else "BUY"
        self.order.orderType = "TRAIL LIMIT"
        self.order.totalQuantity = 1
        self.order.eTradeOnly = False
        self.order.firmQuoteOnly = False
        self.order.trailStopPrice = entry_price * 0.95 if leg == "BUY" else entry_price * 1.05
        self.order.lmtPriceOffset = 3
        self.order.auxPrice = False  # to verify
        self.order.parentId = parentId


#the Main module

bot = Bot()
time.sleep(1)
ORDER_ID = bot.ib.return_nextvalidid()
SUN_ID = ORDER_ID + 1

long = "BUY"
short = "SELL"


long_leg = EntryOrder("BUY")
bot.ib.placeOrder(ORDER_ID, bot.o_m_d_c.contract, long_leg.entry_order)
parent_id = ORDER_ID
# bot.ib.reqAllOpenOrders()
time.sleep(3)
# print("10 s")
# bot.ib.openOrderEnd()
# bot.ib.reqExecutions(1, ExecutionFilter)
# bot.ib.reqPositions()

print(f"XXXX entry price: {bot.ib.return_entry_price()}")
long_leg_entry_price = bot.ib.return_entry_price()
limit_order = limit_order(parent_id, long_leg_entry_price * 0.5)
bot.ib.placeOrder(ORDER_ID, bot.o_m_d_c.contract, limit_order.order)
parent_id = ORDER_ID
stl_long_leg = RiskManagementOrder(long, long_leg_entry_price, ORDER_ID)
if bot.ib.is_parent_order_filled == True:
    bot.ib.placeOrder(ORDER_ID, bot.o_m_d_c.contract, stl_long_leg.order)


# short_leg = EntryOrder(short)
# bot.ib.placeOrder(7, bot.o_m_d_p, short_leg)
#
# short_leg_entry_price = 0 #to fix
# short_leg_id = 0 #to fix
# stl_short_leg = RiskManagementOrder(short, short_leg_entry_price, short_leg_id)
# bot.ib.placeOrder(7, bot.o_m_d_p, stl_short_leg)


