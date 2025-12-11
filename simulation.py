import heapq
import random
import csv
from dataclasses import dataclass, field
from typing import Any


@dataclass
class NetworkConfig:
    name: str
    mean_latency_ms: float
    std_dev_latency_ms: float
    packet_loss_rate: float

class LatencySimulator:
    def __init__(self, config: NetworkConfig, seed: int = None):
        self.config = config
        self.random = random.Random(seed)

    def next_latency_ms(self) -> float:
        return max(0.1, self.random.gauss(self.config.mean_latency_ms, self.config.std_dev_latency_ms))

@dataclass
class Order:
    order_id: int
    side: str 
    price: float
    quantity: int
    timestamp: int

@dataclass
class MarketEvent:
    timestamp: int
    event_type: str 
    order_id: int
    price: float = 0.0
    qty: int = 0
    side: str = '' 

class MarketDataReplayer:
    def __init__(self, filename: str):
        self.filename = filename
        self._mock_events = [
            MarketEvent(timestamp=1000, event_type='ADD', order_id=1, price=99.95, qty=100, side='buy'),
            MarketEvent(timestamp=1010, event_type='ADD', order_id=2, price=100.01, qty=50, side='sell'),
            MarketEvent(timestamp=1020, event_type='ADD', order_id=3, price=100.00, qty=20, side='buy'), 
            MarketEvent(timestamp=1030, event_type='ADD', order_id=4, price=100.02, qty=75, side='sell'),
            MarketEvent(timestamp=1040, event_type='ADD', order_id=5, price=100.05, qty=30, side='buy'), 
            MarketEvent(timestamp=1050, event_type='ADD', order_id=6, price=100.03, qty=30, side='buy')
        ]

    def stream_events(self):
        yield from self._mock_events

class BookSide:
    def __init__(self):
        self._levels = {}

    def add_order(self, price, qty):
        self._levels[price] = self._levels.get(price, 0) + qty

    def remove_order(self, price, qty):
        if price in self._levels:
            self._levels[price] -= qty
            if self._levels[price] <= 0:
                del self._levels[price]

class BidBook(BookSide):
    def best_price(self):
        return max(self._levels.keys()) if self._levels else None

class AskBook(BookSide):
    def best_price(self):
        return min(self._levels.keys()) if self._levels else None

class MatchingEngine:
    def __init__(self):
        self.bids = BidBook()
        self.asks = AskBook()
        self.orders = {} 

        self.bids.add_order(99.90, 100)
        self.bids.add_order(99.95, 50)
        self.bids.add_order(100.00, 20)

        self.asks.add_order(100.10, 100)
        self.asks.add_order(100.15, 50)


    def process_order(self, order: Order):
        print(f"      [ENGINE] Processing order {order.order_id} ({order.side} {order.quantity} @ {order.price})")
        self.orders[order.order_id] = order
        if order.side == 'buy':
            self.bids.add_order(order.price, order.quantity)
        elif order.side == 'sell':
            self.asks.add_order(order.price, order.quantity)
        return "ACCEPTED" 

def apply_market_event(engine: MatchingEngine, event: MarketEvent):
    if event.event_type == 'ADD':
        if event.side == 'buy':
            engine.bids.add_order(event.price, event.qty)
        else:
            engine.asks.add_order(event.price, event.qty)




@dataclass(order=True)
class SimEvent:
    timestamp: int
    event_type: str = field(compare=False) 
    payload: Any = field(compare=False)

class Strategy:
    """Base class for User Strategies"""
    def on_market_update(self, book_state):
        return None 

class SimpleMarketMaker(Strategy):
    def __init__(self):
        self.sent_order = False

    def on_market_update(self, engine):
        best_bid = engine.bids.best_price()
        if not self.sent_order and best_bid and best_bid >= 100.00:
            print(f"    [STRATEGY] Signal triggered at {best_bid}!")
            self.sent_order = True
            return Order(999, 'buy', 100.05, 10, 0) # qty 10, ts 0 (placeholder)
        return None

class SimulationRunner:
    def __init__(self, replayer, engine, latency_sim, strategy):
        self.replayer = replayer
        self.engine = engine
        self.latency = latency_sim
        self.strategy = strategy

        self.events = []
        self.current_time = 0

        self.market_stream = replayer.stream_events()
        self._schedule_next_market_event()

    def _schedule_next_market_event(self):
        try:
            evt = next(self.market_stream)
            heapq.heappush(self.events, SimEvent(evt.timestamp, 'MARKET', evt))
        except StopIteration:
            pass 

    def run(self):
        print("\n--- SIMULATION START ---")

        while self.events:
            sim_event = heapq.heappop(self.events)
            self.current_time = sim_event.timestamp

            if sim_event.event_type == 'MARKET':
                self._handle_market_event(sim_event.payload)
                self._schedule_next_market_event() 

            elif sim_event.event_type == 'ORDER_ARRIVAL':
                self._handle_order_arrival(sim_event.payload)

    def _handle_market_event(self, market_event):
        apply_market_event(self.engine, market_event)

        print(f"[{self.current_time}] MARKET: {market_event.event_type} {market_event.qty} @ {market_event.price}")

        user_order = self.strategy.on_market_update(self.engine)

        if user_order:
            latency_ms = self.latency.next_latency_ms()
            latency_us = int(latency_ms * 1000)
            arrival_time = self.current_time + latency_us

            print(f"    [NETWORK] Order sent. Latency: {latency_ms:.2f}ms. Arrives at: {arrival_time}")

            heapq.heappush(self.events, SimEvent(arrival_time, 'ORDER_ARRIVAL', user_order))

    def _handle_order_arrival(self, order):
        print(f"[{self.current_time}] EXCHANGE: User Order Arrived! Processing...")


        status = self.engine.process_order(order)
        print(f"    [EXCHANGE] Order Status: {status}")



if __name__ == "__main__":

    p_colo = NetworkConfig("Colo", 0.5, 0.1, 0.0)

    sim_latency = LatencySimulator(p_colo, seed=42)
    sim_engine = MatchingEngine()
    sim_replayer = MarketDataReplayer("dummy.csv")
    sim_strategy = SimpleMarketMaker()

    runner = SimulationRunner(sim_replayer, sim_engine, sim_latency, sim_strategy)

    runner.run()