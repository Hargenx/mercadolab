from __future__ import annotations

from dataclasses import dataclass, field
from random import Random
from statistics import mean
from typing import Iterable


@dataclass(slots=True)
class FIIMarketConfig:
    """Parâmetros de configuração do cenário de mercado de FII."""

    num_dias: int = 60
    num_investidores: int = 50
    tamanho_vizinhanca: int = 5
    seed: int = 42

    ticker_fii: str = "MXRF11"
    num_cotas_fii: int = 10_000
    preco_inicial_cota: float = 100.0
    caixa_inicial_fii: float = 100_000.0

    caixa_inicial_investidor: float = 10_000.0
    cotas_iniciais_investidor: int = 10

    num_imoveis: int = 5
    valor_base_imovel: float = 200_000.0
    vacancia_base: float = 0.1
    custo_manutencao_base: float = 2_000.0
    aluguel_base_factor: float = 0.006
    aluguel_volatilidade: float = 0.02

    taxa_selic: float = 0.10
    expectativa_inflacao: float = 0.04
    premio_risco: float = 0.03

    media_noticia: float = 0.0
    vol_noticia: float = 0.2

    frequencia_dividendos: int = 5
    payout_ratio: float = 0.9
    reinvestimento_ratio: float = 0.1

    quantidade_maxima_ordem: int = 5
    spread_relativo_maximo: float = 0.03

    peso_fundamento: float = 0.5
    peso_vizinhos: float = 0.2
    peso_noticia: float = 0.2
    peso_caixa: float = 0.1

    ruido_decisao: float = 0.05


@dataclass(slots=True)
class OrdemFII:
    """Ordem de compra ou venda no mercado de FII."""

    tipo: str  # "compra" ou "venda"
    investidor_id: str
    preco_limite: float
    quantidade: int


@dataclass(slots=True)
class TransacaoFII:
    """Transação executada entre comprador e vendedor."""

    comprador_id: str
    vendedor_id: str
    ativo: str
    preco_execucao: float
    quantidade: int
    dia: int

    @property
    def valor_total(self) -> float:
        return self.preco_execucao * self.quantidade


@dataclass(slots=True)
class Imovel:
    """Imóvel pertencente ao FII."""

    valor: float
    vacancia: float
    custo_manutencao: float
    aluguel_factor: float
    desvio_normal: float = 0.02

    def gerar_fluxo_aluguel(self, rng: Random) -> float:
        """
        Gera o fluxo de aluguel do imóvel no período.
        """
        ocupacao = max(0.0, 1.0 - self.vacancia)
        ruido = rng.gauss(0.0, self.desvio_normal)
        aluguel_bruto = self.valor * self.aluguel_factor * ocupacao * (1.0 + ruido)
        aluguel_bruto = max(0.0, aluguel_bruto)
        return max(0.0, aluguel_bruto - self.custo_manutencao)


@dataclass(slots=True)
class FII:
    """Fundo imobiliário simplificado."""

    ticker: str
    num_cotas: int
    caixa: float
    imoveis: list[Imovel]
    preco_cota: float
    payout_ratio: float = 0.9
    reinvestimento_ratio: float = 0.1

    historico_precos: list[float] = field(default_factory=list)
    historico_dividendos: list[float] = field(default_factory=list)
    historico_caixa: list[float] = field(default_factory=list)
    historico_fluxo_aluguel: list[float] = field(default_factory=list)

    def inicializar_historico(self) -> None:
        self.historico_precos.append(self.preco_cota)
        self.historico_dividendos.append(0.0)
        self.historico_caixa.append(self.caixa)
        self.historico_fluxo_aluguel.append(0.0)

    def valor_patrimonial_total(self) -> float:
        return self.caixa + sum(imovel.valor for imovel in self.imoveis)

    def valor_patrimonial_por_cota(self) -> float:
        if self.num_cotas <= 0:
            return 0.0
        return self.valor_patrimonial_total() / self.num_cotas

    def calcular_fluxo_aluguel(self, rng: Random) -> float:
        fluxo_total = sum(imovel.gerar_fluxo_aluguel(rng) for imovel in self.imoveis)
        self.caixa += fluxo_total
        self.historico_fluxo_aluguel.append(fluxo_total)
        self.historico_caixa.append(self.caixa)
        return fluxo_total

    def distribuir_dividendos(self) -> float:
        """
        Distribui parte do caixa na forma de dividendos por cota.
        """
        if self.num_cotas <= 0 or self.caixa <= 0:
            self.historico_dividendos.append(0.0)
            return 0.0

        montante_distribuido = self.caixa * self.payout_ratio
        montante_reinvestido = self.caixa * self.reinvestimento_ratio
        dividendos_por_cota = montante_distribuido / self.num_cotas

        self.caixa = max(0.0, self.caixa - montante_distribuido - montante_reinvestido)
        self.historico_dividendos.append(dividendos_por_cota)
        self.historico_caixa.append(self.caixa)

        return dividendos_por_cota

    def registrar_preco(self, preco: float) -> None:
        self.preco_cota = preco
        self.historico_precos.append(preco)


