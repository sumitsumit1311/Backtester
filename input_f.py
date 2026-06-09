#ingester
import pandas as pd
from datamodel import TradingState, OrderDepth

def load_market_data(csv_path: str) -> tuple[dict[int, TradingState], list[str]]:
    print("Loading data into RAM...")
    df = pd.read_csv(csv_path, sep=';')
    
    # Fetching list of all products/commodities
    unique_products = df['product'].unique().tolist()
    
    market_data_by_tick = {}
    grouped = df.groupby('timestamp')
    
    for timestamp, group in grouped:
        order_depths = {}
        for _, row in group.iterrows():
            symbol = row['product']
            depth = OrderDepth()
            
            if pd.notna(row['bid_price_1']): depth.buy_orders[int(row['bid_price_1'])] = int(row['bid_volume_1'])
            if pd.notna(row['bid_price_2']): depth.buy_orders[int(row['bid_price_2'])] = int(row['bid_volume_2'])
            
            if pd.notna(row['ask_price_1']): depth.sell_orders[int(row['ask_price_1'])] = int(row['ask_volume_1'])
            if pd.notna(row['ask_price_2']): depth.sell_orders[int(row['ask_price_2'])] = int(row['ask_volume_2'])
            
            order_depths[symbol] = depth
            
        market_data_by_tick[timestamp] = TradingState(
            timestamp=timestamp,
            listings={}, 
            order_depths=order_depths,
            own_trades={}, market_trades={}, position={}, observations={},traderData=str
        )
        
    print(f"Loaded {len(market_data_by_tick)} ticks. Found products: {unique_products}")
    return market_data_by_tick, unique_products