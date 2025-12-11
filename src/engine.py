import heapq
from collections import deque, defaultdict
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Order:
    id: int
    side: str  
    price: float
    qty: int
    timestamp: int 
    
    filled_qty: int = 0
    status: str = 'OPEN' 

    @property
    def open_qty(self):
        return self.qty - self.filled_qty

@dataclass
class Trade:
    price: float
    qty: int
    maker_order_id: int
    taker_order_id: int


class OrderBookSide:
    """
    Manages one side of the book (Bids or Asks).
    """
    def __init__(self, is_bid: bool):
        self.is_bid = is_bid
        self.price_heap = [] 
        self.price_levels = defaultdict(deque) 
        self.orders = {} 
        
    def add(self, order: Order):
        if order.price not in self.price_levels:
            heap_price = -order.price if self.is_bid else order.price
            heapq.heappush(self.price_heap, heap_price)
            
        self.price_levels[order.price].append(order)
        self.orders[order.id] = order

    def best_price(self) -> Optional[float]:
        if not self.price_heap:
            return None
        price = self.price_heap[0]
        return -price if self.is_bid else price

    def get_queue_position(self, order_id: int) -> int:
        """
        The 'Crystal Ball' feature: Returns how many shares are ahead of you.
        """
        if order_id not in self.orders:
            return -1
            
        target_order = self.orders[order_id]
        queue = self.price_levels[target_order.price]
        
        qty_ahead = 0
        for order in queue:
            if order.id == target_order.id:
                break
            qty_ahead += order.open_qty
        return qty_ahead

    def remove_filled_levels(self):
        """Clean up empty price levels from the heap."""
        while self.price_heap:
            raw_price = self.price_heap[0]
            real_price = -raw_price if self.is_bid else raw_price
            
            if not self.price_levels[real_price]:
                heapq.heappop(self.price_heap)
                del self.price_levels[real_price]
            else:
                break

class MatchingEngine:
    def __init__(self):
        self.bids = OrderBookSide(is_bid=True)
        self.asks = OrderBookSide(is_bid=False)
        self.trades = [] 

    def process_order(self, order: Order):
        """
        Entry point for all orders.
        Attempts to match immediately (Taking Liquidity).
        Resting orders go to the book (Making Liquidity).
        """
        opposing_book = self.bids if order.side == 'sell' else self.asks
        my_book = self.asks if order.side == 'sell' else self.bids

        while order.open_qty > 0:
            best_price = opposing_book.best_price()
            
            if best_price is None:
                break
            
            is_match = (order.side == 'buy' and order.price >= best_price) or \
                       (order.side == 'sell' and order.price <= best_price)
                       
            if not is_match:
                break

            best_queue = opposing_book.price_levels[best_price]
            maker_order = best_queue[0] 
            
            match_qty = min(order.open_qty, maker_order.open_qty)
            
            self._execute_trade(maker_order, order, match_qty, best_price)
            
            if maker_order.open_qty == 0:
                best_queue.popleft() 
                opposing_book.remove_filled_levels()

        if order.open_qty > 0:
            my_book.add(order)
            return "RESTING"
        else:
            return "FILLED"

    def _execute_trade(self, maker, taker, qty, price):
        maker.filled_qty += qty
        taker.filled_qty += qty
        
        if maker.open_qty == 0: maker.status = 'FILLED'
        else: maker.status = 'PARTIAL'
        
        if taker.open_qty == 0: taker.status = 'FILLED'
        else: taker.status = 'PARTIAL'

        self.trades.append(Trade(price, qty, maker.id, taker.id))
        print(f"TRADE: {qty} @ {price} | Maker: #{maker.id} | Taker: #{taker.id}")


if __name__ == "__main__":
    engine = MatchingEngine()
    
    print("1. Injecting Liquidity (Makers)...")
    engine.process_order(Order(1, 'sell', 101.0, 100, 1000))
    engine.process_order(Order(2, 'sell', 101.0, 50, 1001)) 
    engine.process_order(Order(3, 'sell', 102.0, 200, 1002))
    
    print("\n2. Checking Queue Position for Order #2 (The 50 lot seller)...")
    qty_ahead = engine.asks.get_queue_position(2)
    print(f"Order #2 has {qty_ahead} shares ahead of it.")
    
    print("\n3. Incoming Aggressive Buy (Taker)...")
    my_buy_order = Order(99, 'buy', 101.50, 120, 2000)
    status = engine.process_order(my_buy_order)
    
    print(f"\nFinal Status: {status}")