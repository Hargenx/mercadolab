# Contributing to MercadoLab

Obrigado por considerar contribuir com o **MercadoLab**.

Este projeto busca oferecer uma base **clara**, **extensível** e **reproduzível** para a criação de cenários de mercados artificiais baseados em agentes. Para manter essa proposta consistente ao longo do tempo, contribuições precisam respeitar alguns princípios arquiteturais e de qualidade.

---

## Princípios fundamentais

Toda contribuição deve preservar os seguintes princípios:

1. **MercadoLab não deve impor uma microestrutura específica de mercado.**
2. **O núcleo do projeto deve permanecer pequeno, claro e extensível.**
3. **Componentes de domínio, execução e cenários devem manter separação de responsabilidades.**
4. **Novas abstrações devem favorecer reusabilidade e neutralidade metodológica.**
5. **Investidor segue o contrato central:** `decidir(ativo, tempo) -> Side`.

Contribuições que embutem uma teoria econômica rígida, uma microestrutura obrigatória ou lógica experimental excessivamente específica provavelmente pertencem a:

- uma camada opcional de cenário;
- um exemplo em `examples/`;
- um módulo separado;
- ou um pacote complementar.

---

## Estrutura do repositório

A estrutura pode evoluir com o projeto, mas em geral o repositório segue esta organização:

```text
mercadolab/
├── src/mercadolab/          # núcleo do pacote
├── tests/                   # testes unitários, integração e benchmarks
├── examples/                # exemplos de uso
├── README.md
├── CHANGELOG.md
├── CONTRIBUTING.md
└── pyproject.toml                 → suíte de teste e benchmarks
```

---

Se sua contribuição altera a organização estrutural do projeto, explique claramente:

- o motivo da mudança;
- o impacto arquitetural;
- e como a alteração se relaciona com a identidade do MercadoLab.

---

## Tipos de contribuição aceitos

São especialmente bem-vindas contribuições que melhorem:

- clareza da API pública;
- consistência de nomes, contratos e docstrings;
- qualidade dos componentes centrais do domínio;
- mecanismos de execução e scheduler;
- exemplos de uso;
- testes;
- documentação;
- organização arquitetural;
- cenários de referência opcionais, desde que não contaminem o núcleo do projeto.

---

## Tipos de contribuição que exigem mais cuidado

Mudanças nas seguintes áreas exigem atenção especial:

- `Investidor`
- `Dinheiro`
- `Tempo`
- `Ativo`
- `Mercado`
- `Transacao`
- `scheduler.py`
- superfície pública do pacote (`__init__.py`)

Se sua PR alterar um desses pontos, explique claramente:

- o que mudou;
- por que mudou;
- qual o impacto na API;
- e se houve impacto em exemplos, testes ou documentação.

---

## Diretrizes de código

### Estilo geral

- Use **Python moderno e legível**.
- Prefira `snake_case` para funções e métodos.
- Use `PascalCase` para classes.
- Mantenha nomes claros e consistentes com o domínio do projeto.
- Evite misturar estilos de nomenclatura no mesmo módulo.

### Clareza e responsabilidade

- Cada classe ou função deve ter uma responsabilidade clara.
- Evite acoplamento desnecessário entre camadas.
- Se um comportamento pertence a um cenário específico, ele provavelmente não deve entrar no núcleo do pacote.

### Docstrings

- Mantenha docstrings em classes e métodos públicos.
- Prefira docstrings curtas, objetivas e informativas.
- A docstring deve explicar a intenção do elemento, não repetir trivialmente o nome.

### Tipagem

- Use type hints sempre que possível.
- Prefira assinaturas explícitas e estáveis.
- Se uma mudança de typing alterar a API pública, documente isso.

---

## Regras para o scheduler e hot-path

O scheduler é uma parte sensível do projeto.

Ao contribuir nessa área:

- preserve clareza de leitura;
- evite complexidade acidental;
- evite alocações desnecessárias no hot-path;
- explique qualquer mudança de comportamento;
- atualize testes e exemplos quando necessário.

Mudanças relevantes de desempenho no scheduler devem, sempre que possível, vir acompanhadas de benchmark ou comparação objetiva.

Refatorações de nomenclatura, clareza, correção funcional ou consistência arquitetural não precisam necessariamente de benchmark, desde que não alterem a intenção de desempenho do código.

---

## Testes

Toda contribuição relevante deve incluir ou atualizar testes.

Prioridades:

1. testes unitários para o núcleo do domínio;
2. testes de integração para o scheduler e fluxo básico de execução;
3. benchmarks quando houver impacto de desempenho relevante.

Se sua PR muda comportamento, a suíte de testes deve refletir isso.

---

## Benchmarks

Benchmarks são importantes, mas devem ser usados com critério.

Eles são especialmente úteis quando a contribuição:

- altera o scheduler;
- muda a estratégia de execução concorrente;
- modifica o caminho quente de decisão ou pareamento;
- impacta volume de objetos ou custo por tick.

Nem toda PR precisa incluir benchmark. Mas PRs com alegações de ganho de desempenho devem trazer evidência correspondente.

---

## Exemplos e cenários

Exemplos devem:

- ser curtos;
- ser executáveis;
- refletir a API atual do projeto;
- ajudar o usuário a entender o papel do núcleo e da camada de execução.

Cenários mais específicos podem ser aceitos desde que:

- não imponham uma teoria ao núcleo;
- fiquem claramente identificados como opcionais;
- não desorganizem a superfície pública do pacote.

---

## API pública

A API pública do topo do pacote deve permanecer **pequena e estável**.

Mudanças nessa superfície devem ser tratadas com cuidado especial.
Se uma PR:

- adiciona um novo símbolo ao topo do pacote;
- remove um símbolo existente;
- ou altera um contrato público;

então ela deve:

- justificar a mudança;
- atualizar documentação;
- atualizar testes relacionados à API pública;
- e registrar o impacto no `CHANGELOG.md`.

---

## CHANGELOG

Mudanças relevantes devem ser registradas no `CHANGELOG.md`, especialmente quando envolverem:

- API pública;
- comportamento do scheduler;
- contratos centrais do domínio;
- arquitetura do projeto;
- documentação de uso.

---

## Como abrir uma contribuição

Ao abrir uma PR, tente incluir:

- **Resumo da mudança**
- **Motivação**
- **Arquivos afetados**
- **Impacto na API pública**
- **Impacto em testes**
- **Impacto em documentação**
- **Observações adicionais**, se houver

---

## O que provavelmente será recusado

Contribuições com alta chance de rejeição incluem:

- lógica excessivamente específica de um único experimento no núcleo do pacote;
- abstrações pouco claras ou prematuras;
- mudanças grandes sem documentação do impacto;
- inconsistência de nomenclatura;
- quebra de API pública sem justificativa;
- funcionalidades que imponham uma única microestrutura como comportamento obrigatório do framework.

---

## Discussões e sugestões

Se você tiver dúvida sobre:

- arquitetura;
- escopo do núcleo;
- cenário opcional vs componente central;
- nomeação;
- ou impacto de uma refatoração;

abra uma issue antes da PR.

Isso ajuda a manter o projeto coerente e evita retrabalho.

---

## Código de conduta

Ao contribuir, siga também o [Código de Conduta](CODE_OF_CONDUCT.md).

Obrigado por ajudar a tornar o MercadoLab mais claro, consistente e útil para pesquisa, ensino e experimentação.

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
