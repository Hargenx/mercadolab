from __future__ import annotations

from decimal import Decimal

from mercadolab.api.ativo import Ativo, TipoAtivo
from mercadolab.api.carteira import Carteira
from mercadolab.api.investidor import Investidor
from mercadolab.api.mercado import Mercado
from mercadolab.api.ordem import LadoOrdem, TipoOrdem
from mercadolab.api.posicao import Posicao
from mercadolab.api.simulacao import Simulacao
from mercadolab.api.tempo import Tempo

# ============================================================
# USO DA FRAMEWORK
# ============================================================
# O MercadoLab fornece os componentes centrais do domínio:
# Ativo, Investidor, Mercado, Ordem, Simulacao, Carteira, Posicao e Tempo.
# Neste exemplo, a lógica do cenário é propositalmente simples e explícita.


def main() -> None:
    # 1. Criar um ativo negociável usando a framework.
    fii = Ativo(
        ticker="XPML11",
        tipo=TipoAtivo.FII,
        nome="FII Exemplo XPML11",
        moeda="BRL",
        tick_size=Decimal("0.01"),
        lote_padrao=1,
    )

    # 2. Criar o mercado e registrar o ativo.
    mercado = Mercado(nome="Mercado FII Exemplo")
    mercado.adicionar_ativo(fii)

    # 3. Criar participantes do mercado.
    comprador = Investidor(
        nome="Comprador",
        carteira=Carteira(caixa=Decimal("10000.00")),
    )

    vendedor = Investidor(
        nome="Vendedor",
        carteira=Carteira(caixa=Decimal("0.00")),
    )

    # 4. Definir o estado inicial do cenário.
    # Esta parte é uma escolha externa ao núcleo da framework.
    vendedor.carteira.posicoes[fii.ticker] = Posicao(
        ativo=fii,
        quantidade=10,
        preco_medio=Decimal("100.00"),
    )

    # 5. Criar a simulação.
    sim = Simulacao(mercado=mercado, tempo_atual=Tempo(tick=0))
    sim.adicionar_investidor(comprador)
    sim.adicionar_investidor(vendedor)

    # 6. Criar ordens no mesmo tick.
    # A framework não impõe estratégias; aqui as ordens são definidas manualmente.
    ordem_venda = vendedor.emitir_ordem(
        ativo=fii,
        lado=LadoOrdem.VENDA,
        tipo=TipoOrdem.LIMITADA,
        quantidade=5,
        tempo=sim.tempo_atual,
        preco_limite=Decimal("105.00"),
    )

    ordem_compra = comprador.emitir_ordem(
        ativo=fii,
        lado=LadoOrdem.COMPRA,
        tipo=TipoOrdem.LIMITADA,
        quantidade=5,
        tempo=sim.tempo_atual,
        preco_limite=Decimal("105.00"),
    )

    # 7. Executar um tick com as ordens definidas.
    transacoes = sim.executar_tick([ordem_venda, ordem_compra])

    # 8. Exibir resultados.
    print("Tempo atual após o tick:", sim.tempo_atual)
    print("Quantidade de transações:", len(transacoes))

    for t in transacoes:
        print(t.ativo.ticker, t.quantidade, t.preco, t.valor_total)

    print("Caixa comprador:", comprador.carteira.caixa)
    print("Caixa vendedor:", vendedor.carteira.caixa)
    print("Posição comprador:", comprador.carteira.obter_posicao(fii))
    print("Posição vendedor:", vendedor.carteira.obter_posicao(fii))


if __name__ == "__main__":
    main()
