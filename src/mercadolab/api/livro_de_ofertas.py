from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from mercadolab.api.ativo import Ativo
from mercadolab.api.ordem import LadoOrdem, Ordem, TipoOrdem


@dataclass(slots=True)
class LivroDeOfertas:
    """Representa o conjunto de ordens ativas de compra e venda de um ativo."""

    ativo: Ativo
    ordens_compra: list[Ordem] = field(default_factory=list)
    ordens_venda: list[Ordem] = field(default_factory=list)

    def adicionar_ordem(self, ordem: Ordem) -> None:
        if ordem.ativo != self.ativo:
            raise ValueError("a ordem não pertence ao ativo deste livro.")
        if not ordem.esta_ativa():
            raise ValueError("apenas ordens ativas podem entrar no livro.")
        if ordem.tipo is TipoOrdem.MERCADO:
            raise ValueError(
                "ordens a mercado não devem permanecer no livro de ofertas."
            )

        if ordem.lado is LadoOrdem.COMPRA:
            self.ordens_compra.append(ordem)
            self._ordenar_compras()
        else:
            self.ordens_venda.append(ordem)
            self._ordenar_vendas()

    def remover_ordem(self, ordem: Ordem) -> None:
        lista = (
            self.ordens_compra if ordem.lado is LadoOrdem.COMPRA else self.ordens_venda
        )
        if ordem in lista:
            lista.remove(ordem)

    def listar_ordens_compra(self) -> list[Ordem]:
        return list(self.ordens_compra)

    def listar_ordens_venda(self) -> list[Ordem]:
        return list(self.ordens_venda)

    def melhor_compra(self) -> Ordem | None:
        return self.ordens_compra[0] if self.ordens_compra else None

    def melhor_venda(self) -> Ordem | None:
        return self.ordens_venda[0] if self.ordens_venda else None

    def _ordenar_compras(self) -> None:
        self.ordens_compra.sort(
            key=lambda o: (
                self._preco_limite_obrigatorio(o),
                -o.tempo.tick,
            ),
            reverse=True,
        )

    def _ordenar_vendas(self) -> None:
        self.ordens_venda.sort(
            key=lambda o: (
                self._preco_limite_obrigatorio(o),
                o.tempo.tick,
            )
        )

    @staticmethod
    def _preco_limite_obrigatorio(ordem: Ordem) -> Decimal:
        if ordem.preco_limite is None:
            raise ValueError("ordens no livro devem possuir preco_limite.")
        return ordem.preco_limite
