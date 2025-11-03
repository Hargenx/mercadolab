# Contribuindo para o MercadoLab

Obrigado por considerar contribuir com este projeto.

MercadoLab é um framework minimalista de componentes para ABM em mercados financeiros artificiais.  
O princípio fundamental é: **não impor microestrutura**.  
Toda contribuição deve preservar essa propriedade.

---

## Princípios fundamentais (obrigatórios)

Toda PR deve manter estes axiomas:

1. MercadoLab não implementa microestrutura de mercado.
2. MercadoLab não possui “engine”.
3. MercadoLab não cria cenários, dados ou artefatos experimentais.
4. MercadoLab entrega *somente* blocos base + paralelismo eficiente.
5. Investidor segue o contrato: `decidir(ativo, tempo) -> Side`.

Se a contribuição sugerida tenta embutir lógica de mercado ou modelo de preço, ela provavelmente pertence a:

- um plugin externo
- um exemplo dentro de `examples/`
- ou a um projeto externo a este repositório.

---

## Estrutura do repositório

src/mercadolab/api         → tipos públicos (Ativo, Tempo, Dinheiro, Side, Investidor, Transacao)  
src/mercadolab/internal    → agendamento paralelo, utilidades e otimizações  
examples/                  → exemplos de uso (opcionais, demonstrativos)  
tests/                     → suíte de teste e benchmarks

---

## Regras de código

- Python >= 3.11
- dataclasses com `slots=True`
- evitar alocações desnecessárias dentro do hot-path (run_tick)
- nada de logging, prints ou I/O dentro do scheduler
- alterações de desempenho: apresentar benchmark comparativo **antes e depois**

Linter:

```bash
ruff check .
```

Testes:

```bash
pytest
```

Benchmarks:

```bash
pytest --benchmark-only
```

Uma PR que mexa em `scheduler.py` sem benchmark é automaticamente rejeitada.

---

## Pull Requests

Para aceitar uma PR:

- Deve ser pequena, objetiva.
- Deve vir acompanhada de testes.
- Se alterar performance: benchmarks antes/depois.
- Se adicionar API pública: abrir Issue de discussão **antes**.
- Se adicionar microestrutura: NÃO entra.

---

## Plugins externos

Microestrutura deve ser publicada como plugin externo ou como pacote separado.

Nome sugerido de namespace PyPI:

`mercadolab-nome-do-projeto`

---

## Decisões técnicas

Toda mudança estrutural deve ser documentada em `CHANGELOG.md`.

---

## Comunicação

Abra Issues para:

- propostas de melhoria de performance
- novas otimizações da hot-path
- instrumentação opcional (opt-in)
- novas abstrações minimalistas (com justificativa formal)

issues que pedem "adicionar Market" ou "simulação padrão" → serão fechadas como *wontfix*

---

## Obrigado

Cada melhoria de performance aqui tem impacto direto na capacidade de pesquisa.
O foco deste projeto é ser uma base limpa, mínima e **veloz**.

Contribuições que mantêm essa visão são extremamente bem-vindas.
