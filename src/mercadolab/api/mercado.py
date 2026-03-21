from __future__ import annotations

from dataclasses import dataclass, field

from .ativo import Ativo


@dataclass(slots=True)
class Mercado:
    """Representa um conjunto de ativos disponíveis em um cenário de mercado."""

    nome: str
    _ativos: dict[str, Ativo] = field(default_factory=dict, repr=False)

    def adicionar_ativo(self, ativo: Ativo) -> None:
        if ativo.ticker in self._ativos:
            raise ValueError(f"Já existe um ativo com ticker '{ativo.ticker}'.")
        self._ativos[ativo.ticker] = ativo

    def remover_ativo(self, ticker: str) -> None:
        if ticker not in self._ativos:
            raise KeyError(f"Ativo não encontrado: {ticker}")
        self._ativos.pop(ticker)

    def obter_ativo(self, ticker: str) -> Ativo:
        try:
            return self._ativos[ticker]
        except KeyError as exc:
            raise KeyError(f"Ativo não encontrado: {ticker}") from exc

    def listar_ativos(self) -> tuple[Ativo, ...]:
        return tuple(self._ativos.values())
