from __future__ import annotations

from decimal import Decimal
import random

from ..api.ativo import Ativo, TipoAtivo
from ..api.carteira import Carteira
from ..api.investidor import Investidor
from ..api.mercado import Mercado
from ..api.ordem import LadoOrdem, TipoOrdem
from ..api.posicao import Posicao
from ..api.simulacao import Simulacao
from ..api.tempo import Tempo

# ============================================================
# CONFIGURAÇÃO DO CENÁRIO
# ============================================================
# Estas constantes pertencem ao cenário de uso e não ao núcleo da framework.
SEED = 42
TOTAL_TICKS = 252
TOTAL_INVESTIDORES = 100
CHECKPOINTS = {0, 1, 2, 9, 49, 99, 149, 199, 251}


def fmt_money(valor: Decimal) -> str:
    return f"{valor.quantize(Decimal('0.01'))}"


# ============================================================
# LÓGICA EXTERNA AO FRAMEWORK
# ============================================================
# Esta função define como os investidores começam o cenário.
# O MercadoLab não impõe tipos fixos de investidor, como comprador ou vendedor.
# Todos são apenas participantes; o cenário decide o estado inicial.
def criar_investidores(ativo: Ativo, total: int = 100) -> list[Investidor]:
    investidores: list[Investidor] = []

    for i in range(total):
        caixa_inicial = Decimal(str(random.randint(1000, 20000))).quantize(
            Decimal("0.01")
        )

        investidor = Investidor(
            nome=f"Investidor_{i + 1}",
            carteira=Carteira(caixa=caixa_inicial),
        )

        # Parte externa: alguns investidores começam com posição no ativo.
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
# Esta função representa uma política de geração de ordens.
# O MercadoLab não impõe como os agentes decidem; esta lógica pode ser
# substituída por qualquer outra definida pelo usuário.
def gerar_ordens_para_tick(
    investidores: list[Investidor],
    ativo: Ativo,
    tempo: Tempo,
) -> list:
    ordens = []

    for investidor in investidores:
        posicao = investidor.carteira.obter_posicao(ativo)
        caixa = investidor.carteira.caixa

        preco = Decimal(str(random.choice([98, 99, 100, 101, 102, 103]))).quantize(
            Decimal("0.01")
        )
        quantidade = random.randint(1, 5)

        # O mesmo investidor pode comprar, vender ou não fazer nada,
        # dependendo do seu estado atual e das regras do cenário.
        opcoes = ["nada"]

        if caixa >= preco * Decimal(quantidade):
            opcoes.append("comprar")

        if posicao is not None and posicao.quantidade >= quantidade:
            opcoes.append("vender")

        acao = random.choice(opcoes)

        # USO DA FRAMEWORK:
        # Aqui usamos Investidor.emitir_ordem para produzir ordens compatíveis
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


def resumo_investidores(
    investidores: list[Investidor],
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

    # ============================================================
    # USO DA FRAMEWORK
    # ============================================================
    # Criamos um ativo negociável usando a estrutura fornecida pela framework.
    ativo = Ativo(
        ticker="XPML11",
        tipo=TipoAtivo.FII,
        nome="FII Exemplo XPML11",
        moeda="BRL",
        tick_size=Decimal("0.01"),
        lote_padrao=1,
    )

    # Criamos o mercado e registramos o ativo.
    mercado = Mercado(nome="Mercado FII - Simulação Anual")
    mercado.adicionar_ativo(ativo)

    # Criamos a simulação, responsável por coordenar tempo e submissão de ordens.
    simulacao = Simulacao(
        mercado=mercado,
        tempo_atual=Tempo(tick=0),
    )

    # ============================================================
    # LÓGICA EXTERNA AO FRAMEWORK
    # ============================================================
    # O usuário define quais participantes farão parte do cenário.
    investidores = criar_investidores(ativo, total=TOTAL_INVESTIDORES)
    for investidor in investidores:
        simulacao.adicionar_investidor(investidor)

    historico: list[dict[str, Decimal | int]] = []
    total_transacoes = 0
    volume_total = Decimal("0.00")

    # ============================================================
    # INTEGRAÇÃO ENTRE CENÁRIO EXTERNO E FRAMEWORK
    # ============================================================
    # A lógica externa gera as ordens do tick.
    # A framework processa essas ordens, executa transações e atualiza o estado.
    for _ in range(TOTAL_TICKS):
        tick_anterior = simulacao.tempo_atual.tick
        ordens = gerar_ordens_para_tick(
            simulacao.listar_investidores(),
            ativo,
            simulacao.tempo_atual,
        )
        transacoes = simulacao.executar_tick(ordens)

        quantidade_transacoes = len(transacoes)
        volume_tick = sum((t.valor_total for t in transacoes), Decimal("0.00"))

        total_transacoes += quantidade_transacoes
        volume_total += volume_tick

        historico.append(
            {
                "tick": tick_anterior,
                "ordens": len(ordens),
                "transacoes": quantidade_transacoes,
                "volume": volume_tick,
            }
        )

        if tick_anterior in CHECKPOINTS:
            print(
                f"Tick {tick_anterior:3} | "
                f"ordens={len(ordens):3} | "
                f"transacoes={quantidade_transacoes:3} | "
                f"volume={fmt_money(volume_tick)}"
            )

    ticks_com_negocio = sum(1 for item in historico if item["transacoes"] > 0)
    media_ordens = sum(int(item["ordens"]) for item in historico) / len(historico)
    media_transacoes = (
        sum(int(item["transacoes"]) for item in historico) / len(historico)
    )

    print("\n===== RESUMO FINAL =====")
    print("Seed:", SEED)
    print("Ticks executados:", len(historico))
    print("Total de transações:", total_transacoes)
    print("Volume financeiro total:", fmt_money(volume_total))
    print("Tempo final da simulação:", simulacao.tempo_atual)
    print("Ticks com pelo menos uma transação:", ticks_com_negocio)
    print("Média de ordens por tick:", round(media_ordens, 2))
    print("Média de transações por tick:", round(media_transacoes, 2))

    resumo_investidores(simulacao.listar_investidores(), ativo, limite=12)


if __name__ == "__main__":
    main()
