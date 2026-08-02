from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from mercadolab.api.ativo import Ativo
from mercadolab.api.livro_de_ofertas import LivroDeOfertas
from mercadolab.api.ordem import LadoOrdem, Ordem, TipoOrdem
from mercadolab.api.transacao import Transacao


@dataclass(slots=True)
class Mercado:
    """Representa o ambiente de negociação que organiza ativos, livros e execuções."""

    nome: str
    _ativos: dict[str, Ativo] = field(default_factory=dict, repr=False)
    _livros: dict[str, LivroDeOfertas] = field(default_factory=dict, repr=False)
    _transacoes: list[Transacao] = field(default_factory=list, repr=False)

    def __post_init__(self) -> None:
        if not self.nome.strip():
            raise ValueError("nome não pode ser vazio.")

    def adicionar_ativo(self, ativo: Ativo) -> None:
        if ativo.ticker in self._ativos:
            raise ValueError(f"Já existe um ativo com ticker '{ativo.ticker}'.")
        self._ativos[ativo.ticker] = ativo
        self._livros[ativo.ticker] = LivroDeOfertas(ativo=ativo)

    def remover_ativo(self, ticker: str) -> None:
        if ticker not in self._ativos:
            raise KeyError(f"Ativo não encontrado: {ticker}")
        self._ativos.pop(ticker)
        self._livros.pop(ticker, None)

    def obter_ativo(self, ticker: str) -> Ativo:
        try:
            return self._ativos[ticker]
        except KeyError as exc:
            raise KeyError(f"Ativo não encontrado: {ticker}") from exc

    def obter_livro(self, ticker: str) -> LivroDeOfertas:
        try:
            return self._livros[ticker]
        except KeyError as exc:
            raise KeyError(
                f"Livro de ofertas não encontrado para o ativo: {ticker}"
            ) from exc

    def listar_ativos(self) -> tuple[Ativo, ...]:
        return tuple(self._ativos.values())

    def listar_livros(self) -> tuple[LivroDeOfertas, ...]:
        return tuple(self._livros.values())

    def listar_transacoes(self) -> tuple[Transacao, ...]:
        return tuple(self._transacoes)

    def cancelar_ordem(self, ordem: Ordem) -> None:
        """Cancela uma ordem ativa e a remove do respectivo livro de ofertas."""
        if ordem.ativo.ticker not in self._ativos:
            raise ValueError(
                f"O ativo '{ordem.ativo.ticker}' não está listado neste mercado."
            )

        if not ordem.esta_ativa():
            raise ValueError("apenas ordens ativas podem ser canceladas.")

        livro = self.obter_livro(ordem.ativo.ticker)
        ordens_do_lado = (
            livro.ordens_compra
            if ordem.lado is LadoOrdem.COMPRA
            else livro.ordens_venda
        )

        if ordem not in ordens_do_lado:
            raise ValueError("a ordem não está registrada no livro de ofertas.")

        ordem.cancelar()
        livro.remover_ordem(ordem)

    def submeter_ordem(self, ordem: Ordem) -> tuple[Transacao, ...]:
        """Submete uma ordem nova ao mercado e retorna as transações geradas."""
        if ordem.ativo.ticker not in self._ativos:
            raise ValueError(
                f"O ativo '{ordem.ativo.ticker}' não está listado neste mercado."
            )
        if not ordem.esta_ativa():
            raise ValueError("A ordem submetida não está ativa.")
        if not ordem.ativo.negociavel:
            raise ValueError("O ativo da ordem não está disponível para negociação.")

        livro = self.obter_livro(ordem.ativo.ticker)
        transacoes: list[Transacao] = []

        livro_oposto = (
            livro.ordens_venda
            if ordem.lado is LadoOrdem.COMPRA
            else livro.ordens_compra
        )

        while ordem.esta_ativa() and livro_oposto:
            melhor_contraparte = livro_oposto[0]

            if not melhor_contraparte.esta_ativa():
                livro.remover_ordem(melhor_contraparte)
                continue

            if not self._ordens_sao_compativeis(ordem, melhor_contraparte):
                break

            quantidade_exec = min(
                ordem.quantidade_restante,
                melhor_contraparte.quantidade_restante,
            )

            preco_exec = self._definir_preco_execucao(
                ordem_submetida=ordem,
                ordem_em_livro=melhor_contraparte,
            )

            ordem_compra = (
                ordem if ordem.lado is LadoOrdem.COMPRA else melhor_contraparte
            )
            ordem_venda = ordem if ordem.lado is LadoOrdem.VENDA else melhor_contraparte

            if not self._transacao_eh_liquidavel(
                ordem_compra=ordem_compra,
                ordem_venda=ordem_venda,
                quantidade=quantidade_exec,
                preco=preco_exec,
            ):
                if not self._ordem_eh_liquidavel(
                    ordem=melhor_contraparte,
                    quantidade=quantidade_exec,
                    preco=preco_exec,
                ):
                    melhor_contraparte.expirar()
                    livro.remover_ordem(melhor_contraparte)
                    continue

                break

            transacao = self._criar_transacao(
                ordem_entrante=ordem,
                ordem_em_livro=melhor_contraparte,
                quantidade=quantidade_exec,
                preco=preco_exec,
            )

            ordem.registrar_execucao(quantidade_exec)
            melhor_contraparte.registrar_execucao(quantidade_exec)

            self._liquidar_transacao(transacao)

            transacoes.append(transacao)
            self._transacoes.append(transacao)

            if not melhor_contraparte.esta_ativa():
                livro.remover_ordem(melhor_contraparte)

        if ordem.esta_ativa() and ordem.tipo is TipoOrdem.LIMITADA:
            livro.adicionar_ordem(ordem)
        elif ordem.esta_ativa() and ordem.tipo is TipoOrdem.MERCADO:
            ordem.expirar()
        return tuple(transacoes)

    def _ordens_sao_compativeis(
        self,
        ordem_entrante: Ordem,
        ordem_em_livro: Ordem,
    ) -> bool:
        if ordem_entrante.lado is LadoOrdem.COMPRA:
            if ordem_entrante.tipo is TipoOrdem.MERCADO:
                return True

            if ordem_entrante.preco_limite is None:
                raise ValueError("ordem limitada de compra deve possuir preco_limite.")
            if ordem_em_livro.preco_limite is None:
                raise ValueError("ordem em livro deve possuir preco_limite.")

            return ordem_entrante.preco_limite >= ordem_em_livro.preco_limite

        if ordem_entrante.tipo is TipoOrdem.MERCADO:
            return True

        if ordem_entrante.preco_limite is None:
            raise ValueError("ordem limitada de venda deve possuir preco_limite.")
        if ordem_em_livro.preco_limite is None:
            raise ValueError("ordem em livro deve possuir preco_limite.")

        return ordem_entrante.preco_limite <= ordem_em_livro.preco_limite

    def _definir_preco_execucao(
        self,
        ordem_submetida: Ordem,
        ordem_em_livro: Ordem,
    ) -> Decimal:
        if ordem_em_livro.preco_limite is None:
            raise ValueError("A ordem em livro deve possuir preço limite.")
        return ordem_em_livro.preco_limite

    def _transacao_eh_liquidavel(
        self,
        ordem_compra: Ordem,
        ordem_venda: Ordem,
        quantidade: int,
        preco: Decimal,
    ) -> bool:
        return self._ordem_eh_liquidavel(
            ordem=ordem_compra,
            quantidade=quantidade,
            preco=preco,
        ) and self._ordem_eh_liquidavel(
            ordem=ordem_venda,
            quantidade=quantidade,
            preco=preco,
        )

    def _ordem_eh_liquidavel(
        self,
        ordem: Ordem,
        quantidade: int,
        preco: Decimal,
    ) -> bool:
        """Aplica a política patrimonial padrão de liquidação à vista."""
        carteira = ordem.investidor.carteira

        if ordem.lado is LadoOrdem.COMPRA:
            custo_total = preco * Decimal(quantidade)
            return carteira.caixa >= custo_total

        posicao = carteira.obter_posicao(ordem.ativo)
        return posicao is not None and posicao.quantidade >= quantidade

    def _liquidar_transacao(self, transacao: Transacao) -> None:
        carteira_compradora = transacao.ordem_compra.investidor.carteira
        carteira_vendedora = transacao.ordem_venda.investidor.carteira

        carteira_compradora.aplicar_compra(
            ativo=transacao.ativo,
            quantidade=transacao.quantidade,
            preco=transacao.preco,
        )
        carteira_vendedora.aplicar_venda(
            ativo=transacao.ativo,
            quantidade=transacao.quantidade,
            preco=transacao.preco,
        )

    def _criar_transacao(
        self,
        ordem_entrante: Ordem,
        ordem_em_livro: Ordem,
        quantidade: int,
        preco: Decimal,
    ) -> Transacao:
        ordem_compra = (
            ordem_entrante
            if ordem_entrante.lado is LadoOrdem.COMPRA
            else ordem_em_livro
        )
        ordem_venda = (
            ordem_entrante if ordem_entrante.lado is LadoOrdem.VENDA else ordem_em_livro
        )

        return Transacao(
            ativo=ordem_compra.ativo,
            quantidade=quantidade,
            preco=preco,
            ordem_compra=ordem_compra,
            ordem_venda=ordem_venda,
            tempo=ordem_entrante.tempo,
        )
