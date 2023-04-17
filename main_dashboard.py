import time
import pandas as pd
import threading
from datetime import datetime
from ibapi.wrapper import EWrapper
from ibapi.client import EClient
from ibapi.contract import Contract
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import math

# Create an empty DataFrame with the specified column names
dashboard = pd.DataFrame(columns=["time", "underlying price", "call strike", "call price", "call bid", "call stl", "put strike", "put price", "put bid", "put stl", "error"])
option_e_date = datetime.now().strftime("%Y%m%d")

def round_up_to_5(x):
    return math.ceil(x / 5) * 5
def round_down_to_5(x):
    return math.floor(x / 5) * 5
class MarketDataApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.underlying_price_snapshot = 0

    def update_dashboard(self, time, underlying_price=None, call_strike=None, call_price=None, call_bid=None,
                         call_stl=None, put_strike=None, put_price=None, put_bid=None, put_stl=None, error=None):
        global dashboard
        # Create a new row with the specified values
        new_row = {
            "time": time,
            "underlying price": underlying_price,
            "call strike": call_strike,
            "call price": call_price,
            "call bid": call_bid,
            "call stl": call_stl,
            "put strike": put_strike,
            "put price": put_price,
            "put bid": put_bid,
            "put stl": put_stl,
            "error": error
        }

        # If there's already a row with the same time, update it with the new values
        if len(dashboard) > 0 and dashboard.iloc[-1]["time"] == time:
            dashboard.iloc[-1] = {**dashboard.iloc[-1], **new_row}
        else:
            dashboard = dashboard._append(new_row, ignore_index=True)

    def tickPrice(self, reqId, tickType, price, attrib):
        #underlying price
        if tickType == 4 and reqId == 1:  # "LAST" price
            self.underlying_price_snapshot = price
            self.update_dashboard(time = datetime.now().strftime("%H:%M:%S"), underlying_price = price)
            print(f"Underlying Price : {price}")
            print(self.underlying_price_snapshot)

        #call option price
        if tickType == 4 and reqId == 2:
            print(f"Call Option Price : {price}")
            self.update_dashboard(time = datetime.now().strftime("%H:%M:%S"), call_price = price)


        #call option bid
        if tickType == 1 and reqId == 2:
            print(f"CALL Option bid : {price}")
            self.update_dashboard(time = datetime.now().strftime("%H:%M:%S"), call_bid = price)


        #put option price
        if tickType == 4 and reqId == 3:
            print(f"Put Option Price : {price}")
            self.update_dashboard(time = datetime.now().strftime("%H:%M:%S"), put_price = price)


        #put option bid
        if tickType == 1 and reqId == 3:
            print(f"Put Option bid : {price}")
            self.update_dashboard(time = datetime.now().strftime("%H:%M:%S"), put_bid = price)


    def return_underlying_price_snapshot(self):
        return self.underlying_price_snapshot
def animate_underlying_price(i):
    global dashboard
    x_values = dashboard["time"]
    y_values = dashboard["underlying price"]
    plt.cla()
    plt.plot(x_values, y_values, label="Underlying price")
    plt.legend(loc="upper left")
    plt.tight_layout()

def animate_call_bid(i):
    global dashboard
    global app
    x_values = dashboard["time"]
    y_values = dashboard["call bids"]
    plt.cla()
    plt.plot(x_values, y_values, label="call bids")
    plt.legend(loc="upper left")
    plt.tight_layout()

def update(i):
    animate_underlying_price(i)
    animate_call_bid(i)
def main():
    global dashboard
    # Define the asset (S&P 500 E-mini futures contract in this example)
    underlying_contract = Contract()
    underlying_contract.symbol = "MES"
    underlying_contract.secType = "FUT"
    underlying_contract.exchange = "CME"
    underlying_contract.currency = "USD"
    underlying_contract.lastTradeDateOrContractMonth = "202306"  # Change this to the desired expiration date

    # Create an instance of the MarketDataApp class
    app = MarketDataApp()
    # Connect to the IB
    app.connect("127.0.0.1", 7496, clientId=2)  # Change the IP, port, and clientId as needed
    # Start the app in a separate thread
    app_thread = threading.Thread(target=app.run)
    app_thread.start()

    # Request market data for the specified contract
    app.reqMktData(1, underlying_contract, "", False, False, [])

    time.sleep(1)

    price_snapshot = app.return_underlying_price_snapshot()
    call_strike = round_up_to_5(price_snapshot)
    print(f"Call Strike : {call_strike}")
    put_strike = round_down_to_5(price_snapshot)
    print(f"Put Strike : {put_strike}")

    call_contract = Contract()
    call_contract.symbol = "MES"
    call_contract.secType = "FOP"
    call_contract.exchange = "CME"
    call_contract.currency = "USD"
    call_contract.lastTradeDateOrContractMonth = option_e_date
    call_contract.strike = call_strike
    call_contract.right = "CALL"
    call_contract.multiplier = 5

    put_contract = Contract()
    put_contract.symbol = "MES"
    put_contract.secType = "FOP"
    put_contract.exchange = "CME"
    put_contract.currency = "USD"
    put_contract.lastTradeDateOrContractMonth = option_e_date
    put_contract.strike = put_strike
    put_contract.right = "PUT"
    put_contract.multiplier = 5


    # Request market data for the specified contract
    app.reqMktData(2, call_contract, "", False, False, [])
    app.reqMktData(3, put_contract, "", False, False, [])

    # Set up the live dashboard
    underlying_price_animation = FuncAnimation(plt.gcf(), update, interval=1000)
    plt.tight_layout()
    plt.show()
    print(dashboard)

if __name__ == "__main__":
    main()
