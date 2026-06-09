#datamodel
from typing import Dict, List

class Order:
    def __init__(self, symbol: str, price: int, quantity: int):
        self.symbol = symbol
        self.price = price
        self.quantity = quantity
        # Positive quantity = BUY, Negative quantity = SELL

class OrderDepth:
    def __init__(self):
        self.buy_orders: Dict[int, int] = {}  # {price: quantity}
        self.sell_orders: Dict[int, int] = {} 

class Trade:
    def __init__(self, symbol: str, price: int, quantity: int, buyer: str = None, seller: str = None, timestamp: int = 0):
        self.symbol = symbol
        self.price = price
        self.quantity = quantity
        self.timestamp = timestamp

class TradingState:
    def __init__(self, timestamp: int, listings: dict, order_depths: Dict[str, OrderDepth], own_trades: dict, market_trades: dict, position: dict, observations: dict,traderData: str):
        self.timestamp = timestamp
        self.order_depths = order_depths
        self.own_trades = own_trades
        self.position = position
        self.listings = listings
        self.market_trades = market_trades
        self.observations = observations
        self.traderData = traderData