from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from mercadolab import Ativo, Dinheiro, Investidor, Mercado, Side, Tempo, Transacao
from mercadolab.internal.engine import ParallelScheduler, make_executor


@dataclass(slots=True)
class BasicMarketResult:
    """Resultado da execução de um cenário básico de mercado."""

    mercado: Mercado
    investidores: tuple[Investidor, ...]
    transacoes: list[Transacao]
    ticks_executados: int


class CompradorBasico(Investidor):
    """Investidor simples que sempre decide comprar."""

    def decidir(self, ativo: Ativo, tempo: Tempo) -> Side:
        return Side.BUY


class VendedorBasico(Investidor):
    """Investidor simples que sempre decide vender."""

    def decidir(self, ativo: Ativo, tempo: Tempo) -> Side:
        return Side.SELL


@dataclass(slots=True)
class BasicMarketScenario:
    """Cenário básico de referência para o MercadoLab."""

    n_compradores: int = 50
    n_vendedores: int = 50
    ativos: Sequence[str] = ("AAA11", "BBB3", "CCC4")
    ticks: int = 10
    saldo_inicial_comprador: float = 10_000.0
    saldo_inicial_vendedor: float = 0.0
    moeda: str = "BRL"
    preco_inicial: float = 100.0
    max_workers: int | None = 8

    def criar_mercado(self) -> Mercado:
        mercado = Mercado("basic_market")
        for ticker in self.ativos:
            mercado.adicionar_ativo(Ativo(ticker))
        return mercado

    def criar_investidores(self) -> tuple[Investidor, ...]:
        compradores = tuple(
            CompradorBasico(
                id=f"b{i}",
                nome=f"Comprador {i}",
                carteira=Dinheiro(self.moeda, self.saldo_inicial_comprador),
                perfil="comprador_basico",
            )
            for i in range(self.n_compradores)
        )
        vendedores = tuple(
            VendedorBasico(
                id=f"s{i}",
                nome=f"Vendedor {i}",
                carteira=Dinheiro(self.moeda, self.saldo_inicial_vendedor),
                perfil="vendedor_basico",
            )
            for i in range(self.n_vendedores)
        )
        return compradores + vendedores

    def price_fn(self, ativo: Ativo, tempo: Tempo, mercado: Mercado) -> float:
        """Função de preço simples usada pelo cenário básico."""
        return self.preco_inicial + float(tempo.tick - 1)

    def executar(self) -> BasicMarketResult:
        mercado = self.criar_mercado()
        investidores = self.criar_investidores()
        transacoes: list[Transacao] = []

        with make_executor(max_workers=self.max_workers) as executor:
            scheduler = ParallelScheduler(
                mercado=mercado,
                investidores=investidores,
                executor=executor,
            )

            for tick in range(1, self.ticks + 1):
                tempo = Tempo(tick)
                transacoes.extend(
                    scheduler.executar_passo(
                        tempo,
                        price_fn=self.price_fn,
                        enforce_cash=True,
                    )
                )

        return BasicMarketResult(
            mercado=mercado,
            investidores=investidores,
            transacoes=transacoes,
            ticks_executados=self.ticks,
        )
