from datamodel import Order, OrderDepth, Trade

class MatchingEngine:
    def __init__(self, volume_limit: int = 200):
        # Set the hard constraint for max volume per order
        self.volume_limit = volume_limit

    def process_orders(self, timestamp: int, desired_orders: dict[str, list[Order]], current_state: dict[str, OrderDepth]) -> list[Trade]:
        executed_trades = []
        
        for symbol, orders in desired_orders.items():
            market_depth = current_state[symbol]
            
            for order in orders:
                
                direction = 1 if order.quantity > 0 else -1
                remaining_quantity = min(abs(order.quantity), self.volume_limit)
                
                if remaining_quantity == 0:
                    continue
                
                if direction == 1:
                    asks = sorted(market_depth.sell_orders.items()) 
                    
                    for ask_price, ask_vol in asks:
                        if remaining_quantity <= 0:
                            break  # Our order is completely filled
                            
                        if order.price >= ask_price: 
                            # Calculate how much we can actually trade at this price level
                            # (Taking abs() in case your ingester stores ask volumes as negative numbers)
                            available_vol = abs(ask_vol) 
                            
                            # We can only trade the smaller of what we want vs what is available
                            trade_vol = min(remaining_quantity, available_vol)
                            
                            if trade_vol > 0:
                                executed_trades.append(Trade(symbol, ask_price, trade_vol, buyer="BOT", seller="", timestamp=timestamp))
                                remaining_quantity -= trade_vol
                                
                                # 2. DEPLETE THE ORDER BOOK: Prevent double-filling the same volume
                                # If your ingester uses negative numbers for asks, change this to += trade_vol
                                market_depth.sell_orders[ask_price] -= trade_vol 
                                
                elif direction == -1:
                    # WE ARE SELLING -> Match against Bids (highest to lowest)
                    bids = sorted(market_depth.buy_orders.items(), reverse=True) 
                    
                    for bid_price, bid_vol in bids:
                        if remaining_quantity <= 0:
                            break  # Our order is completely filled
                            
                        if order.price <= bid_price: 
                            available_vol = bid_vol
                            trade_vol = min(remaining_quantity, available_vol)
                            
                            if trade_vol > 0:
                                executed_trades.append(Trade(symbol, bid_price, trade_vol, buyer="", seller="BOT", timestamp=timestamp))
                                remaining_quantity -= trade_vol
                                
                                # Deplete the order book
                                market_depth.buy_orders[bid_price] -= trade_vol
                                
        return executed_trades