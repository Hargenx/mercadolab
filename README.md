# MercadoLab

![Logo da Framework](./assets/img/file.svg "MercadoLab")

**Framework em Python para construção de cenários de mercados artificiais baseados em agentes.**

O MercadoLab fornece um núcleo de domínio enxuto para modelar instrumentos negociáveis, participantes, ordens, transações, livros de ofertas, mercado e simulação temporal, sem impor uma única teoria comportamental, microestrutura fixa ou estratégia de decisão.

A proposta da framework é simples: **oferecer a infraestrutura para que outros desenvolvam seus próprios mercados artificiais**, como mercados de FIIs, criptoativos, ações ou cenários híbridos, mantendo em aberto regras de negociação, comportamento dos agentes e hipóteses experimentais.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python >=3.11](https://img.shields.io/badge/python-%3E%3D3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![PyPI](https://img.shields.io/pypi/v/mercadolab)](https://pypi.org/project/mercadolab/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mercadolab)](https://pypi.org/project/mercadolab/)

---

## ✨ Destaques

- **Núcleo de domínio explícito**: `Ativo`, `Tempo`, `Investidor`, `Carteira`, `Posicao`, `Ordem`, `Transacao`, `LivroDeOfertas`, `Mercado` e `Simulacao`.
- **Simulação neutra**: a framework coordena tempo e submissão de ordens sem impor estratégias ou políticas de decisão.
- **Microestrutura aberta**: permite construir diferentes tipos de mercado sobre a mesma base.
- **Foco em extensibilidade**: adequada para pesquisa, ensino, prototipação e experimentação.
- **Arquitetura modular**: separa claramente domínio, negociação e orquestração temporal.
- **Exemplos executáveis**: inclui exemplos mínimos e de simulação anual para demonstrar o uso da framework.

---

## 🚀 Instalação

```bash
pip install mercadolab
````

### Desenvolvimento local

````bash
git clone https://github.com/Hargenx/mercadolab.git
cd mercadolab
pip install -e ".[dev]"
````

---

## 🧱 Núcleo da framework

O núcleo atual da framework é composto pelas seguintes classes públicas:

- `Ativo`: representa o instrumento negociável.
- `Tempo`: representa o instante discreto da simulação.
- `Investidor`: representa o participante do mercado.
- `Carteira`: representa o estado patrimonial do participante.
- `Posicao`: representa a quantidade mantida de um ativo.
- `Ordem`: representa a instrução de compra ou venda.
- `Transacao`: representa a execução entre ordens compatíveis.
- `LivroDeOfertas`: organiza as ordens ativas de um ativo.
- `Mercado`: agrega ativos, livros e transações, além de processar submissão de ordens.
- `Simulacao`: coordena o avanço temporal e a submissão controlada de ordens ao mercado.

Essas classes formam uma base reutilizável para construção de cenários específicos sem acoplar o núcleo a uma teoria econômica ou microestrutura única.

---

## 🧪 Exemplo mínimo de uso

````python
from decimal import Decimal

from mercadolab.api.ativo import Ativo, TipoAtivo
from mercadolab.api.carteira import Carteira
from mercadolab.api.investidor import Investidor
from mercadolab.api.mercado import Mercado
from mercadolab.api.ordem import LadoOrdem, TipoOrdem
from mercadolab.api.posicao import Posicao
from mercadolab.api.simulacao import Simulacao
from mercadolab.api.tempo import Tempo

# 1. Criar ativo
fii = Ativo(
    ticker="XPML11",
    tipo=TipoAtivo.FII,
    nome="FII Exemplo XPML11",
    moeda="BRL",
    tick_size=Decimal("0.01"),
    lote_padrao=1,
)

# 2. Criar mercado e adicionar ativo
mercado = Mercado(nome="Mercado FII Exemplo")
mercado.adicionar_ativo(fii)

# 3. Criar investidores
comprador = Investidor(
    nome="Comprador",
    carteira=Carteira(caixa=Decimal("10000.00")),
)

vendedor = Investidor(
    nome="Vendedor",
    carteira=Carteira(caixa=Decimal("0.00")),
)

# 4. Dar posição inicial ao vendedor
vendedor.carteira.posicoes[fii.ticker] = Posicao(
    ativo=fii,
    quantidade=10,
    preco_medio=Decimal("100.00"),
)

# 5. Criar simulação
sim = Simulacao(mercado=mercado, tempo_atual=Tempo(tick=0))
sim.adicionar_investidor(comprador)
sim.adicionar_investidor(vendedor)

# 6. Criar ordens no mesmo tick
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

# 7. Executar um tick
transacoes = sim.executar_tick([ordem_venda, ordem_compra])

print("Tempo atual após o tick:", sim.tempo_atual)
print("Quantidade de transações:", len(transacoes))

for t in transacoes:
    print(
        t.ativo.ticker,
        t.quantidade,
        t.preco,
        t.valor_total,
    )

print("Caixa comprador:", comprador.carteira.caixa)
print("Caixa vendedor:", vendedor.carteira.caixa)
print("Posição comprador:", comprador.carteira.obter_posicao(fii))
print("Posição vendedor:", vendedor.carteira.obter_posicao(fii))
````

Esse exemplo demonstra o fluxo mínimo ponta a ponta:

- criação de ativo;
- criação de mercado;
- emissão de ordens;
- execução de transação;
- atualização patrimonial.

---

## 📈 Exemplo mais completo

O repositório também pode incluir uma simulação anual simplificada com múltiplos investidores em:

````text
mercadolab/scenarios/exemplo_simulacao_anual.py
````

Esse exemplo demonstra:

- múltiplos participantes;
- geração externa de ordens;
- 252 ticks de simulação;
- transações, volume e estado patrimonial final;
- uso da framework sem impor estratégias internas.

### Execução dos exemplos

Após instalar o projeto em modo editável, os exemplos podem ser executados como módulos do pacote:

````bash
python -m mercadolab.scenarios.exemplo_minimo_fii
python -m mercadolab.scenarios.exemplo_simulacao_anual
````

---

## 🧭 Filosofia de projeto

O MercadoLab foi projetado para ser uma **ferramenta de construção**, não um modelo fechado de mercado.

Isso significa que a framework:

- **fornece infraestrutura**, não estratégias prontas;
- **mantém a simulação temporal**, mas não impõe comportamento dos agentes;
- **processa ordens e transações**, mas não fixa uma única teoria econômica;
- **permite diferentes mercados** sobre a mesma base conceitual.

Assim, o mesmo núcleo pode ser utilizado para:

- mercados de FIIs;
- mercados de criptoativos;
- mercados de ações;
- cenários acadêmicos sintéticos;
- protótipos experimentais com microestruturas customizadas.

---

## 🧠 O que a framework deixa em aberto

Por escolha arquitetural, o MercadoLab **não impõe**:

- estratégias de decisão dos agentes;
- subclasses obrigatórias de investidores;
- uma única política de formação de preço;
- uma única teoria econômica;
- um conjunto fixo de cenários;
- uma única política de concorrência.

Essas decisões pertencem ao desenvolvedor ou pesquisador que utiliza a framework.

---

## ⚙️ Concorrência e reprodutibilidade

A arquitetura atual favorece a separação entre:

- **coordenação temporal da simulação**
- **processamento do mercado**
- **lógica externa de geração de ordens**

Essa separação permite evoluir para modos opcionais de concorrência na coleta ou geração de ordens, sem impor paralelismo ao núcleo do mercado.

### Observação importante

Quando a geração de ordens depende de um gerador pseudoaleatório global, como `random.seed(...)`, a execução concorrente pode comprometer a reprodutibilidade estrita do experimento.

Isso acontece porque a semente fixa apenas o estado inicial do gerador, mas a sequência efetivamente consumida depende da **ordem de execução** das tarefas. Em execução serial, essa ordem é previsível; em execução concorrente, ela pode variar.

Por isso:

- **modo serial** tende a ser mais reprodutível;
- **modo concorrente** pode ser útil para desempenho, mas exige mais cuidado experimental.

---

## 🔬 Motivação científica

Muitas bibliotecas e implementações de mercados artificiais já embutem uma microestrutura, uma política de execução ou um conjunto específico de agentes. Isso pode limitar a reutilização do software e introduzir premissas teóricas diretamente na infraestrutura experimental.

O MercadoLab busca separar:

- **infraestrutura do mercado**
- **orquestração da simulação**
- **hipóteses comportamentais e teóricas**

Essa separação favorece:

- reprodutibilidade;
- extensibilidade;
- clareza arquitetural;
- comparação entre cenários;
- uso em ensino e pesquisa.

---

## ✅ Testes

O núcleo atual da framework já pode ser validado por testes automatizados cobrindo, entre outros pontos:

- criação de ativos;
- emissão e validação de ordens;
- organização do livro de ofertas;
- submissão ao mercado;
- geração de transações;
- atualização patrimonial;
- avanço temporal da simulação.

Execução da suíte:

````bash
pytest
````

---

## 🧰 Desenvolvimento

- Lint: `ruff check .`
- Testes: `pytest`
- Tipagem: `mypy src/mercadolab`

---

## 🗺️ Roadmap

- [ ] ampliar exemplos de uso da framework
- [ ] formalizar contratos de extensão para estratégias e agentes
- [ ] adicionar cenários de referência sem contaminar o núcleo
- [ ] expandir documentação de integração com notebooks e Google Colab
- [ ] evoluir o suporte opcional à coleta concorrente de ordens
- [ ] ampliar coleta de métricas para análise experimental

---

## 🤝 Contribuindo

Veja [![CONTRIBUTING](https://img.shields.io/badge/CONTRIBUTING-grey?logo=git)](CONTRIBUTING.md) e nosso [![Code of Conduct](https://img.shields.io/badge/CODE%20OF%20CONDUCT-grey?logo=git)](CODE_OF_CONDUCT.md).
Sugestões, dúvidas e discussões podem ser abertas via Issues no GitHub.  

---

## 📜 Licença

Distribuído sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📚 Citação

Mauricio Sanches de Jesus, Raphael (2025).
**MercadoLab — framework baseado em agentes para mercados artificiais.**
GitHub: [https://github.com/Hargenx/mercadolab](https://github.com/Hargenx/mercadolab)

---

## 📝 Changelog

O histórico de versões e mudanças arquiteturais do projeto está disponível em [`CHANGELOG.md`](CHANGELOG.md).
