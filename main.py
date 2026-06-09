from input_f import load_market_data
from engine import MatchingEngine
from strategies import Trader # Your bot

def run_backtest(csv_path: str):
    # 1. Unpack both the data and the dynamic product list
    market_data, product_list = load_market_data(csv_path)
    
    trader = Trader()
    engine = MatchingEngine()
    
    # 2. DYNAMIC INITIALIZATION: 
    # Create a dictionary setting the position of every discovered product to 0
    positions = {product: 0 for product in product_list}
    cash = 0
    
    timestamps = sorted(market_data.keys())
    
    print("Starting simulation...")
    for t in timestamps:
        current_state = market_data[t]
        
        # Inject our dynamic positions into the state
        current_state.position = positions.copy()
        result = trader.run(current_state)

        if isinstance(result, tuple) and len(result) == 3:
            orders, conversions, trader_data = result # Unpack all three safely!
        else:
            orders = result
        
        trades = engine.process_orders(t, orders, current_state.order_depths)
        
        for trade in trades:
            if trade.buyer == "BOT":
                positions[trade.symbol] += trade.quantity
                cash -= (trade.price * trade.quantity)
            elif trade.seller == "BOT":
                positions[trade.symbol] -= trade.quantity
                cash += (trade.price * trade.quantity)
                
    print("Simulation complete!")
    print(f"Final Cash: {cash}")
    print(f"Final Positions: {positions}")

if __name__ == "__main__":
    run_backtest("prices_round_1_day_0.csv")