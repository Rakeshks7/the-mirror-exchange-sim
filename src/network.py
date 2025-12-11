import numpy as np
from dataclasses import dataclass

@dataclass
class NetworkConfig:
    name: str
    base_latency_ms: float
    jitter_scale: float
    drop_probability: float

class LatencySimulator:
    def __init__(self, config: NetworkConfig, seed: int):
        self.config = config
        self.rng = np.random.default_rng(seed)
        
    def next_latency_ms(self) -> float:
        if self.rng.random() < self.config.drop_probability:
            return -1.0 
            
        jitter = self.rng.gamma(shape=2.0, scale=self.config.jitter_scale)
        return self.config.base_latency_ms + jitter