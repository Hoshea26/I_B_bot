from ib_socket import IBapi
from option_contract import OptionsMarketData
from one_time_price import UnderlyingData
import threading
import datetime
import time
import math

from underlying_contract import MarketDataUnderLying

# HOST = "172.20.10.11"
HOST = "127.0.0.1"
PORT = 7496
CLIENTID = 1

def round_up_to_5(x):
    return math.ceil(x / 5) * 5
def round_down_to_5(x):
    return math.floor(x / 5) * 5

option_e_date = datetime.datetime.now().strftime("%Y%m%d")
# option_e_date = "20230428"

class Bot:

    def __init__(self):
        self.ib = IBapi()
        self.ib.connect(host=HOST, port=PORT, clientId=CLIENTID)
        self.thread = threading.Thread(target=self.ran_loop, daemon=True)
        self.thread.start()
        time.sleep(1)
        self.m_d_u = MarketDataUnderLying("MES", "FUT", "USD", "CME", "202306")
        self.ib.reqMktData(reqId=1,
                           contract=self.m_d_u.contract,
                           genericTickList="",
                           snapshot=False,
                           regulatorySnapshot=False,
                           mktDataOptions=[])
        time.sleep(1)
        underlying_price = self.ib.return_price()
        self.call_strike = round_up_to_5(underlying_price)
        self.put_strike = round_down_to_5(underlying_price)
        print(f"UNDERLYING PRICE: {underlying_price}")
        print("#                #                  #")
        print(f"CALL STRIKE: {self.call_strike}")
        print("#                #                  #")
        print(f"PUT STRIKE: {self.put_strike}")
        print("#                #                  #")


        # self.m_d_u = MarketDataUnderLying("MES", "FUT", "USD", "CME", "202306")
        self.call_contract = OptionsMarketData("MES",
                                         "FOP",
                                         "USD",
                                         "CME",
                                               option_e_date,
                                               self.call_strike,
                                         "C",
                                               5)
        self.put_contract = OptionsMarketData("MES",
                                         "FOP",
                                         "USD",
                                         "CME",
                                              option_e_date,
                                              self.put_strike,
                                         "P",
                                              5)

        self.reqid = 2
        self. market_data = []
        self.req_market_data()

    def req_market_data(self):
        # self.market_data.append(self.m_d_u)
        self.market_data.append(self.call_contract)
        self.market_data.append(self.put_contract)
        for data in self.market_data:
            self.ib.reqMktData(reqId=self.reqid,
                               contract=data.contract,
                               genericTickList="",
                               snapshot=False,
                               regulatorySnapshot=False,
                               mktDataOptions=[])
            self.reqid += 1

    def ran_loop(self):
        self.ib.run()


# bot = Bot()
