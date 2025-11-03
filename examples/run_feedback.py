from mercadolab import Dinheiro, Tempo, Ativo, Side, Fundamentalista, Especulativo
from mercadolab.internal.engine import make_executor, ParallelScheduler


# --- AGENTES PARA O TESTE (iguais ao colab em espírito) ---
class Buyer(Fundamentalista):
    def decidir(self, ativo: Ativo, tempo: Tempo) -> Side:
        return Side.BUY


class Seller(Especulativo):
    def decidir(self, ativo: Ativo, tempo: Tempo) -> Side:
        return Side.SELL


def main():
    ativos = [Ativo("AAA11")]

    # população mista
    investidores = []
    for i in range(50):  # 50 compradores
        investidores.append(Buyer(f"b{i}", f"Buyer{i}", Dinheiro("BRL", 0)))
    for j in range(50):  # 50 vendedores
        investidores.append(Seller(f"s{j}", f"Seller{j}", Dinheiro("BRL", 0)))

    # estado do modelo
    preco = 100.0
    k = 0.1  # sensibilidade ao excesso de demanda
    ticks = 40

    with make_executor("thread", max_workers=32) as ex:
        sched = ParallelScheduler(executor=ex, price_fn=lambda ativo, tempo: preco)

        for t in range(1, ticks + 1):
            tempo = Tempo(t)
            trades = sched.run_tick(tempo, ativos, investidores)

            # contagem dos lados (BUY/SELL)
            buys = sum(1 for tx in trades if tx.lado is Side.BUY)
            sells = sum(1 for tx in trades if tx.lado is Side.SELL)

            excess = buys - sells
            preco = preco + k * excess

            print(
                f"t={t:02d}  trades={len(trades):3d}  excess={excess:+4d}  price={preco:.2f}"
            )


if __name__ == "__main__":
    main()
