import dash
# import dash_core_components as dcc
from dash import dcc
from dash import html
# import dash_html_components as html
import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
import time
import threading
from datetime import datetime
from ibapi.wrapper import EWrapper
from ibapi.client import EClient
from ibapi.contract import Contract
import plotly.graph_objs as go
import math
import random
import numpy as np

def round_up_to_5(x):
    return math.ceil(x / 5) * 5
def round_down_to_5(x):
    return math.floor(x / 5) * 5


option_e_date = datetime.now().strftime("%Y%m%d")
STL_MARGIN = 0.8
underlying_price_df = pd.DataFrame(columns=["time", "price"])
call_bid_df = pd.DataFrame(columns=["time", "price"])
call_bid_stl_df = pd.DataFrame(columns=["time", "max bid", "stl"])
put_bid_df = pd.DataFrame(columns=["time", "price"])
put_bid_stl_df = pd.DataFrame(columns=["time", "max bid", "stl"])
put_bid_hist_df = pd.DataFrame(columns=["time", "open", "high", "low", "close"])

new_row = {"time": datetime.now().strftime("%H:%M:%S"), "price": 0}
call_bid_df = call_bid_df._append(new_row, ignore_index=True)
put_bid_df = put_bid_df._append(new_row, ignore_index=True)

def append_price(time, price, asset_type):
    global underlying_price_df
    global call_bid_df
    global put_bid_df
    new_row = {
        "time": time,
        "price": price,
    }
    if asset_type == "underlying":
        underlying_price_df = underlying_price_df._append(new_row, ignore_index=True)
    if asset_type == "call":
        call_bid_df = call_bid_df._append(new_row, ignore_index=True)
    if asset_type == "put":
        put_bid_df = put_bid_df._append(new_row, ignore_index=True)

def append_stl(time, max_price, asset_type):
    global underlying_stl_df
    global call_bid_stl_df
    global put_bid_stl_df


    stl = max_price * STL_MARGIN

    new_row = {
        "time": time,
        "stl": stl
    }
    if asset_type == "call":
        call_bid_stl_df = call_bid_stl_df._append(new_row, ignore_index=True)
    if asset_type == "put":
        put_bid_stl_df = put_bid_stl_df._append(new_row, ignore_index=True)
class MarketDataApp(EWrapper, EClient):
    global underlying_price_df
    global call_bid_df
    global put_bid_df
    def __init__(self):
        EClient.__init__(self, self)
        self.underlying_price_snapshot = 0

    def tickPrice(self, reqId, tickType, price, attrib):
        # underlying price
        if tickType == 4 and reqId == 1:
            self.underlying_price_snapshot = price
            # print(f"Underlying Price : {price}")
            if price != -1:
                append_price(datetime.now().strftime("%H:%M:%S"), price, "underlying")


        # call option price
        if tickType == 4 and reqId == 2:
            # print(f"Call Option Price : {price}")
            pass

        # call option bid
        if tickType == 1 and reqId == 2:
            # print(f"CALL Option bid : {price}")
            if price != -1:
                append_price(datetime.now().strftime("%H:%M:%S"), price, "call")
                append_stl(datetime.now().strftime("%H:%M:%S"), call_bid_df["price"].max(), "call")

        # put option price
        if tickType == 4 and reqId == 3:
            # print(f"Put Option Price : {price}")
            pass

        # put option bid
        if tickType == 1 and reqId == 3:
            # print(f"Put Option bid : {price}")
            if price != -1:
                append_price(datetime.now().strftime("%H:%M:%S"), price, "put")
                append_stl(datetime.now().strftime("%H:%M:%S"), put_bid_df["price"].max(), "put")

    def historicalData(self, reqId, bar):
        global put_bid_hist_df
        if reqId == 1:
            # new_row = {"time": bar.date, "open": bar.open, "high": bar.high, "low": bar.low, "close": bar.close}
            # put_bid_hist_df = put_bid_hist_df.append(new_row, ignore_index=True)
            print(bar.date, bar.open, bar.high, bar.low, bar.close)
    def error(self, reqId, errorCode, errorString):
        print(errorCode)
        print(errorString)

    def return_underlying_price_snapshot(self):
        return self.underlying_price_snapshot

def remove_outliers_iqr(data, multiplier=1.5):
    Q1 = data.quantile(0.25)
    Q3 = data.quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - multiplier * IQR
    upper_bound = Q3 + multiplier * IQR
    return data.where((data >= lower_bound) & (data <= upper_bound))

def main():
    global underlying_price_df
    underlying_contract = Contract()
    underlying_contract.symbol = "MES"
    underlying_contract.secType = "FUT"
    underlying_contract.exchange = "CME"
    underlying_contract.currency = "USD"
    underlying_contract.lastTradeDateOrContractMonth = "202306"  # Change this to the desired expiration date

    app = MarketDataApp()
    app.connect("10.0.0.4", 7496, clientId=3)
    app_thread = threading.Thread(target=app.run)
    app_thread.start()
    app.reqMktData(1, underlying_contract, "", False, False, [])
    while app.return_underlying_price_snapshot() == 0:
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
    app.reqHistoricalData(reqId=1,
                          contract=put_contract,
                          endDateTime="",
                          durationStr="10800 s",
                          barSizeSetting="5 secs",
                          whatToShow="BID",
                          useRTH=0,
                          formatDate=1,
                          keepUpToDate=True,
                          chartOptions=[])

