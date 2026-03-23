# MercadoLab

![Logo da Framework](./assets/img/file.svg "MercadoLab")

**Framework em Python para criação de cenários de mercados artificiais baseados em agentes.**  
MercadoLab fornece componentes fundamentais de domínio e mecanismos de execução paralela, permitindo construir cenários experimentais sem impor uma única microestrutura de mercado.  
Você define o cenário, as regras e a teoria. O framework oferece a base para modelar e executar.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE) [![Python >=3.11](https://img.shields.io/badge/python-%3E%3D3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/) [![PyPI](https://img.shields.io/pypi/v/mercadolab)](https://pypi.org/project/mercadolab/) [![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mercadolab)](https://pypi.org/project/mercadolab/)

---

## ✨ Destaques

- **Núcleo de domínio estável**: `Ativo`, `Tempo`, `Dinheiro`, `Side`, `Investidor`, `Mercado`, `Transacao`.
- **Execução paralela**: `ParallelScheduler` com suporte a execução concorrente de decisões.
- **Não impõe microestrutura específica**: sem order book obrigatório, sem formação de preço única e sem teoria econômica fixa.
- **Foco em pesquisa e ensino**: favorece extensibilidade, experimentação e reprodutibilidade.
- **Arquitetura modular**: separa componentes de domínio, execução e cenários.
- **Cenários de referência**: inclui cenários básicos e adaptativos construídos sobre o núcleo da framework.

---

## 🚀 Instalação

```bash
pip install mercadolab
```

> **Nota**: para desenvolvimento local:

```bash
git clone https://github.com/Hargenx/mercadolab
cd mercadolab
pip install -e ".[dev]"
```

---

## 🧪 Exemplo de uso

```python
from mercadolab import Ativo, Dinheiro, Investidor, Mercado, Side, Tempo
from mercadolab.internal.engine import ParallelScheduler, make_executor


class Buyer(Investidor):
    def decidir(self, ativo: Ativo, tempo: Tempo) -> Side:
        return Side.BUY


class Seller(Investidor):
    def decidir(self, ativo: Ativo, tempo: Tempo) -> Side:
        return Side.SELL


def price_fn(ativo: Ativo, tempo: Tempo, mercado: Mercado) -> float:
    return 100.0


mercado = Mercado("mercado_teste")
mercado.adicionar_ativo(Ativo("AAA11"))

investidores = (
    Buyer("b1", "Buyer 1", Dinheiro("BRL", 1000.0)),
    Seller("s1", "Seller 1", Dinheiro("BRL", 1000.0)),
)

with make_executor(max_workers=8) as executor:
    scheduler = ParallelScheduler(
        mercado=mercado,
        investidores=investidores,
        executor=executor,
    )
    transacoes = scheduler.executar_passo(
        Tempo(1),
        price_fn=price_fn,
        enforce_cash=True,
    )
```

Conceitos centrais:

- `Investidor.decidir(ativo, tempo) -> Side`: contrato central para definição do comportamento dos agentes.
- `Mercado` organiza os ativos disponíveis no cenário.
- `ParallelScheduler` coordena a execução das decisões e o pareamento básico de transações.
- MercadoLab não impõe uma microestrutura fechada; ele oferece um núcleo extensível para construção de cenários.

---

## Cenários disponíveis

Além do núcleo do domínio e do mecanismo de execução, o MercadoLab já inclui cenários de referência construídos **sem alterar o core da framework**.  
Esses cenários têm dois objetivos principais:

- demonstrar como o núcleo pode ser usado na prática;
- servir como base para documentação, testes e evolução de cenários mais sofisticados.

A ideia central é que o **core permaneça pequeno, estável e neutro**, enquanto cenários concretos são construídos por composição em uma camada própria.

### `BasicMarketScenario`

O `BasicMarketScenario` foi criado como **cenário mínimo de referência**.

Ele existe para mostrar, de forma previsível e didática, que o fluxo essencial do MercadoLab já funciona ponta a ponta:

- criação de mercado;
- definição de ativos;
- criação de investidores;
- execução por ticks;
- geração de transações;
- atualização de caixa dos agentes;
- uso do `ParallelScheduler`.

#### O que foi modelado

No cenário básico:

- há compradores e vendedores fixos;
- compradores sempre decidem `BUY`;
- vendedores sempre decidem `SELL`;
- os ativos são definidos no próprio cenário;
- o preço é gerado por uma função simples e determinística;
- a execução ocorre por um número configurável de ticks.

#### O que foi deixado de fora de propósito

O cenário básico **não** tenta representar um mercado realista.  
Por escolha de projeto, ele não inclui:

- influência social;
- notícias;
- carteira por ativo;
- hold/inatividade;
- mudança adaptativa de estratégia;
- formação de preço endógena;
- ordem limitada ou order book completo.

Isso foi intencional: o papel do `BasicMarketScenario` é ser um **baseline funcional, legível e testável**.

---

### `AdaptiveMarketScenario`

O `AdaptiveMarketScenario` foi criado como um segundo passo: um cenário ainda simples, mas já com **heterogeneidade comportamental**.

Ele demonstra que o MercadoLab consegue sustentar agentes cuja decisão depende de múltiplos fatores, sem que isso exija mudanças no núcleo da framework.

#### O que foi modelado 2

Neste cenário, cada agente toma decisão com base em três componentes principais:

- **vizinhos**: o agente observa uma pequena vizinhança social;
- **carteira**: o estado atual do caixa influencia sua predisposição;
- **fator externo**: um sinal exógeno global afeta o sentimento do mercado.

Além disso, cada agente possui um **viés individual**, o que evita simetria total e permite que compradores e vendedores coexistam no mesmo tick.

#### O que esse cenário demonstra

O `AdaptiveMarketScenario` mostra que:

- o comportamento dos agentes pode ser não trivial;
- a decisão pode combinar fatores internos e externos;
- a framework suporta cenários com interação social simples;
- transações e saldos passam a divergir entre agentes;
- o mercado pode exibir dinâmica mais rica do que no cenário básico.

#### O que ainda não foi incluído

Mesmo sendo mais expressivo que o cenário básico, esse cenário ainda não pretende ser uma modelagem completa de mercado.  
Ele ainda não inclui, por exemplo:

- inventário detalhado por ativo;
- decisão explícita de quantidade;
- estado `HOLD`;
- rede social complexa;
- formação de preço baseada diretamente no excesso de demanda;
- order book completo.

O objetivo aqui é manter um cenário **intermediário**: simples o suficiente para ser entendido, mas rico o suficiente para demonstrar adaptação e heterogeneidade.

Os cenários atuais foram desenvolvidos em etapas: primeiro um cenário determinístico e mínimo (`BasicMarketScenario`), depois um cenário com heterogeneidade e influência social (`AdaptiveMarketScenario`). Essa progressão ajuda a validar o núcleo do MercadoLab antes da introdução de estruturas mais sofisticadas.

---

## Papel dos cenários na arquitetura do MercadoLab

Os cenários de referência foram construídos para reforçar uma decisão arquitetural importante do projeto:

> o núcleo da framework não deve embutir uma única teoria de mercado, mas deve permitir que diferentes cenários sejam construídos sobre uma base comum.

Em outras palavras:

- o **core** oferece os componentes fundamentais;
- a **engine** executa a dinâmica;
- os **cenários** combinam esses elementos para produzir mercados concretos.

Essa separação é central para o MercadoLab, porque permite:

- clareza arquitetural;
- extensibilidade;
- reprodutibilidade;
- comparação entre cenários;
- e evolução incremental do projeto sem contaminar o núcleo com regras muito específicas.

---

## 🔬 Motivação científica

Frameworks que já trazem uma microestrutura embutida tendem a impor pressupostos teóricos ao experimento.
O MercadoLab busca manter a microestrutura como variável de modelagem — e não como premissa fixa do framework.

Ideal para:

- calibração
- experimentos ABM puros
- replicação de artigos
- teses / dissertações sobre dinâmica de preço artificial

---

## 🧰 Desenvolvimento

- Lint: `ruff check .`
- Testes: `pytest`
- Tipagem (opcional): `mypy src/mercadolab`

---

## 🗺️ Roadmap (curto prazo)

- [ ] `chunk_size` auto-tuning para scheduler
- [ ] métricas auxiliares (opcionais) sem impor microestrutura
- [ ] hooks de instrumentação (opt-in)
- [ ] camada opcional de coleta de estatísticas sem Book

---

## 🤝 Contribuindo

Veja [![CONTRIBUTING](https://img.shields.io/badge/CONTRIBUTING-grey?logo=git)](CONTRIBUTING.md) e nosso [![Code of Conduct](https://img.shields.io/badge/CODE%20OF%20CONDUCT-grey?logo=git)](CODE_OF_CONDUCT.md).
Sugestões, dúvidas e discussões podem ser abertas via Issues no GitHub.  

---

## 📜 Licença

Distribuído sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📚 Citar

Mauricio Sanches de Jesus, Raphael (2025).
MercadoLab — framework baseado em agentes para mercados artificiais.
GitHub: [https://github.com/Hargenx/mercadolab](https://github.com/Hargenx/mercadolab)

---

## 📝 Changelog

O histórico de versões e mudanças arquiteturais do projeto está disponível em [`CHANGELOG.md`](CHANGELOG.md).
