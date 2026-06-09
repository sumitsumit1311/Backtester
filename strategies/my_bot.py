import math
import json
from datamodel import OrderDepth, TradingState, Order

class Trader:
    def __init__(self):
        self.LIMIT = 200
        self.MARK_ERROR = 8.0 

    def run(self, state: TradingState):
        result = {}
        
        try:
            trader_dict = json.loads(state.traderData) if state.traderData else {}
        except Exception:
            trader_dict = {}
        
        for product in state.order_depths.keys():
            order_depth_h = state.order_depths[product]
            orders_h = []
            pos_h = state.position.get(product, 0)
            
            bids = sorted(order_depth_h.buy_orders.items(), key=lambda x: x[0], reverse=True)
            asks = sorted(order_depth_h.sell_orders.items(), key=lambda x: x[0])

            if bids and asks:
                current_mid = (bids[0][0] + asks[0][0]) / 2.0
                
                # --- CALCULATE ORDERBOOK IMBALANCE ---
                bid_vol = sum(order_depth_h.buy_orders.values())
                ask_vol = abs(sum(order_depth_h.sell_orders.values()))
                
                # Range [-1, 1]. Positive = Buy Heavy, Negative = Sell Heavy
                imbalance = (bid_vol - ask_vol) / (bid_vol + ask_vol)

                predictive_offset = 0
                if imbalance > 0.4:
                    predictive_offset = -4  
                elif imbalance < -0.4:
                    predictive_offset = 3   

                target_bid = int(current_mid - self.MARK_ERROR + predictive_offset)
                target_ask = int(current_mid + self.MARK_ERROR + predictive_offset)

                skew = int((pos_h / self.LIMIT) * 12)
                final_bid = target_bid - skew
                final_ask = target_ask - skew

                # --- EXECUTION ---
                buy_allowance = self.LIMIT - pos_h
                sell_allowance = self.LIMIT + pos_h

                for price, vol in asks:
                    if price < (current_mid - 7 + predictive_offset) and buy_allowance > 0:
                        qty = min(-vol, buy_allowance)
                        orders_h.append(Order(product, price, int(qty)))
                        buy_allowance -= qty

                if buy_allowance > 0:
                    orders_h.append(Order(product, final_bid, int(buy_allowance)))
                if sell_allowance > 0:
                    orders_h.append(Order(product, final_ask, int(-sell_allowance)))

            result[product] = orders_h
            trader_dict={}
            state.traderData = json.dumps(trader_dict)

        return result, 0, state.traderData