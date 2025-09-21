# MercadoLab

![Logo da Framework](./assets/img/file.svg "MercadoLab")

**Laboratório de simulações baseadas em agentes para mercados.**  
Crie cenários, teste estratégias e estude dinâmicas de preço com um framework **plugável**, leve e “pip‑friendly”.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE) [![Python >=3.10](https://img.shields.io/badge/python-%3E%3D3.10-blue.svg)](https://www.python.org/downloads/release/python-3100/) [![PyPI](https://img.shields.io/pypi/v/mercadolab)](https://pypi.org/project/mercadolab/) [![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mercadolab)](https://pypi.org/project/mercadolab/)

---

## ✨ Destaques

- **Arquitetura de plugins**: registre agentes via *entry points* (`mercadolab.plugins`).  
- **API simples**: `Simulation` + `Market` + `BaseAgent` para loops claros e extensíveis.  
- **Sem dependências pesadas**: `numpy` e `pandas` como base; `matplotlib` (opcional) para gráficos.  
- **CLI**: `mercadolab quickstart` roda um exemplo funcional em segundos.

---

## 🚀 Instalação

```bash
pip install mercadolab
```

> **Nota**: durante o desenvolvimento local, você pode usar instalação editable:

```bash
git clone https://github.com/Hargenx/mercadolab
cd mercadolab
pip install -e ".[dev]"
```

---

## 🧪 Comece em 10 segundos (CLI)

```bash
mercadolab quickstart --steps 50 --seed 42
```

Saída esperada: últimas linhas de um `DataFrame` com preço e estados dos agentes.

Liste plugins detectados:

```bash
mercadolab plugins
```

Rode uma simulação mínima (sem plugins):

```bash
mercadolab run --steps 50 --n-agents 3 --price0 100
```

---

## 📦 API Essencial

```python
from mercadolab.core.simulation import Simulation
from mercadolab.core.market import Market
from mercadolab.core.investidor import Investidor, Ordem

class MeuInvestidor(Investidor):
    def decide(self, market: Market):
        # Lógica de decisão do agente
        return Ordem(agent=self, side="buy", qty=0.5)

sim = Simulation(seed=42)
sim.add_agent(MeuInvestidor(name="alice"))
sim.run(steps=100)
df = sim.to_frame()
print(df.tail())
```

**Conceitos:**

- `Investidor.decide(market) -> Ordem | None`: onde a “estratégia” acontece (retorne `None` se não negociar no tick).
- `Market`: evolui o preço (processo simples) e executa ordens a mercado.
- `Simulation`: orquestra o loop, coleta *logs* e exporta um `pandas.DataFrame`.

---

## 🔌 Plugins (entry points)

Declare seu agente como *plugin* no `pyproject.toml` do seu pacote:

```toml
[project.entry-points."mercadolab.plugins"]
hello = "mercadolab_hello.hello:HelloAgent"
```

- Publique agentes externos como plugins detectados automaticamente.

comando de verificação:

```bash
pip install mercadolab-hello
mercadolab plugins
```

No runtime, `mercadolab` carregará automaticamente:

```python
from mercadolab.plugins import load_plugins
plugins = load_plugins()
Agent = plugins["meu-agente"]
```

> Dica: publique seus plugins com o prefixo **`mercadolab-`** (ex.: `mercadolab-fiis`) para facilitar descoberta.

---

## 🧰 Desenvolvimento

- Lint: `ruff check .`  
- Testes: `pytest`  
- Tipagem (opcional): `mypy src/mercadolab`

---

## 🗺️ Roadmap (curto prazo)

- [ ] Suporte a múltiplos ativos e *order types* (limit/stop).  
- [ ] Métricas e *reporting* (PnL, Sharpe, drawdown).  
- [ ] Hooks de eventos (pré/pós-tick).  
- [ ] *Backtesting* com dados reais (adaptação em `datasets`).  

---

## 🤝 Contribuindo

Veja [CONTRIBUTING.md](CONTRIBUTING.md) e nosso [Código de Conduta](CODE_OF_CONDUCT.md).  
Bugs e ideias: **Issues** no GitHub.

---

## 📜 Licença

[MIT](LICENSE).

---

## 📚 Citar

Se este projeto te ajudou em artigos/relatórios, cite como:

```bibtex
@software{mercadolab_2025,
  title   = {MercadoLab: laboratório de simulações baseadas em agentes para mercados},
  author  = {Sanches de Jesus, Raphael Mauricio},
  year    = {2025},
  url     = {https://github.com/Hargenx/mercadolab},
  version = {0.1.0}
}
```
