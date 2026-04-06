from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from mercadolab.api.ativo import Ativo
from mercadolab.api.posicao import Posicao


@dataclass(slots=True)
class Carteira:
    """Representa o estado patrimonial de um participante no mercado."""

    caixa: Decimal = Decimal("0")
    posicoes: dict[str, Posicao] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.caixa < 0:
            raise ValueError("caixa não pode ser negativo.")

    def obter_posicao(self, ativo: Ativo) -> Posicao | None:
        return self.posicoes.get(ativo.ticker)

    def garantir_posicao(self, ativo: Ativo) -> Posicao:
        posicao = self.obter_posicao(ativo)
        if posicao is None:
            posicao = Posicao(ativo=ativo)
            self.posicoes[ativo.ticker] = posicao
        return posicao

    def possui_ativo(self, ativo: Ativo) -> bool:
        posicao = self.obter_posicao(ativo)
        return posicao is not None and not posicao.zerada()

    def aplicar_compra(self, ativo: Ativo, quantidade: int, preco: Decimal) -> None:
        custo_total = preco * Decimal(quantidade)

        if custo_total > self.caixa:
            raise ValueError("caixa insuficiente para realizar a compra.")

        posicao = self.garantir_posicao(ativo)
        posicao.aplicar_compra(quantidade, preco)
        self.caixa -= custo_total

    def aplicar_venda(self, ativo: Ativo, quantidade: int, preco: Decimal) -> None:
        posicao = self.obter_posicao(ativo)

        if posicao is None or posicao.zerada():
            raise ValueError("não há posição disponível para venda.")

        posicao.aplicar_venda(quantidade, preco)
        self.caixa += preco * Decimal(quantidade)

        if posicao.zerada():
            del self.posicoes[ativo.ticker]
