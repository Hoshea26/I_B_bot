from ibapi.execution import ExecutionFilter
from data_manager import CLIENTID
from data_manager import Bot
from ibapi.order import Order
import time
import dash
from dash import dcc
from dash import html
import plotly.graph_objs as go


class EntryOrder(Order):
    def __init__(self):
        super().__init__()
        self.orderType = "BOX TOP"
        self.action = "BUY"
        self.totalQuantity = 1
        self.eTradeOnly = False
        self.firmQuoteOnly = False


class ExitOrder(Order):
    def __init__(self):
        super().__init__()
        self.orderType = "BOX TOP"
        self.action = "SELL"
        self.totalQuantity = 1
        self.eTradeOnly = False
        self.firmQuoteOnly = False

bot = Bot()
CALL_SUN_ID = 0
PUT_SUN_ID = 0

def strategy():

    def place_exit_order(contract, order_id, order):
        print(f"EXIT order ID {order_id}")
        bot.ib.placeOrder(order_id, contract, order)
        print("EXIT ORDER WAS PLACED")

    def trade_loop():
        global CALL_SUN_ID, PUT_SUN_ID

        entry_order = EntryOrder()
        exit_order = ExitOrder()

        bot.ib.reqIds(-1)
        time.sleep(1)
        CALL_ORDER_ID = bot.ib.return_next_valid_id()
        # print(f"CALL_ORDER_ID : {CALL_ORDER_ID}")
        bot.ib.placeOrder(CALL_ORDER_ID, bot.call_contract.contract, entry_order)
        print("CALL ORDER WAS PLACED")

        PUT_ORDER_ID = CALL_ORDER_ID + 1
        # print(f"PUT_ORDER_ID : {PUT_ORDER_ID}")
        bot.ib.placeOrder(PUT_ORDER_ID, bot.put_contract.contract, entry_order)
        print("PUT ORDER WAS PLACED")

        while bot.ib.executions.empty:
            time.sleep(0.1)
            print("waiting for executions")
        print(bot.ib.executions["right"][0],bot.ib.executions["strike"][0],
              bot.ib.executions["side"][0],bot.ib.executions["price"][0])
        while len(bot.ib.executions) == 1:
            time.sleep(0.1)
        print(bot.ib.executions["right"][1], bot.ib.executions["strike"][1],
                bot.ib.executions["side"][1], bot.ib.executions["price"][1])

        call_count = 0
        put_count = 0

        while True:
            c_is_true = bot.ib.is_call_stl_triggered()
            p_is_true = bot.ib.is_put_stl_triggered()

            if c_is_true and not call_count:
                CALL_SUN_ID = PUT_ORDER_ID + 1 if not put_count else PUT_SUN_ID + 1
                place_exit_order(bot.call_contract.contract, CALL_SUN_ID, exit_order)
                if put_count == 0:
                    while len(bot.ib.executions) == 2:
                        time.sleep(0.1)
                if put_count == 1:
                    while len(bot.ib.executions) == 3:
                        time.sleep(0.1)
                print(bot.ib.executions["right"][-1], bot.ib.executions["strike"][-1],
                      bot.ib.executions["side"][-1], bot.ib.executions["price"][-1])
                call_count = 1


            if p_is_true and not put_count:
                PUT_SUN_ID = PUT_ORDER_ID + 1 if not call_count else CALL_SUN_ID + 1
                place_exit_order(bot.put_contract.contract, PUT_SUN_ID, exit_order)
                if call_count == 0:
                    while len(bot.ib.executions) == 2:
                        time.sleep(0.1)
                if call_count == 1:
                    while len(bot.ib.executions) == 3:
                        time.sleep(0.1)
                print(bot.ib.executions["right"][-1], bot.ib.executions["strike"][-1],
                      bot.ib.executions["side"][-1], bot.ib.executions["price"][-1])
                put_count = 1

            if c_is_true and p_is_true:
                bot.ib.reset_stl()
                break

    while True:
        trade_loop()

# strategy()

class Dash_Bot:
    def __init__(self, bot_ib_underlying_price_df_time,
                 bot_ib_underlying_price_df_price):
        self.bot_ib_underlying_price_df_time = bot_ib_underlying_price_df_time
        self.bot_ib_underlying_price_df_price = bot_ib_underlying_price_df_price

    def update_underlying_prices_graph(self, n):
        trace_chart = go.Scatter(x=list(self.bot_ib_underlying_price_df_time),
                                 y=list(self.bot_ib_underlying_price_df_price),
                                 name="Underlying Prices",
                                 line=dict(color="#4287f5")
                                 )
        data = [trace_chart]
        layout = dict(title="Underlying Prices Chart", showlegend=False)
        fig = dict(data=data, layout=layout)
        return fig

    def serve_layout(self):
        return html.Div(children=[
            html.H1(children='The Options Dashboard'),

            html.Label("Underlying Prices"),
            html.Div(dcc.Graph(id="underlying-prices")),
            dcc.Interval(id='interval-component', interval=0.5 * 1000, n_intervals=0),
        ])


d = Dash_Bot(bot.ib.underlying_price_df.time, bot.ib.underlying_price_df.price)
web = dash.Dash()
web.layout = d.serve_layout()

web.callback(
    dash.dependencies.Output('underlying-prices', 'figure'),
    [dash.dependencies.Input('interval-component', 'n_intervals')]
)(d.update_underlying_prices_graph)

web.run_server(debug=True, use_reloader=False)
