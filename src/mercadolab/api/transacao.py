from __future__ import annotations

from dataclasses import dataclass

from .ativo import Ativo
from .enums import Side
from .investidor import Investidor
from .tempo import Tempo


@dataclass(frozen=True, slots=True)
class Transacao:
    """Evento imutável que representa uma transação em um cenário de mercado."""

    id: str
    investidor: Investidor
    ativo: Ativo
    tempo: Tempo
    lado: Side
    preco: float
    quantidade: int
    ordem_id: str = ""

    def valor_total(self) -> float:
        return self.preco * float(self.quantidade)

    def eh_compra(self) -> bool:
        return self.lado is Side.BUY

    def eh_venda(self) -> bool:
        return self.lado is Side.SELL

    def __repr__(self) -> str:
        return (
            f"Transacao(id={self.id}, "
            f"investidor={self.investidor}, "
            f"ativo={self.ativo}, "
            f"tempo={self.tempo}, "
            f"lado={self.lado}, "
            f"preco={self.preco}, "
            f"quantidade={self.quantidade}, "
            f"ordem_id={self.ordem_id})"
        )