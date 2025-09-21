from mercadolab.core.simulation import Simulation
from mercadolab.plugins.random_trader import RandomTrader

def test_quick_run():
    sim = Simulation(seed=1)
    sim.add_agent(RandomTrader(name="test"))
    sim.run(steps=5)
    assert len(sim.log) == 5