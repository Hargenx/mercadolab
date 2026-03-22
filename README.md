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

Veja CONTRIBUTING.md e nosso Código de Conduta.
Sugestões, dúvidas e discussões podem ser abertas via Issues no GitHub. [![CONTRIBUTING](https://img.shields.io/badge/CONTRIBUTING-grey?logo=git)](CONTRIBUTING.md) [![Code of Conduct](https://img.shields.io/badge/CODE%20OF%20CONDUCT-grey?logo=git)](CODE_OF_CONDUCT.md)

---

## 📜 Licença

Distribuído sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📚 Citar

Mauricio Sanches de Jesus, Raphael (2025).
MercadoLab — framework baseado em agentes para mercados artificiais.
GitHub: [https://github.com/Hargenx/mercadolab](https://github.com/Hargenx/mercadolab)

---

## 📝 Changelog

O histórico de versões e mudanças arquiteturais do projeto está disponível em [`CHANGELOG.md`](CHANGELOG.md).
