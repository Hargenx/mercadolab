import argparse
import sys
from .core.simulation import Simulation
from .plugins import load_plugins

def _cmd_quickstart(args: argparse.Namespace) -> int:
    # Simple 10-step simulation with a single RandomTrader plugin agent
    plugins = load_plugins()
    if "random-trader" not in plugins:
        print("Plugin 'random-trader' não encontrado. Instale ou verifique a entry point.", file=sys.stderr)
        return 2
    AgentCls = plugins["random-trader"]
    sim = Simulation(seed=args.seed)
    sim.add_agent(AgentCls(name="alice"))
    sim.run(steps=args.steps)
    df = sim.to_frame()
    print(df.tail())
    return 0

def _cmd_plugins(args: argparse.Namespace) -> int:
    plugins = load_plugins()
    if not plugins:
        print("Nenhum plugin encontrado.")
        return 0
    print("Plugins disponíveis:")
    for name, cls in plugins.items():
        print(f"- {name}: {cls.__module__}.{cls.__name__}")
    return 0

def _cmd_run(args: argparse.Namespace) -> int:
    from .core.investidor import BaseAgent
    from .core.market import Market
    # Minimal run without plugins (user code could subclass BaseAgent)
    class HoldAgent(BaseAgent):
        def decide(self, market):
            return None
    sim = Simulation(seed=args.seed)
    sim.market = Market(price0=args.price0)
    for i in range(args.n_agents):
        sim.add_agent(HoldAgent(name=f"agent{i+1}"))
    sim.run(steps=args.steps)
    print(sim.to_frame().tail())
    return 0

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="mercadolab",
        description="MercadoLab — laboratório ABM para mercados."
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p1 = sub.add_parser("quickstart", help="Roda um exemplo rápido usando o plugin RandomTrader.")
    p1.add_argument("--steps", type=int, default=50)
    p1.add_argument("--seed", type=int, default=42)
    p1.set_defaults(func=_cmd_quickstart)

    p2 = sub.add_parser("plugins", help="Lista plugins detectados via entry-points.")
    p2.set_defaults(func=_cmd_plugins)

    p3 = sub.add_parser("run", help="Roda uma simulação mínima (sem plugins).")
    p3.add_argument("--steps", type=int, default=50)
    p3.add_argument("--seed", type=int, default=42)
    p3.add_argument("--n-agents", type=int, default=3)
    p3.add_argument("--price0", type=float, default=100.0)
    p3.set_defaults(func=_cmd_run)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())