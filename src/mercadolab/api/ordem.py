from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from mercadolab.api.ativo import Ativo
from mercadolab.api.tempo import Tempo

if TYPE_CHECKING:
    from mercadolab.api.investidor import Investidor


class LadoOrdem(Enum):
    COMPRA = "compra"
    VENDA = "venda"


class TipoOrdem(Enum):
    MERCADO = "mercado"
    LIMITADA = "limitada"


class StatusOrdem(Enum):
    PENDENTE = "pendente"
    PARCIALMENTE_EXECUTADA = "parcialmente_executada"
    EXECUTADA = "executada"
    CANCELADA = "cancelada"
    EXPIRADA = "expirada"


@dataclass(slots=True)
class Ordem:
    """Representa uma instrução de compra ou venda de um ativo."""

    ativo: Ativo
    investidor: Investidor
    lado: LadoOrdem
    tipo: TipoOrdem
    quantidade: int
    tempo: Tempo
    preco_limite: Decimal | None = None
    id: UUID = field(default_factory=uuid4)
    status: StatusOrdem = StatusOrdem.PENDENTE
    quantidade_executada: int = 0

    def __post_init__(self) -> None:
        if self.quantidade <= 0:
            raise ValueError("quantidade deve ser maior que zero.")

        if self.tipo is TipoOrdem.LIMITADA:
            if self.preco_limite is None or self.preco_limite <= 0:
                raise ValueError("ordem limitada exige preco_limite positivo.")

        if self.tipo is TipoOrdem.MERCADO and self.preco_limite is not None:
            raise ValueError("ordem a mercado não deve ter preco_limite.")

        if not self.ativo.validar_quantidade(self.quantidade):
            raise ValueError("quantidade inválida para o lote do ativo.")

        if self.preco_limite is not None and not self.ativo.validar_preco(
            self.preco_limite
        ):
            raise ValueError("preço inválido para o tick size do ativo.")

    @property
    def quantidade_restante(self) -> int:
        return self.quantidade - self.quantidade_executada

    def esta_ativa(self) -> bool:
        return self.status in {
            StatusOrdem.PENDENTE,
            StatusOrdem.PARCIALMENTE_EXECUTADA,
        }

    def registrar_execucao(self, quantidade: int) -> None:
        if quantidade <= 0:
            raise ValueError("a quantidade executada deve ser positiva.")
        if quantidade > self.quantidade_restante:
            raise ValueError("a execução excede a quantidade restante.")
        if not self.esta_ativa():
            raise ValueError("não é possível executar uma ordem inativa.")

        self.quantidade_executada += quantidade

        if self.quantidade_executada == self.quantidade:
            self.status = StatusOrdem.EXECUTADA
        else:
            self.status = StatusOrdem.PARCIALMENTE_EXECUTADA

    def cancelar(self) -> None:
        if self.status is StatusOrdem.EXECUTADA:
            raise ValueError("não é possível cancelar uma ordem já executada.")
        if self.status is StatusOrdem.CANCELADA:
            raise ValueError("a ordem já está cancelada.")

        self.status = StatusOrdem.CANCELADA
