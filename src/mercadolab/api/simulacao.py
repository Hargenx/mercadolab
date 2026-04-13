from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Callable

from mercadolab.api.investidor import Investidor
from mercadolab.api.mercado import Mercado
from mercadolab.api.ordem import Ordem
from mercadolab.api.tempo import Tempo
from mercadolab.api.transacao import Transacao


GeradorOrdens = Callable[
    [Investidor, Mercado, Tempo], list[Ordem] | tuple[Ordem, ...] | None
]


@dataclass(slots=True)
class Simulacao:
    """Coordena a execução temporal de um cenário de mercado sem impor estratégias.

    A simulação pode operar em modo serial ou, opcionalmente, coletar ordens de forma
    concorrente. A concorrência pode melhorar desempenho em alguns cenários, mas pode
    comprometer a reprodutibilidade estrita quando a geração de ordens depende de um
    gerador pseudoaleatório global, mesmo com seed definido.
    """

    mercado: Mercado
    tempo_atual: Tempo = field(default_factory=lambda: Tempo(tick=0))
    investidores: list[Investidor] = field(default_factory=list)

    def adicionar_investidor(self, investidor: Investidor) -> None:
        self.investidores.append(investidor)

    def listar_investidores(self) -> tuple[Investidor, ...]:
        return tuple(self.investidores)

    def avancar_tempo(self) -> None:
        self.tempo_atual = self.tempo_atual.proximo()

    def submeter_ordens(self, ordens: list[Ordem]) -> tuple[Transacao, ...]:
        transacoes: list[Transacao] = []

        for ordem in ordens:
            transacoes.extend(self.mercado.submeter_ordem(ordem))

        return tuple(transacoes)

    def executar_tick(self, ordens: list[Ordem]) -> tuple[Transacao, ...]:
        transacoes = self.submeter_ordens(ordens)
        self.avancar_tempo()
        return transacoes

    def executar(self, ordens_por_tick: list[list[Ordem]]) -> tuple[Transacao, ...]:
        if ordens_por_tick is None:
            raise ValueError("ordens_por_tick não pode ser None.")

        todas_transacoes: list[Transacao] = []

        for ordens in ordens_por_tick:
            todas_transacoes.extend(self.executar_tick(ordens))

        return tuple(todas_transacoes)

    def coletar_ordens(
        self,
        gerador_ordens: GeradorOrdens,
        concorrente: bool = False,
        max_workers: int | None = None,
    ) -> list[Ordem]:
        """Coleta ordens dos investidores usando uma função externa.

        Em modo serial, a ordem de chamada é previsível e favorece reprodutibilidade.
        Em modo concorrente, a coleta pode ser mais rápida, mas a ordem de execução das
        tarefas pode variar e alterar o consumo de números pseudoaleatórios globais.
        """
        investidores_ativos = [i for i in self.investidores if i.ativo]

        if not concorrente:
            ordens: list[Ordem] = []
            for investidor in investidores_ativos:
                resultado = gerador_ordens(investidor, self.mercado, self.tempo_atual)
                if resultado:
                    ordens.extend(resultado)
            return ordens

        ordens_concorrentes: list[Ordem] = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futuros = [
                executor.submit(
                    gerador_ordens, investidor, self.mercado, self.tempo_atual
                )
                for investidor in investidores_ativos
            ]
            for futuro in futuros:
                resultado = futuro.result()
                if resultado:
                    ordens_concorrentes.extend(resultado)

        return ordens_concorrentes

    def executar_tick_com_gerador(
        self,
        gerador_ordens: GeradorOrdens,
        concorrente: bool = False,
        max_workers: int | None = None,
    ) -> tuple[Transacao, ...]:
        """Coleta ordens com um gerador externo e executa um tick.

        Use o modo concorrente com cautela em cenários que dependem de reprodutibilidade
        estrita baseada em random.seed global.
        """
        ordens = self.coletar_ordens(
            gerador_ordens=gerador_ordens,
            concorrente=concorrente,
            max_workers=max_workers,
        )
        return self.executar_tick(ordens)
