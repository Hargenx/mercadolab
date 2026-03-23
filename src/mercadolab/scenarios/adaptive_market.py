from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

from mercadolab import Ativo, Dinheiro, Investidor, Mercado, Side, Tempo, Transacao
from mercadolab.internal.engine import ParallelScheduler, make_executor


@dataclass(slots=True)
class AdaptiveMarketResult:
    """Resultado da execução do cenário adaptativo."""

    mercado: Mercado
    investidores: tuple[Investidor, ...]
    transacoes: list[Transacao]
    ticks_executados: int
    sinais_externos: list[float]


@dataclass(slots=True)
class AdaptiveMarketConfig:
    """Parâmetros do cenário adaptativo."""

    n_agentes: int = 100
    ativos: Sequence[str] = ("AAA11", "BBB3", "CCC4")
    ticks: int = 30
    moeda: str = "BRL"
    saldo_inicial: float = 10_000.0
    preco_inicial: float = 100.0
    max_workers: int | None = 8

    tamanho_vizinhanca: int = 5

    peso_vizinhos: float = 0.5
    peso_carteira: float = 0.3
    peso_externo: float = 0.2


class InvestidorAdaptativo(Investidor):
    """Investidor que decide com base em vizinhos, carteira e sinal externo."""

    def __init__(
        self,
        *,
        id: str,
        nome: str,
        carteira: Dinheiro,
        perfil: str = "adaptativo",
        saldo_referencia: float = 10_000.0,
        peso_vizinhos: float = 0.5,
        peso_carteira: float = 0.3,
        peso_externo: float = 0.2,
        vies_pessoal: float = 0.0,
    ) -> None:
        super().__init__(id=id, nome=nome, carteira=carteira, perfil=perfil)
        self.saldo_referencia = saldo_referencia
        self.peso_vizinhos = peso_vizinhos
        self.peso_carteira = peso_carteira
        self.peso_externo = peso_externo
        self.vies_pessoal = vies_pessoal

        self.vizinhos: list["InvestidorAdaptativo"] = []
        self.sinal_externo_atual: float = 0.0

    def decidir(self, ativo: Ativo, tempo: Tempo) -> Side:
        score_vizinhos = self._score_vizinhos(ativo, tempo)
        score_carteira = self._score_carteira()
        score_externo = self.sinal_externo_atual

        score_total = (
            self.peso_vizinhos * score_vizinhos
            + self.peso_carteira * score_carteira
            + self.peso_externo * score_externo
            + self.vies_pessoal
        )

        return Side.BUY if score_total >= 0 else Side.SELL

    def _score_vizinhos(self, ativo: Ativo, tempo: Tempo) -> float:
        if not self.vizinhos:
            return 0.0

        saldo = 0
        for vizinho in self.vizinhos:
            decisao = vizinho.decidir_base(ativo, tempo)
            saldo += 1 if decisao is Side.BUY else -1

        return saldo / len(self.vizinhos)

    def _score_carteira(self) -> float:
        if self.saldo_referencia <= 0:
            return 0.0

        proporcao = self.carteira.valor / self.saldo_referencia

        if proporcao > 1.05:
            return 1.0
        if proporcao < 0.95:
            return -1.0
        return 0.0

    def decidir_base(self, ativo: Ativo, tempo: Tempo) -> Side:
        """
        Decisão simplificada para ser usada pelos vizinhos sem recursão infinita.
        """
        score_carteira = self._score_carteira()
        score_externo = self.sinal_externo_atual
        score_total = (
            self.peso_carteira * score_carteira + self.peso_externo * score_externo + self.vies_pessoal
        )
        return Side.BUY if score_total >= 0 else Side.SELL


@dataclass(slots=True)
class AdaptiveMarketScenario:
    """Cenário em que agentes decidem com base em vizinhos, carteira e fator externo."""

    config: AdaptiveMarketConfig = field(default_factory=AdaptiveMarketConfig)

    def criar_mercado(self) -> Mercado:
        mercado = Mercado("adaptive_market")
        for ticker in self.config.ativos:
            mercado.adicionar_ativo(Ativo(ticker))
        return mercado

    def criar_investidores(self) -> tuple[InvestidorAdaptativo, ...]:
        investidores = tuple(
            InvestidorAdaptativo(
                id=f"a{i}",
                nome=f"Agente {i}",
                carteira=Dinheiro(self.config.moeda, self.config.saldo_inicial),
                saldo_referencia=self.config.saldo_inicial,
                peso_vizinhos=self.config.peso_vizinhos,
                peso_carteira=self.config.peso_carteira,
                peso_externo=self.config.peso_externo,
                vies_pessoal=0.35 if i % 2 == 0 else -0.35,
            )
            for i in range(self.config.n_agentes)
        )
        self._configurar_vizinhanca(investidores)
        return investidores

    def _configurar_vizinhanca(
        self,
        investidores: tuple[InvestidorAdaptativo, ...],
    ) -> None:
        n = len(investidores)
        k = min(self.config.tamanho_vizinhanca, max(0, n - 1))

        for i, investidor in enumerate(investidores):
            vizinhos: list[InvestidorAdaptativo] = []
            for deslocamento in range(1, k + 1):
                vizinhos.append(investidores[(i + deslocamento) % n])
            investidor.vizinhos = vizinhos

    def sinal_externo(self, tick: int) -> float:
        """
        Sinal externo simples e determinístico:
        alterna entre positivo e negativo a cada bloco de 5 ticks.
        """
        bloco = (tick - 1) // 5
        return 1.0 if bloco % 2 == 0 else -1.0

    def price_fn(self, ativo: Ativo, tempo: Tempo, mercado: Mercado) -> float:
        """
        Função de preço simples para o cenário adaptativo.
        """
        return self.config.preco_inicial + 0.5 * float(tempo.tick - 1)

    def executar(self) -> AdaptiveMarketResult:
        mercado = self.criar_mercado()
        investidores = self.criar_investidores()
        transacoes: list[Transacao] = []
        sinais_externos: list[float] = []

        with make_executor(max_workers=self.config.max_workers) as executor:
            scheduler = ParallelScheduler(
                mercado=mercado,
                investidores=investidores,
                executor=executor,
            )

            for tick in range(1, self.config.ticks + 1):
                tempo = Tempo(tick)
                sinal = self.sinal_externo(tick)
                sinais_externos.append(sinal)

                for investidor in investidores:
                    investidor.sinal_externo_atual = sinal

                transacoes.extend(
                    scheduler.executar_passo(
                        tempo,
                        price_fn=self.price_fn,
                        enforce_cash=True,
                    )
                )

        return AdaptiveMarketResult(
            mercado=mercado,
            investidores=investidores,
            transacoes=transacoes,
            ticks_executados=self.config.ticks,
            sinais_externos=sinais_externos,
        )
