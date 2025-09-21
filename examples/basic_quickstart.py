"""
Exemplo rápido de uso da biblioteca (sem CLI).
"""
from mercadolab.core.simulation import Simulation
from mercadolab.plugins.random_trader import RandomTrader

if __name__ == "__main__":
    sim = Simulation(seed=42)
    sim.add_agent(RandomTrader(name="alice"))
    sim.run(steps=50)
    df = sim.to_frame()
    print(df.tail())