@dataclass(slots=True)
class BancoCentral:
    """Variáveis macroeconômicas simplificadas."""

    taxa_selic: float
    expectativa_inflacao: float
    premio_risco: float


@dataclass(slots=True)
class Midia:
    """Gerador simples de sinal externo de mercado."""

    valor_atual: float = 0.0
    sigma: float = 0.2

    def gerar_noticia(self, rng: Random) -> float:
        self.valor_atual = rng.gauss(self.valor_atual * 0.5, self.sigma)
        return self.valor_atual


@dataclass(slots=True)
class InvestidorFII:
    """Investidor simplificado do mercado de FII."""

    id: str
    caixa: float
    cotas: int
    literacia_financeira: float
    vies_comportamental: float = 0.0

    vizinhos: list["InvestidorFII"] = field(default_factory=list)
    historico_riqueza: list[float] = field(default_factory=list)
    historico_sentimento: list[float] = field(default_factory=list)

    def definir_vizinhos(self, vizinhos: list["InvestidorFII"]) -> None:
        self.vizinhos = vizinhos

    def riqueza_total(self, preco_cota: float) -> float:
        return self.caixa + self.cotas * preco_cota

    def registrar_riqueza(self, preco_cota: float) -> None:
        self.historico_riqueza.append(self.riqueza_total(preco_cota))

    def receber_dividendos(self, dividendo_por_cota: float) -> None:
        self.caixa += self.cotas * dividendo_por_cota

    def sentimento_vizinhos(self) -> float:
        if not self.vizinhos:
            return 0.0
        return mean(
            v.historico_sentimento[-1] if v.historico_sentimento else 0.0
            for v in self.vizinhos
        )

    def calcular_preco_esperado(
        self,
        fii: FII,
        banco_central: BancoCentral,
        noticia: float,
    ) -> float:
        """
        Preço esperado simples, inspirado na lógica do notebook:
        combina fundamento, risco macro, notícia e influência social.
        """
        valor_patrimonial = fii.valor_patrimonial_por_cota()

        dividendo_recente = (
            fii.historico_dividendos[-1] if fii.historico_dividendos else 0.0
        )
        retorno_dividendos = dividendo_recente / max(fii.preco_cota, 1e-9)

        ajuste_macro = (
            -0.5 * banco_central.taxa_selic
            - 0.2 * banco_central.expectativa_inflacao
            - 0.3 * banco_central.premio_risco
        )

        componente_fundamental = 0.7 * valor_patrimonial + 0.3 * fii.preco_cota * (
            1.0 + retorno_dividendos + ajuste_macro
        )

        componente_social = self.sentimento_vizinhos()
        componente_noticia = noticia
        componente_pessoal = self.vies_comportamental

        preco_esperado = componente_fundamental * (
            1.0
            + 0.05 * componente_social
            + 0.05 * componente_noticia
            + 0.03 * componente_pessoal
        )

        return max(1.0, preco_esperado)

    def gerar_ordem(
        self,
        *,
        fii: FII,
        banco_central: BancoCentral,
        noticia: float,
        dia: int,
        quantidade_maxima: int,
        spread_relativo_maximo: float,
        peso_fundamento: float,
        peso_vizinhos: float,
        peso_noticia: float,
        peso_caixa: float,
        ruido_decisao: float,
        rng: Random,
    ) -> OrdemFII | None:
        """
        Gera uma ordem simples de compra ou venda.
        """
        preco_esperado = self.calcular_preco_esperado(fii, banco_central, noticia)

        score_fundamento = (preco_esperado - fii.preco_cota) / max(fii.preco_cota, 1e-9)
        score_vizinhos = self.sentimento_vizinhos()
        score_noticia = noticia

        riqueza = self.riqueza_total(fii.preco_cota)
        peso_caixa_atual = self.caixa / max(riqueza, 1e-9)
        score_caixa = (peso_caixa_atual - 0.5) * 2.0

        score_total = (
            peso_fundamento * score_fundamento
            + peso_vizinhos * score_vizinhos
            + peso_noticia * score_noticia
            + peso_caixa * score_caixa
            + self.vies_comportamental
            + rng.gauss(0.0, ruido_decisao)
        )

        self.historico_sentimento.append(score_total)

        spread = abs(rng.uniform(0.0, spread_relativo_maximo))
        quantidade = max(1, rng.randint(1, quantidade_maxima))

        if score_total > 0:
            preco_limite = fii.preco_cota * (1.0 + spread)
            custo_total = preco_limite * quantidade
            if self.caixa >= custo_total:
                return OrdemFII(
                    tipo="compra",
                    investidor_id=self.id,
                    preco_limite=preco_limite,
                    quantidade=quantidade,
                )
            return None

        if score_total < 0 and self.cotas > 0:
            quantidade = min(quantidade, self.cotas)
            if quantidade <= 0:
                return None
            preco_limite = fii.preco_cota * max(0.01, 1.0 - spread)
            return OrdemFII(
                tipo="venda",
                investidor_id=self.id,
                preco_limite=preco_limite,
                quantidade=quantidade,
            )

        return None


