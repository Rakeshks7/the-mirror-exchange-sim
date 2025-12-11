# The Mirror: Deterministic Exchange Simulator

### A High-Fidelity Market Microstructure Simulator for HFT Algorithms

**The Problem:** Standard backtesters assume zero latency, infinite liquidity, and perfect execution.
**The Solution:** "The Mirror" simulates the chaotic reality of live markets—**Network Jitter**, **Queue Position**, and **Packet Loss**.

## 🚀 Key Features

* **Level 3 Matching Engine:** Full Price-Time Priority Limit Order Book (LOB).
* **Realistic Network Modeling:** Gamma Distribution for latency (Co-lo to WiFi).
* **The "Crystal Ball":** Tracks exactly where your order sits in the queue.
* **100% Deterministic:** Seeded RNG ensures perfect regression testing.

## 🛠️ Architecture

1. **`MatchingEngine`:** Manages the LOB and FIFO logic.
2. **`LatencySimulator`:** Intercepts orders with seeded network delays.
3. **`MarketDataReplayer`:** Streams Tick-by-Tick (L3) data.
4. **`SimulationRunner`:** Priority Queue event loop orchestrating time.

## 📦 Usage

1. **Install:** `pip install -r requirements.txt`
2. **Run Sim:** `python src/simulation.py`
3. **Test:** `python tests/test_determinism.py`

## ⚠️ Disclaimer
For educational and research purposes only. Not financial advice.

## License
MIT License