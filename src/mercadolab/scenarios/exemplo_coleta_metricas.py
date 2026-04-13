from __future__ import annotations

from collections.abc import Sequence
from decimal import Decimal
from pathlib import Path
from typing import TypedDict
import csv
import random

from mercadolab.api.ativo import Ativo, TipoAtivo
from mercadolab.api.carteira import Carteira
from mercadolab.api.investidor import Investidor
from mercadolab.api.mercado import Mercado
from mercadolab.api.ordem import LadoOrdem, Ordem, TipoOrdem
from mercadolab.api.posicao import Posicao
from mercadolab.api.simulacao import Simulacao
from mercadolab.api.tempo import Tempo
from mercadolab.api.transacao import Transacao


SEED = 42
TOTAL_TICKS = 252
TOTAL_INVESTIDORES = 100
EXPORTAR_CSV = True
ARQUIVO_CSV = "metricas_simulacao_anual.csv"

CHECKPOINTS = {0, 1, 2, 9, 49, 99, 149, 199, 251}


class MetricasTick(TypedDict):
    tick: int
    ordens: int
    transacoes: int
    volume: Decimal
    preco_medio: Decimal | None
    ultimo_preco: Decimal | None


def fmt_money(valor: Decimal) -> str:
    return f"{valor.quantize(Decimal('0.01'))}"


def fmt_optional_money(valor: Decimal | None) -> str:
    if valor is None:
        return "None"
    return fmt_money(valor)


# ============================================================
# LÓGICA EXTERNA AO FRAMEWORK
# ============================================================
# Esta função define como os investidores começam o cenário.
# A framework não impõe perfis fixos de comprador/vendedor.
def criar_investidores(ativo: Ativo, total: int = 100) -> list[Investidor]:
    investidores: list[Investidor] = []

    for i in range(total):
        caixa_inicial = Decimal(str(random.randint(1000, 20000))).quantize(
            Decimal("0.01")
        )

        # USO DA FRAMEWORK:
        # Criamos um Investidor com uma Carteira.
        investidor = Investidor(
            nome=f"Investidor_{i + 1}",
            carteira=Carteira(caixa=caixa_inicial),
        )

        # LÓGICA EXTERNA:
        # Alguns investidores começam com posição no ativo, outros não.
        if random.random() < 0.5:
            investidor.carteira.posicoes[ativo.ticker] = Posicao(
                ativo=ativo,
                quantidade=random.randint(5, 100),
                preco_medio=Decimal(
                    str(random.choice([95, 98, 100, 102, 105]))
                ).quantize(Decimal("0.01")),
            )

        investidores.append(investidor)

    return investidores


# ============================================================
# LÓGICA EXTERNA AO FRAMEWORK
# ============================================================
# Esta função representa uma política externa de geração de ordens.
# O MercadoLab não impõe essa lógica.
def gerar_ordens_para_tick(
    investidores: Sequence[Investidor],
    ativo: Ativo,
    tempo: Tempo,
) -> list[Ordem]:
    ordens: list[Ordem] = []

    for investidor in investidores:
        posicao = investidor.carteira.obter_posicao(ativo)
        caixa = investidor.carteira.caixa

        preco = Decimal(str(random.choice([98, 99, 100, 101, 102, 103]))).quantize(
            Decimal("0.01")
        )
        quantidade = random.randint(1, 5)

        opcoes = ["nada"]

        if caixa >= preco * Decimal(quantidade):
            opcoes.append("comprar")

        if posicao is not None and posicao.quantidade >= quantidade:
            opcoes.append("vender")

        acao = random.choice(opcoes)

        # USO DA FRAMEWORK:
        # O investidor usa emitir_ordem para criar uma Ordem compatível
        # com o núcleo do MercadoLab.
        if acao == "comprar":
            ordens.append(
                investidor.emitir_ordem(
                    ativo=ativo,
                    lado=LadoOrdem.COMPRA,
                    tipo=TipoOrdem.LIMITADA,
                    quantidade=quantidade,
                    tempo=tempo,
                    preco_limite=preco,
                )
            )

        elif acao == "vender":
            ordens.append(
                investidor.emitir_ordem(
                    ativo=ativo,
                    lado=LadoOrdem.VENDA,
                    tipo=TipoOrdem.LIMITADA,
                    quantidade=quantidade,
                    tempo=tempo,
                    preco_limite=preco,
                )
            )

    return ordens


def calcular_metricas_tick(
    tick: int,
    ordens: Sequence[Ordem],
    transacoes: Sequence[Transacao],
) -> MetricasTick:
    quantidade_transacoes = len(transacoes)
    volume_tick = sum((t.valor_total for t in transacoes), Decimal("0.00"))

    if transacoes:
        quantidade_total_tick = sum(t.quantidade for t in transacoes)
        preco_medio_tick = sum(
            (t.preco * Decimal(t.quantidade) for t in transacoes), Decimal("0.00")
        ) / Decimal(quantidade_total_tick)
        ultimo_preco_tick = transacoes[-1].preco
    else:
        preco_medio_tick = None
        ultimo_preco_tick = None

    return {
        "tick": tick,
        "ordens": len(ordens),
        "transacoes": quantidade_transacoes,
        "volume": volume_tick,
        "preco_medio": preco_medio_tick,
        "ultimo_preco": ultimo_preco_tick,
    }


