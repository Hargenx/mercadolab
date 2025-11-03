# MercadoLab

![Logo da Framework](./assets/img/file.svg "MercadoLab")

**Framework minimalista de componentes para simulações baseadas em agentes em mercados financeiros artificiais.**  
MercadoLab fornece blocos fundamentais de ABM + execução paralela eficiente, sem impor microestrutura.  
Você define a teoria. O framework executa os agentes em paralelo.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE) [![Python >=3.11](https://img.shields.io/badge/python-%3E%3D3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/) [![PyPI](https://img.shields.io/pypi/v/mercadolab)](https://pypi.org/project/mercadolab/) [![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mercadolab)](https://pypi.org/project/mercadolab/)

---

## ✨ Destaques

- **Base conceitual mínima e estável**: Ativo, Tempo, Dinheiro, Side, Investidor.
- **Execução paralela de decisões**: `ParallelScheduler` com `ThreadPoolExecutor`.
- **Não impõe microestrutura**: sem Simulation, sem Market, sem Order Book — o pesquisador decide.
- **Foco em pesquisa**: reduz contaminação epistemológica na modelagem.
- **Performance**: ~40 ms/tick com ~1000 agentes (run_tick) / ~24 ms/tick (decide_only).

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

## 🧪 Padrão de Uso (essência da API pública)

```python
from mercadolab import Ativo, Tempo, Side, Investidor
from mercadolab.internal.engine import make_executor, ParallelScheduler

class Buyer(Investidor):
    def decidir(self, ativo, tempo):
        return Side.BUY

class Seller(Investidor):
    def decidir(self, ativo, tempo):
        return Side.SELL

ativos = [Ativo("AAA11")]
investidores = [Buyer("b","BRL"), Seller("s","BRL")]

def price_fn(ativo, tempo):
    return 100.0

with make_executor("thread", max_workers=8) as ex:
    sched = ParallelScheduler(executor=ex, price_fn=price_fn)
    trades = sched.run_tick(Tempo(1), ativos, investidores)
```

Conceitos centrais:

- `Investidor.decidir(ativo, tempo) -> Side`: única obrigatoriedade.
- MercadoLab não define “motor de mercado” — apenas as peças-base.

---

## 🔬 Motivação científica

Frameworks que já trazem mercado embutido impõem teoria.
MercadoLab mantém a microestrutura como variável — e não como premissa.

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
Sugestões / discussões: Issues no GitHub.

---

## 📜 Licença

MIT.

---

## 📚 Citar

Sanches de Jesus, Raphael Mauricio (2025).
MercadoLab — framework baseado em agentes para mercados artificiais.
GitHub: [https://github.com/Hargenx/mercadolab](https://github.com/Hargenx/mercadolab)

---

## 2) CHANGELOG.md – rastreabilidade formal 0.2.0 → 0.3.0

```markdown
# MercadoLab – CHANGELOG

## 0.3.0 (breaking change / redesign)

### Removido
- Removido `Simulation`.
- Removido `Market`.
- Removido `Order` / `Ordem`.
- Removida API orientada a DataFrame.
- Removida CLI (`mercadolab quickstart`, `mercadolab run`, etc.).

### Adicionado
- API pública minimalista e estável: `Ativo`, `Tempo`, `Dinheiro`, `Side`, `Investidor`.
- Scheduler paralelo: `ParallelScheduler` + `make_executor`.
- Dois modos formais de operação:
  - `run_tick` (pares BUY/SELL)
  - `decide_only_tick` (medição pura BUY/SELL sem transações)

### Alterado
- baseline Python passou a ser >= 3.11
- reposicionamento metodológico: framework passa a ser “caixa de blocos” para pesquisa ABM

### Justificativa
Remoção de microestrutura implícita evita contaminação epistemológica e melhora reprodutibilidade científica.
