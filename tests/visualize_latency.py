import matplotlib.pyplot as plt
import numpy as np

def plot_latency_distribution():
    rng = np.random.default_rng(seed=42)
    shape, scale = 2.0, 2.0  
    base_latency = 5.0       
    
    data = base_latency + rng.gamma(shape, scale, 10000)
    
    plt.figure(figsize=(10, 6))
    
    count, bins, ignored = plt.hist(data, bins=50, density=True, alpha=0.6, color='#007acc', label='Simulated Packets')
    
    plt.axvline(base_latency, color='red', linestyle='--', linewidth=2, label='Physics Limit (Base Latency)')
    
    plt.title('Network Jitter Model: The "Long Tail" of Latency', fontsize=14, fontweight='bold')
    plt.xlabel('Latency (ms)', fontsize=12)
    plt.ylabel('Probability Density', fontsize=12)
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.annotate('Packet Spikes (Tail Latency)\nRisk Zone for Algos', 
                 xy=(15, 0.05), xytext=(20, 0.1),
                 arrowprops=dict(facecolor='black', shrink=0.05))

    print("Generating 'latency_distribution.png'...")
    plt.savefig('latency_distribution.png')
    plt.show()

if __name__ == "__main__":
    plot_latency_distribution()