def serve_layout():
    return html.Div(children=[
        html.H1(children='The Options Dashboard'),

        # html.Label("Underlying Prices"),
        # html.Div(
        #     dcc.Graph(id="underlying-prices")
        # ),
        #
        # html.Label("Call Bids"),
        # html.Div(
        #     dcc.Graph(id="call-bids")
        # ),

        html.Label("Put Bids"),
        html.Div(
            # dcc.Checklist(id="put-bids",
            #               options=[{'label': 'Include Rangeslider',
            #                         'value': 'slider'}],
            #               value=['slider']
            #               ),
            dcc.Graph(id="put-bids-graph")
        ),

        html.Label("Put Bids - IQR Filtered"),
        html.Div(
            dcc.Graph(id="put-bids-iqr-filtered")
        ),

        dcc.Interval(
            id='interval-component',
            interval=0.5*1000,  # in milliseconds, update every 1 second
            n_intervals=0
        ),
    ])

def update_underlying_prices_graph(n):
    trace_chart = go.Scatter(x=list(underlying_price_df.time),
                             y=list(underlying_price_df.price),
                             name="Underlying Prices",
                             line=dict(color="#4287f5")
                             )
    data = [trace_chart]
    layout = dict(title="Underlying Prices Chart", showlegend=False)
    fig = dict(data=data, layout=layout)
    return fig

def update_call_bid_graph(n):

    trace_chart = go.Scatter(x=list(call_bid_df.time),
                             y=list(call_bid_df.price),
                             name="price",
                             mode="markers",  # Change to markers for dots
                             line=dict(color="#f44242")
                             )

    trace_stop_loss = go.Scatter(x=list(call_bid_stl_df.time),
                                 y=list(call_bid_stl_df.stl),
                                 name="Stop Loss",
                                 line=dict(color="#ff9900", dash="dash")
                                 )

    data = [trace_chart, trace_stop_loss]
    layout = dict(title="Call Bids Chart", showlegend=False)
    fig = dict(data=data, layout=layout)
    return fig


def update_put_bid_graph(n):
    trace_hist_candle = go.Candlestick(x=list(put_bid_hist_df.time),
                                       open=list(put_bid_hist_df.open),
                                       high=list(put_bid_hist_df.high),
                                       low=list(put_bid_hist_df.low),
                                       close=list(put_bid_hist_df.close),
                                       name="Historical Put Bids"
                                       )

    trace_chart = go.Scatter(x=list(put_bid_df.time),
                             y=list(put_bid_df.price),
                             name="Put Bids",
                             mode="markers",  # Change to markers for dots
                             marker=dict(color="#42f4b0")
                             )

    trace_stop_loss = go.Scatter(x=list(put_bid_stl_df.time),
                                 y=list(put_bid_stl_df.stl),
                                 name="Stop Loss",
                                 line=dict(color="#ff9900", dash="dash")
                                 )

    data = [trace_hist_candle, trace_chart, trace_stop_loss]
    layout = dict(title="Put Bids Chart", showlegend=False)
    fig = dict(data=data, layout=layout)
    return fig

def update_put_bid_iqr_filtered_graph(n):

    iqr_filtered_data = remove_outliers_iqr(put_bid_df["price"])

    trace_chart = go.Scatter(x=list(put_bid_df.time),
                             y=list(iqr_filtered_data),
                             mode='markers',
                             name="Put Bids - IQR Filtered",
                             marker=dict(color="#42f4b0")
                             )
    data = [trace_chart]
    layout = dict(title="Put Bids - IQR Filtered Chart", showlegend=False)
    fig = dict(data=data, layout=layout)
    return fig


web = dash.Dash()

web.layout = serve_layout()

# web.callback(
#     dash.dependencies.Output('underlying-prices', 'figure'),
#     [dash.dependencies.Input('interval-component', 'n_intervals')]
# )(update_underlying_prices_graph)
#
# web.callback(
#     dash.dependencies.Output('call-bids', 'figure'),
#     [dash.dependencies.Input('interval-component', 'n_intervals')]
# )(update_call_bid_graph)

web.callback(
    dash.dependencies.Output('put-bids-graph', 'figure'),
    [dash.dependencies.Input('interval-component', 'n_intervals')]
)(update_put_bid_graph)

web.callback(
    dash.dependencies.Output('put-bids-iqr-filtered', 'figure'),
    [dash.dependencies.Input('interval-component', 'n_intervals')]
)(update_put_bid_iqr_filtered_graph)

if __name__ == '__main__':
    main()
    web.run_server(debug=True, use_reloader=False)
