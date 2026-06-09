import math
import json
from datamodel import OrderDepth, TradingState, Order

class Trader:
    def __init__(self):
        self.HYDRO = "HYDROGEL_PACK"
        self.LIMIT = 200
        self.MARK_ERROR = 8.0 

    def run(self, state: TradingState):
        result = {self.HYDRO: []}
        
        
        
        if self.HYDRO in state.order_depths:
            order_depth_h = state.order_depths[self.HYDRO]
            orders_h = []
            pos_h = state.position.get(self.HYDRO, 0)
            
            bids = sorted(order_depth_h.buy_orders.items(), key=lambda x: x[0], reverse=True)
            asks = sorted(order_depth_h.sell_orders.items(), key=lambda x: x[0])

            if bids and asks:
                current_mid = (bids[0][0] + asks[0][0]) / 2.0
                
                # --- CALCULATE ORDERBOOK IMBALANCE ---
                # Total volume available on top 3 levels
                bid_vol = sum(order_depth_h.buy_orders.values())
                ask_vol = abs(sum(order_depth_h.sell_orders.values()))
                
                # Range [-1, 1]. Positive = Buy Heavy, Negative = Sell Heavy
                imbalance = (bid_vol - ask_vol) / (bid_vol + ask_vol)

                # --- TRANSLATE IMBALANCE TO PRICE SHIFT ---
                # Based on analysis: Imbalance > 0.5 -> -4.7pts next return
                # We shift our target prices by this expected return
                predictive_offset = 0
                if imbalance > 0.4:
                    predictive_offset = -4  # Front-run the drop
                elif imbalance < -0.4:
                    predictive_offset = 3   # Front-run the rise

                # --- DEFINE ASYMMETRIC HARVESTING LEVELS ---
                # We target the Mark 38 premium (mid+8) and Mark 14 discount (mid-8)
                # But we adjust them by the predictive imbalance offset
                target_bid = int(current_mid - self.MARK_ERROR + predictive_offset)
                target_ask = int(current_mid + self.MARK_ERROR + predictive_offset)

                # --- INVENTORY LEASH (AGGRESSIVE) ---
                # Increased multiplier to 12 to ensure we don't hold 'Toxic' inventory
                skew = int((pos_h / self.LIMIT) * 12)
                final_bid = target_bid - skew
                final_ask = target_ask - skew

                # --- EXECUTION ---
                buy_allowance = self.LIMIT - pos_h
                sell_allowance = self.LIMIT + pos_h

                # 1. TAKER: Snipe outliers if Mark 38 makes a massive mistake
                for price, vol in asks:
                    if price < (current_mid - 7 + predictive_offset) and buy_allowance > 0:
                        qty = min(-vol, buy_allowance)
                        orders_h.append(Order(self.HYDRO, price, int(qty)))
                        buy_allowance -= qty

                # 2. MAKER: Place the 'Predator' orders
                if buy_allowance > 0:
                    orders_h.append(Order(self.HYDRO, final_bid, int(buy_allowance)))
                if sell_allowance > 0:
                    orders_h.append(Order(self.HYDRO, final_ask, int(-sell_allowance)))

            result[self.HYDRO] = orders_h
            trader_dict={}
            state.traderData = json.dumps(trader_dict)

        return result, 0, state.traderData