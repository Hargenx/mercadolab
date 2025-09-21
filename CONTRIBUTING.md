# Contribuindo para o MercadoLab

Obrigado por contribuir!

## Requisitos de desenvolvimento

- Python 3.10+
- `pip install -e ".[dev]"`

## Estilo

- Use Ruff (PEP8 + lint): `ruff check .`
- Tipagem opcional com MyPy: `mypy src/mercadolab`

## Testes

- `pytest` (execução rápida)
- Evite dependências pesadas

## Plugins

Exporte seu agente via entry-point no grupo `mercadolab.plugins`.