def exportar_metricas_csv(
    historico: Sequence[MetricasTick],
    caminho: str,
) -> None:
    destino = Path(caminho)

    with destino.open("w", newline="", encoding="utf-8") as arquivo:
        writer = csv.writer(arquivo)
        writer.writerow(
            ["tick", "ordens", "transacoes", "volume", "preco_medio", "ultimo_preco"]
        )

        for item in historico:
            writer.writerow(
                [
                    item["tick"],
                    item["ordens"],
                    item["transacoes"],
                    item["volume"],
                    item["preco_medio"],
                    item["ultimo_preco"],
                ]
            )


def resumo_investidores(
    investidores: Sequence[Investidor],
    ativo: Ativo,
    limite: int = 12,
) -> None:
    print(f"\nResumo de até {limite} investidores:")
    print("-" * 72)

    for investidor in investidores[:limite]:
        posicao = investidor.carteira.obter_posicao(ativo)
        quantidade = posicao.quantidade if posicao else 0
        preco_medio = posicao.preco_medio if posicao else Decimal("0.00")

        print(
            f"{investidor.nome:15} | "
            f"caixa={fmt_money(investidor.carteira.caixa):>10} | "
            f"qtd={quantidade:>4} | "
            f"preco_medio={fmt_money(preco_medio):>7}"
        )


def main() -> None:
    random.seed(SEED)

    # =========================
    # USO DA FRAMEWORK
    # =========================
    # Criamos o ativo, o mercado e a simulação.
    ativo = Ativo(
        ticker="XPML11",
        tipo=TipoAtivo.FII,
        nome="FII Exemplo XPML11",
        moeda="BRL",
        tick_size=Decimal("0.01"),
        lote_padrao=1,
    )

    mercado = Mercado(nome="Mercado FII - Coleta de Métricas")
    mercado.adicionar_ativo(ativo)

    simulacao = Simulacao(
        mercado=mercado,
        tempo_atual=Tempo(tick=0),
    )

    # =========================
    # LÓGICA EXTERNA AO FRAMEWORK
    # =========================
    # Definimos o estado inicial dos participantes.
    investidores = criar_investidores(ativo, total=TOTAL_INVESTIDORES)
    for investidor in investidores:
        simulacao.adicionar_investidor(investidor)

    historico: list[MetricasTick] = []

    total_transacoes = 0
    volume_total = Decimal("0.00")

    for _ in range(TOTAL_TICKS):
        tick_anterior = simulacao.tempo_atual.tick

        # LÓGICA EXTERNA:
        # O cenário gera as ordens do tick.
        ordens = gerar_ordens_para_tick(
            simulacao.listar_investidores(),
            ativo,
            simulacao.tempo_atual,
        )

        # USO DA FRAMEWORK:
        # A simulação executa o tick e o mercado processa as ordens.
        transacoes = simulacao.executar_tick(ordens)

        metricas_tick = calcular_metricas_tick(
            tick=tick_anterior,
            ordens=ordens,
            transacoes=transacoes,
        )
        historico.append(metricas_tick)

        total_transacoes += metricas_tick["transacoes"]
        volume_total += metricas_tick["volume"]

        if tick_anterior in CHECKPOINTS:
            print(
                f"Tick {tick_anterior:3} | "
                f"ordens={metricas_tick['ordens']:3} | "
                f"transacoes={metricas_tick['transacoes']:3} | "
                f"volume={fmt_money(metricas_tick['volume'])} | "
                f"preco_medio={fmt_optional_money(metricas_tick['preco_medio'])} | "
                f"ultimo_preco={fmt_optional_money(metricas_tick['ultimo_preco'])}"
            )

    ticks_com_negocio = len([item for item in historico if item["transacoes"] > 0])
    media_ordens = sum(item["ordens"] for item in historico) / len(historico)
    media_transacoes = sum(item["transacoes"] for item in historico) / len(historico)

    print("\n===== RESUMO FINAL =====")
    print("Seed:", SEED)
    print("Ticks executados:", len(historico))
    print("Total de transações:", total_transacoes)
    print("Volume financeiro total:", fmt_money(volume_total))
    print("Tempo final da simulação:", simulacao.tempo_atual)
    print("Ticks com pelo menos uma transação:", ticks_com_negocio)
    print("Média de ordens por tick:", round(media_ordens, 2))
    print("Média de transações por tick:", round(media_transacoes, 2))

    if EXPORTAR_CSV:
        exportar_metricas_csv(historico, ARQUIVO_CSV)
        print(f"CSV exportado para: {ARQUIVO_CSV}")

    resumo_investidores(simulacao.listar_investidores(), ativo, limite=12)


if __name__ == "__main__":
    main()
