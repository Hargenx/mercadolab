from __future__ import annotations

from concurrent.futures import Executor, ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Callable

from ...api.ativo import Ativo
from ...api.dinheiro import Dinheiro
from ...api.enums import Side
from ...api.investidor import Investidor
from ...api.mercado import Mercado
from ...api.tempo import Tempo
from ...api.transacao import Transacao


PriceFunction = Callable[[Ativo, Tempo, Mercado], float]


def _decidir_par(par: tuple[Investidor, Ativo], tempo: Tempo) -> Side:
    investidor, ativo = par
    return investidor.decidir(ativo, tempo)


@dataclass(slots=True)
class ParallelScheduler:
    """
    Orquestra decisões de investidores e gera transações para um dado instante.

    O scheduler não impõe microestrutura complexa: ele apenas coleta decisões,
    agrupa intenções de compra e venda por ativo e executa pareamentos simples.
    """

    mercado: Mercado
    investidores: tuple[Investidor, ...]
    executor: Executor = field(default_factory=ThreadPoolExecutor)

    def executar_passo(
        self,
        tempo: Tempo,
        *,
        price_fn: PriceFunction,
        enforce_cash: bool = True,
    ) -> list[Transacao]:
        """
        Executa um passo da simulação para todos os ativos do mercado.

        Parameters
        ----------
        tempo:
            Instante atual da simulação.
        price_fn:
            Função que calcula o preço de um ativo em um dado instante.
        enforce_cash:
            Se verdadeiro, impede compra quando o investidor não possui saldo suficiente.

        Returns
        -------
        list[Transacao]
            Lista de transações executadas no passo atual.
        """
        ativos = self.mercado.listar_ativos()
        if not ativos or not self.investidores:
            return []

        pares = tuple(
            (investidor, ativo) for investidor in self.investidores for ativo in ativos
        )
        lados = list(self.executor.map(lambda par: _decidir_par(par, tempo), pares))

        decisoes_por_ativo: dict[str, list[tuple[Investidor, Side]]] = {
            ativo.ticker: [] for ativo in ativos
        }

        for (investidor, ativo), lado in zip(pares, lados, strict=True):
            decisoes_por_ativo[ativo.ticker].append((investidor, lado))

        transacoes: list[Transacao] = []

        for ativo in ativos:
            decisoes = decisoes_por_ativo[ativo.ticker]
            compradores = [
                investidor for investidor, lado in decisoes if lado is Side.BUY
            ]
            vendedores = [
                investidor for investidor, lado in decisoes if lado is Side.SELL
            ]

            if not compradores or not vendedores:
                continue

            preco = price_fn(ativo, tempo, self.mercado)
            transacoes_ativo = self._executar_pareamentos(
                ativo=ativo,
                tempo=tempo,
                preco=preco,
                compradores=compradores,
                vendedores=vendedores,
                enforce_cash=enforce_cash,
            )
            transacoes.extend(transacoes_ativo)

        return transacoes

    def _executar_pareamentos(
        self,
        *,
        ativo: Ativo,
        tempo: Tempo,
        preco: float,
        compradores: list[Investidor],
        vendedores: list[Investidor],
        enforce_cash: bool,
    ) -> list[Transacao]:
        """
        Executa pareamentos simples 1-para-1 entre compradores e vendedores.

        Cada pareamento gera duas transações:
        - uma do lado comprador
        - uma do lado vendedor
        """
        transacoes: list[Transacao] = []
        quantidade_pares = min(len(compradores), len(vendedores))

        for indice in range(quantidade_pares):
            comprador = compradores[indice]
            vendedor = vendedores[indice]

            if comprador is vendedor:
                continue

            valor_unitario = Dinheiro(comprador.carteira.moeda, preco)

            if enforce_cash and comprador.carteira.valor < valor_unitario.valor:
                continue

            comprador.debitar(valor_unitario)
            vendedor.creditar(Dinheiro(vendedor.carteira.moeda, preco))

            transacao_compra = Transacao(
                id=f"tx-{tempo.tick}-{ativo.ticker}-c-{indice}",
                investidor=comprador,
                ativo=ativo,
                tempo=tempo,
                lado=Side.BUY,
                preco=preco,
                quantidade=1,
                ordem_id="",
            )

            transacao_venda = Transacao(
                id=f"tx-{tempo.tick}-{ativo.ticker}-v-{indice}",
                investidor=vendedor,
                ativo=ativo,
                tempo=tempo,
                lado=Side.SELL,
                preco=preco,
                quantidade=1,
                ordem_id="",
            )

            transacoes.append(transacao_compra)
            transacoes.append(transacao_venda)

            self._notificar_transacao(comprador, transacao_compra)
            self._notificar_transacao(vendedor, transacao_venda)

        return transacoes

    @staticmethod
    def _notificar_transacao(investidor: Investidor, transacao: Transacao) -> None:
        """
        Executa o hook pós-transação do investidor de forma tolerante a falhas.
        """
        try:
            investidor.on_transacao(transacao)
        except Exception:
            pass


def make_executor(max_workers: int | None = None) -> Executor:
    """
    Cria um executor padrão para o scheduler.
    """
    return ThreadPoolExecutor(max_workers=max_workers)