@dataclass(slots=True)
class OrderBookFII:
    """Livro de ordens simplificado para o cenário de FII."""

    ordens_compra: list[OrdemFII] = field(default_factory=list)
    ordens_venda: list[OrdemFII] = field(default_factory=list)

    def limpar(self) -> None:
        self.ordens_compra.clear()
        self.ordens_venda.clear()

    def adicionar_ordem(self, ordem: OrdemFII) -> None:
        if ordem.tipo == "compra":
            self.ordens_compra.append(ordem)
        elif ordem.tipo == "venda":
            self.ordens_venda.append(ordem)

    def executar_ordens(
        self,
        *,
        investidores: dict[str, InvestidorFII],
        ativo: str,
        dia: int,
    ) -> list[TransacaoFII]:
        """
        Casa ordens por preço: maiores compras com menores vendas.
        """
        transacoes: list[TransacaoFII] = []

        compras = sorted(self.ordens_compra, key=lambda o: o.preco_limite, reverse=True)
        vendas = sorted(self.ordens_venda, key=lambda o: o.preco_limite)

        i = 0
        j = 0

        while i < len(compras) and j < len(vendas):
            ordem_compra = compras[i]
            ordem_venda = vendas[j]

            if ordem_compra.preco_limite < ordem_venda.preco_limite:
                break

            comprador = investidores[ordem_compra.investidor_id]
            vendedor = investidores[ordem_venda.investidor_id]

            quantidade = min(ordem_compra.quantidade, ordem_venda.quantidade)
            preco_execucao = (
                ordem_compra.preco_limite + ordem_venda.preco_limite
            ) / 2.0
            valor_total = preco_execucao * quantidade

            if comprador.caixa < valor_total:
                i += 1
                continue

            if vendedor.cotas < quantidade:
                j += 1
                continue

            comprador.caixa -= valor_total
            comprador.cotas += quantidade

            vendedor.caixa += valor_total
            vendedor.cotas -= quantidade

            transacoes.append(
                TransacaoFII(
                    comprador_id=comprador.id,
                    vendedor_id=vendedor.id,
                    ativo=ativo,
                    preco_execucao=preco_execucao,
                    quantidade=quantidade,
                    dia=dia,
                )
            )

            ordem_compra.quantidade -= quantidade
            ordem_venda.quantidade -= quantidade

            if ordem_compra.quantidade == 0:
                i += 1
            if ordem_venda.quantidade == 0:
                j += 1

        return transacoes


@dataclass(slots=True)
class FIIMarketResult:
    """Resultado do cenário de mercado de FII."""

    fii: FII
    investidores: tuple[InvestidorFII, ...]
    transacoes: list[TransacaoFII]
    dias_executados: int
    historico_noticias: list[float]
    historico_precos: list[float]
    historico_dividendos: list[float]


