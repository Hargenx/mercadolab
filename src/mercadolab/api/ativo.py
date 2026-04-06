from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


class TipoAtivo(Enum):
    ACAO = "acao"
    ETF = "etf"
    FII = "fii"
    FUTURO = "futuro"
    CRIPTOATIVO = "criptoativo"
    INDICE = "indice"
    OUTRO = "outro"


@dataclass(frozen=True, slots=True)
class Ativo:
    """Representa um instrumento negociável no mercado simulado."""
    ticker: str
    tipo: TipoAtivo
    nome: str = ""
    moeda: str = "BRL"
    tick_size: Decimal = Decimal("0.01")
    lote_padrao: int = 1
    negociavel: bool = True

    def __post_init__(self) -> None:
        if not self.ticker.strip():
            raise ValueError("ticker não pode ser vazio.")
        if self.tick_size <= 0:
            raise ValueError("tick_size deve ser positivo.")
        if self.lote_padrao <= 0:
            raise ValueError("lote_padrao deve ser maior que zero.")

    def validar_quantidade(self, quantidade: int) -> bool:
        """Valida se a quantidade é positiva e múltipla do lote padrão."""
        return quantidade > 0 and quantidade % self.lote_padrao == 0

    def validar_preco(self, preco: Decimal) -> bool:
        """Valida se o preço é positivo e compatível com o tick size."""
        razao = preco / self.tick_size
        return preco > 0 and razao == razao.to_integral_value()
