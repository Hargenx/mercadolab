from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from uuid import UUID, uuid4

from mercadolab.api.ativo import Ativo
from mercadolab.api.ordem import LadoOrdem, Ordem
from mercadolab.api.tempo import Tempo


@dataclass(frozen=True, slots=True)
class Transacao:
    """Representa a execução de uma negociação entre uma ordem de compra e uma de venda."""

    ativo: Ativo
    quantidade: int
    preco: Decimal
    ordem_compra: Ordem
    ordem_venda: Ordem
    tempo: Tempo
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if self.quantidade <= 0:
            raise ValueError("quantidade deve ser maior que zero.")
        if self.preco <= 0:
            raise ValueError("preco deve ser maior que zero.")
        if self.ordem_compra is self.ordem_venda:
            raise ValueError("ordem_compra e ordem_venda devem ser ordens distintas.")
        if self.ordem_compra.lado is not LadoOrdem.COMPRA:
            raise ValueError("ordem_compra deve ser do lado de compra.")
        if self.ordem_venda.lado is not LadoOrdem.VENDA:
            raise ValueError("ordem_venda deve ser do lado de venda.")
        if self.ordem_compra.ativo != self.ordem_venda.ativo:
            raise ValueError("as ordens da transação devem referenciar o mesmo ativo.")
        if (
            self.ordem_compra.ativo != self.ativo
            or self.ordem_venda.ativo != self.ativo
        ):
            raise ValueError(
                "as ordens da transação devem referenciar o mesmo ativo da transação."
            )
        if not self.ativo.validar_quantidade(self.quantidade):
            raise ValueError("quantidade inválida para o lote do ativo.")
        if not self.ativo.validar_preco(self.preco):
            raise ValueError("preço inválido para o tick size do ativo.")

    @property
    def valor_total(self) -> Decimal:
        return self.preco * Decimal(self.quantidade)