@dataclass(slots=True)
class FIIMarketScenario:
    """Cenário de mercado de FII inspirado no modelo do notebook."""

    config: FIIMarketConfig = field(default_factory=FIIMarketConfig)

    def criar_fii(self, rng: Random) -> FII:
        imoveis = [
            Imovel(
                valor=self.config.valor_base_imovel * (1.0 + 0.2 * rng.random()),
                vacancia=max(
                    0.0, min(0.95, self.config.vacancia_base + rng.uniform(-0.03, 0.03))
                ),
                custo_manutencao=self.config.custo_manutencao_base
                * (1.0 + 0.2 * rng.random()),
                aluguel_factor=self.config.aluguel_base_factor
                * (1.0 + rng.uniform(-0.1, 0.1)),
                desvio_normal=self.config.aluguel_volatilidade,
            )
            for _ in range(self.config.num_imoveis)
        ]

        fii = FII(
            ticker=self.config.ticker_fii,
            num_cotas=self.config.num_cotas_fii,
            caixa=self.config.caixa_inicial_fii,
            imoveis=imoveis,
            preco_cota=self.config.preco_inicial_cota,
            payout_ratio=self.config.payout_ratio,
            reinvestimento_ratio=self.config.reinvestimento_ratio,
        )
        fii.inicializar_historico()
        return fii

    def criar_banco_central(self) -> BancoCentral:
        return BancoCentral(
            taxa_selic=self.config.taxa_selic,
            expectativa_inflacao=self.config.expectativa_inflacao,
            premio_risco=self.config.premio_risco,
        )

    def criar_midia(self) -> Midia:
        return Midia(
            valor_atual=self.config.media_noticia,
            sigma=self.config.vol_noticia,
        )

    def criar_investidores(self, rng: Random) -> tuple[InvestidorFII, ...]:
        investidores = tuple(
            InvestidorFII(
                id=f"inv_{i}",
                caixa=self.config.caixa_inicial_investidor,
                cotas=self.config.cotas_iniciais_investidor,
                literacia_financeira=max(0.0, min(1.0, rng.uniform(0.2, 0.95))),
                vies_comportamental=rng.uniform(-0.3, 0.3),
            )
            for i in range(self.config.num_investidores)
        )

        self._configurar_vizinhos(investidores)
        return investidores

    def _configurar_vizinhos(self, investidores: tuple[InvestidorFII, ...]) -> None:
        n = len(investidores)
        k = min(self.config.tamanho_vizinhanca, max(0, n - 1))

        for i, investidor in enumerate(investidores):
            vizinhos = [investidores[(i + d) % n] for d in range(1, k + 1)]
            investidor.definir_vizinhos(vizinhos)

    def executar(self) -> FIIMarketResult:
        rng = Random(self.config.seed)

        fii = self.criar_fii(rng)
        banco_central = self.criar_banco_central()
        midia = self.criar_midia()
        investidores = self.criar_investidores(rng)
        investidores_por_id = {inv.id: inv for inv in investidores}
        book = OrderBookFII()

        historico_noticias: list[float] = []
        transacoes_totais: list[TransacaoFII] = []

        for dia in range(1, self.config.num_dias + 1):
            noticia = midia.gerar_noticia(rng)
            historico_noticias.append(noticia)

            fii.calcular_fluxo_aluguel(rng)

            if dia % self.config.frequencia_dividendos == 0:
                dividendo = fii.distribuir_dividendos()
                for investidor in investidores:
                    investidor.receber_dividendos(dividendo)

            book.limpar()

            for investidor in investidores:
                investidor.registrar_riqueza(fii.preco_cota)
                ordem = investidor.gerar_ordem(
                    fii=fii,
                    banco_central=banco_central,
                    noticia=noticia,
                    dia=dia,
                    quantidade_maxima=self.config.quantidade_maxima_ordem,
                    spread_relativo_maximo=self.config.spread_relativo_maximo,
                    peso_fundamento=self.config.peso_fundamento,
                    peso_vizinhos=self.config.peso_vizinhos,
                    peso_noticia=self.config.peso_noticia,
                    peso_caixa=self.config.peso_caixa,
                    ruido_decisao=self.config.ruido_decisao,
                    rng=rng,
                )
                if ordem is not None:
                    book.adicionar_ordem(ordem)

            transacoes_dia = book.executar_ordens(
                investidores=investidores_por_id,
                ativo=fii.ticker,
                dia=dia,
            )
            transacoes_totais.extend(transacoes_dia)

            if transacoes_dia:
                preco_fechamento = mean(tx.preco_execucao for tx in transacoes_dia)
            else:
                # fallback simples: preço ajustado pelo valor patrimonial e notícia
                preco_fechamento = max(
                    1.0,
                    0.7 * fii.preco_cota
                    + 0.3 * fii.valor_patrimonial_por_cota() * (1.0 + 0.02 * noticia),
                )

            fii.registrar_preco(preco_fechamento)

        return FIIMarketResult(
            fii=fii,
            investidores=investidores,
            transacoes=transacoes_totais,
            dias_executados=self.config.num_dias,
            historico_noticias=historico_noticias,
            historico_precos=list(fii.historico_precos),
            historico_dividendos=list(fii.historico_dividendos),
        )
