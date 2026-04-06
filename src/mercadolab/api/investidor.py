from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from uuid import UUID, uuid4

from mercadolab.api.ativo import Ativo
from mercadolab.api.carteira import Carteira
from mercadolab.api.ordem import LadoOrdem, Ordem, TipoOrdem
from mercadolab.api.tempo import Tempo


@dataclass(slots=True)
class Investidor:
    """Representa um participante do mercado simulado."""

    nome: str
    carteira: Carteira = field(default_factory=Carteira)
    ativo: bool = True
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not self.nome.strip():
            raise ValueError("nome não pode ser vazio.")

    def ativar(self) -> None:
        self.ativo = True

    def desativar(self) -> None:
        self.ativo = False

    def emitir_ordem(
        self,
        ativo: Ativo,
        lado: LadoOrdem,
        tipo: TipoOrdem,
        quantidade: int,
        tempo: Tempo,
        preco_limite: Decimal | None = None,
    ) -> Ordem:
        if not self.ativo:
            raise ValueError("investidor inativo não pode emitir ordens.")

        return Ordem(
            investidor=self,
            ativo=ativo,
            lado=lado,
            tipo=tipo,
            quantidade=quantidade,
            tempo=tempo,
            preco_limite=preco_limite,
        )
