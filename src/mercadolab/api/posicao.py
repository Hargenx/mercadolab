from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from mercadolab.api.ativo import Ativo


@dataclass(slots=True)
class Posicao:
    """Representa a quantidade mantida de um ativo e seu preço médio."""

    ativo: Ativo
    quantidade: int = 0
    preco_medio: Decimal = Decimal("0")

    def __post_init__(self) -> None:
        if self.quantidade < 0:
            raise ValueError("quantidade não pode ser negativa.")
        if self.preco_medio < 0:
            raise ValueError("preco_medio não pode ser negativo.")
        if self.quantidade == 0 and self.preco_medio != 0:
            raise ValueError("posição zerada deve ter preco_medio igual a zero.")

    def aplicar_compra(self, quantidade: int, preco: Decimal) -> None:
        if quantidade <= 0:
            raise ValueError("quantidade de compra deve ser positiva.")
        if preco <= 0:
            raise ValueError("preço de compra deve ser positivo.")
        if not self.ativo.validar_quantidade(quantidade):
            raise ValueError("quantidade inválida para o lote do ativo.")
        if not self.ativo.validar_preco(preco):
            raise ValueError("preço inválido para o tick size do ativo.")

        custo_atual = self.preco_medio * Decimal(self.quantidade)
        custo_novo = preco * Decimal(quantidade)
        nova_quantidade = self.quantidade + quantidade

        self.preco_medio = (custo_atual + custo_novo) / Decimal(nova_quantidade)
        self.quantidade = nova_quantidade

    def aplicar_venda(self, quantidade: int, preco: Decimal) -> None:
        if quantidade <= 0:
            raise ValueError("quantidade de venda deve ser positiva.")
        if preco <= 0:
            raise ValueError("preço de venda deve ser positivo.")
        if quantidade > self.quantidade:
            raise ValueError("não é possível vender mais do que a posição atual.")
        if not self.ativo.validar_quantidade(quantidade):
            raise ValueError("quantidade inválida para o lote do ativo.")
        if not self.ativo.validar_preco(preco):
            raise ValueError("preço inválido para o tick size do ativo.")

        self.quantidade -= quantidade

        if self.quantidade == 0:
            self.preco_medio = Decimal("0")

    def zerada(self) -> bool:
        return self.quantidade == 0
