import csv
import io
from dataclasses import dataclass
from typing import Iterator, Optional


@dataclass
class MarketEvent:
    timestamp: int  
    event_type: str 
    side: str       
    price: float
    qty: int
    order_id: int   


class MarketDataReplayer:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.id_counter = 10000 

    def stream_events(self) -> Iterator[MarketEvent]:
        """
        A Generator that yields events one by one.
        This allows processing massive files without loading RAM.
        """
        mock_csv_data = """timestamp,type,side,price,qty
1000000,ADD,buy,100.00,500
1000050,ADD,sell,100.50,200
1000100,ADD,sell,100.55,300
1005000,CANCEL,sell,100.55,300
1010000,TRADE,buy,100.50,50"""
        
        reader = csv.DictReader(io.StringIO(mock_csv_data))
        
        for row in reader:
            yield MarketEvent(
                timestamp=int(row['timestamp']),
                event_type=row['type'],
                side=row['side'],
                price=float(row['price']),
                qty=int(row['qty']),
                order_id=self._generate_id()
            )

    def _generate_id(self):
        self.id_counter += 1
        return self.id_counter


def apply_market_event(engine, event: MarketEvent):
    """
    Takes a Market Data Event and updates the Matching Engine.
    This reconstructs the 'Background' state of the market.
    """
    from dataclasses import replace
    
    
    if event.event_type == 'ADD':
        order = Order(
            id=event.order_id,
            side=event.side,
            price=event.price,
            qty=event.qty,
            timestamp=event.timestamp 
        )
        engine.process_order(order)
        
    elif event.event_type == 'CANCEL':
        book_side = engine.bids if event.side == 'buy' else engine.asks
        
        if event.price in book_side.price_levels:
            queue = book_side.price_levels[event.price]
            remaining_to_cancel = event.qty
            
            if queue:
                target = queue[-1] 
                if target.open_qty >= remaining_to_cancel:
                    target.qty -= remaining_to_cancel
                else:
                    pass


if __name__ == "__main__":
    
    replayer = MarketDataReplayer("dummy.csv")
    engine = MatchingEngine() 
    
    print("--- Starting Replay ---")
    
    current_sim_time = 0
    
    for event in replayer.stream_events():
        current_sim_time = event.timestamp
        
        print(f"[{current_sim_time} us] Market Event: {event.event_type} {event.qty} @ {event.price}")
        
        apply_market_event(engine, event)
        
        best_bid = engine.bids.best_price()
        best_ask = engine.asks.best_price()
        print(f"    Current Book: {best_bid} | {best_ask}")