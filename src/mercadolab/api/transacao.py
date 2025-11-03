from __future__ import annotations  # <- evita avaliar hints em runtime
from dataclasses import dataclass

from mercadolab.api.ativo import Ativo
from mercadolab.api.investidor import Investidor
from mercadolab.api.tempo import Tempo

from .enums import Side

# NÃO importe Investidor/Ativo/Tempo em runtime para evitar ciclo


@dataclass(frozen=True, slots=True)
class Transacao:
    """
    <<event>> — liga Investidor (trader), Ativo (asset) e Tempo (clock).
    As anotações são forward refs graças ao __future__ acima.
    """

    id: str
    trader: "Investidor"
    asset: "Ativo"
    clock: "Tempo"
    lado: Side
    preco: float
    quantidade: int
    ordemId: str = ""

    def notional(self) -> float:
        return self.preco * float(self.quantidade)

    def isBuy(self) -> bool:
        return self.lado is Side.BUY

    def isSell(self) -> bool:
        return self.lado is Side.SELL
