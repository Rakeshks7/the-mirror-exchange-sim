	import unittest
import logging
from dataclasses import dataclass
import sys


import numpy as np

class LatencySimulator:
    """The source of randomness we need to control."""
    def __init__(self, seed):
        self.rng = np.random.default_rng(seed)

    def next_latency(self):
        return self.rng.gamma(shape=2.0, scale=0.5)

class MockSimulation:
    """A minimal wrapper to simulate a full run."""
    def __init__(self, seed):
        self.latency_sim = LatencySimulator(seed)
        self.execution_log = []

    def run(self, iterations=100):
        """Simulates 100 packets and records when they arrived."""
        current_time = 0
        for _ in range(iterations):
            delay = self.latency_sim.next_latency()
            current_time += delay

            self.execution_log.append(current_time)
        return self.execution_log


class TestExchangeDeterminism(unittest.TestCase):

    def setUp(self):
        print("\n--- Starting New Test Case ---")

    def test_reproducibility(self):
        """
        The 1% Challenge:
        Running the sim twice with Seed 42 must yield bit-perfect identical results.
        """
        SEED = 42
        print(f"Running Simulation A (Seed={SEED})...")
        sim_a = MockSimulation(seed=SEED)
        results_a = sim_a.run()

        print(f"Running Simulation B (Seed={SEED})...")
        sim_b = MockSimulation(seed=SEED)
        results_b = sim_b.run()

        self.assertEqual(len(results_a), len(results_b))

        for i in range(len(results_a)):
            self.assertEqual(
                results_a[i],
                results_b[i],
                f"Mismatch at index {i}! The butterfly effect has occurred."
            )

        print("SUCCESS: Simulation A and B are identical.")

    def test_randomness(self):
        """
        Control Test:
        Changing the seed MUST produce different results.
        """
        print("Running Simulation C (Seed=999)...")
        sim_c = MockSimulation(seed=999)
        results_c = sim_c.run()

        print("Comparing Seed 42 vs Seed 999...")
        self.assertNotEqual(
            results_c[0],
            0.0,
            "Simulation C failed to generate random data"
        )

        sim_a = MockSimulation(seed=42)
        results_a = sim_a.run()
        self.assertNotEqual(results_a, results_c)

        print("SUCCESS: Different seeds produced different market realities.")

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
