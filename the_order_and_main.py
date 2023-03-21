import data_manager
from data_manager import Bot
from ibapi.order import Order


class EntryOrder():
    def __init__(self, leg):
        self.entry_order = Order()
        self.entry_order.orderType = "BOX TOP"
        self.entry_order.action = leg
        self.entry_order.totalQuantity = 1
        self.entry_order.eTradeOnly = False
        self.entry_order.firmQuoteOnly = False

class RiskManagementOrder():
    def __init__(self, leg ,entry_price, parentId):
        self.order = Order()
        self.order.orderType = "TRAIL LIMIT"
        self.order.action = "SELL" if leg == "BUY" else "BUY"
        self.order.totalQuantity = 1
        self.order.eTradeOnly = False
        self.order.firmQuoteOnly = False
        self.order.trailStopPrice = entry_price * 0.95 if leg == "BUY" else entry_price * 1.05
        self.order.lmtPriceOffset = 3
        self.order.auxPrice = False  # to verify
        self.order.parentId = parentId


#the Main module

bot = Bot()


long = "BUY"
short = "SELL"


long_leg = EntryOrder("BUY")
bot.ib.placeOrder(1, bot.o_m_d_c.contract, long_leg.entry_order)
bot.ib.reqExecutions(1)
bot.ib.reqPositions()


# long_leg_entry_price = 0 #to fix
# long_leg_id = 0 #to fix
# stl_long_leg = RiskManagementOrder(long, long_leg_entry_price, long_leg_id)
# bot.ib.placeOrder(5, bot.o_m_d_c, stl_long_leg)


# short_leg = EntryOrder(short)
# bot.ib.placeOrder(7, bot.o_m_d_p, short_leg)
#
# short_leg_entry_price = 0 #to fix
# short_leg_id = 0 #to fix
# stl_short_leg = RiskManagementOrder(short, short_leg_entry_price, short_leg_id)
# bot.ib.placeOrder(7, bot.o_m_d_p, stl_short_leg)
