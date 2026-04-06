from __future__ import annotations

from dataclasses import dataclass, field

from mercadolab.api.investidor import Investidor
from mercadolab.api.mercado import Mercado
from mercadolab.api.ordem import Ordem
from mercadolab.api.tempo import Tempo
from mercadolab.api.transacao import Transacao


@dataclass(slots=True)
class Simulacao:
    """Coordena a execução temporal de um cenário de mercado sem impor estratégias."""

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
