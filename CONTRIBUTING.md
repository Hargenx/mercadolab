# Contributing to MercadoLab

Obrigado por considerar contribuir com o **MercadoLab**.

Este projeto busca oferecer uma base **clara**, **extensível** e **reproduzível** para a criação de cenários de mercados artificiais baseados em agentes. Para manter essa proposta consistente ao longo do tempo, contribuições precisam respeitar alguns princípios arquiteturais e de qualidade.

---

## Princípios fundamentais

Toda contribuição deve preservar os seguintes princípios:

1. **O MercadoLab fornece uma microestrutura básica e explícita**, atualmente baseada em livro de ofertas com prioridade preço-tempo.
2. **O núcleo não deve impor estratégias de negociação ou comportamentos específicos aos participantes.**
3. **O núcleo deve permanecer pequeno, claro, extensível e independente dos cenários experimentais.**
4. **API pública, implementação interna e cenários devem manter responsabilidades separadas.**
5. **Mudanças experimentais devem preservar ou documentar suas condições de reprodutibilidade.**

Contribuições que implementem estratégias específicas, regras comportamentais ou hipóteses de um experimento devem permanecer fora do núcleo. Dependendo de sua finalidade, elas podem ser apresentadas como:

- um cenário em `src/mercadolab/scenarios/`;
- um exemplo acadêmico claramente identificado;
- ou um pacote complementar construído sobre a API pública.

---

## Estrutura do repositório

A estrutura pode evoluir com o projeto, mas em geral o repositório segue esta organização:

```text
mercadolab/
├── .github/workflows/            # integração contínua e publicação
├── assets/                       # recursos visuais da documentação
├── src/mercadolab/
│   ├── api/                      # componentes públicos do domínio
│   ├── scenarios/                # cenários e exemplos executáveis
│   └── tests/                    # testes automatizados
├── README.md
├── CHANGELOG.md
├── CONTRIBUTING.md
├── SECURITY.md
└── pyproject.toml                # configuração do pacote e ferramentas
```

---

Se sua contribuição altera a organização estrutural do projeto, explique claramente:

- o motivo da mudança;
- o impacto arquitetural;
- e como a alteração se relaciona com a identidade do MercadoLab.

---

## Tipos de contribuição aceitos

São especialmente bem-vindas contribuições que melhorem:

- clareza e consistência da API pública;
- contratos, validações e docstrings dos componentes de domínio;
- processamento de ordens, pareamento e liquidação patrimonial;
- coordenação temporal e reprodutibilidade;
- testes automatizados;
- documentação e exemplos executáveis;
- cenários de referência que permaneçam separados do núcleo;
- coleta e exportação opcional de métricas;
- desempenho, quando acompanhado de evidência objetiva.

---

## Mudanças que exigem mais cuidado

Mudanças nas seguintes áreas exigem atenção especial:

- classes e enumerações em `src/mercadolab/api/`;
- processamento de ordens e regras de pareamento;
- atualização de caixa, posições e preço médio;
- avanço temporal da simulação;
- superfície pública exposta pelos arquivos `__init__.py`;
- estrutura do pacote e remoção de código legado.

Se sua contribuição alterar um desses pontos, explique claramente:

- o que mudou;
- por que a mudança é necessária;
- qual é o impacto na API e no comportamento existente;
- quais testes demonstram o novo comportamento;
- e se exemplos, documentação ou `CHANGELOG.md` também foram atualizados.

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

## Regras para o núcleo e o fluxo de execução

Mudanças no processamento do mercado devem:

- preservar ou documentar as regras de prioridade preço-tempo;
- manter consistentes ordens, transações, caixa e posições;
- evitar efeitos colaterais que não estejam explícitos na API;
- preservar as condições documentadas de reprodutibilidade;
- atualizar testes e exemplos quando houver mudança de comportamento.

Otimizações não devem reduzir a clareza do núcleo sem uma justificativa técnica e uma medição objetiva do benefício.

---

## Testes e verificações de qualidade

Toda contribuição relevante deve incluir ou atualizar testes.

As principais verificações do projeto são:

```bash
ruff check .
pytest
mypy
```

Prioridades da suíte:

1. testes unitários para contratos e validações do domínio;
2. testes de integração entre livro, mercado, carteiras e simulação;
3. testes de regressão para falhas corrigidas;
4. testes de reprodutibilidade para cenários determinísticos.

Se uma contribuição mudar um comportamento observável, a suíte deve demonstrar tanto o novo resultado quanto os invariantes que continuam válidos.

---

## Desempenho e medições

Contribuições com alegações de melhoria de desempenho devem apresentar evidências reproduzíveis, contendo:

- versão do código comparada;
- configuração utilizada;
- tamanho do cenário;
- quantidade de repetições;
- ambiente de execução;
- resultados antes e depois.

O projeto não exige benchmark para toda contribuição. Medições são necessárias quando desempenho for parte da justificativa da mudança.

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

A API destinada à construção de cenários está concentrada em `src/mercadolab/api/` e nos símbolos explicitamente exportados pelos arquivos `__init__.py`.

Os módulos em `src/mercadolab/scenarios/` são cenários de referência e não fazem parte da superfície pública estável.

Se uma contribuição:

- adicionar, remover ou renomear uma classe, enumeração, método ou atributo público;
- alterar uma assinatura existente;
- modificar validações ou resultados observáveis;
- ou mudar símbolos exportados por um arquivo `__init__.py`;

ela deve:

- justificar a mudança;
- atualizar os testes relacionados;
- atualizar exemplos e documentação;
- registrar incompatibilidades e instruções de migração;
- e incluir a alteração no `CHANGELOG.md`.

---

## CHANGELOG

Mudanças relevantes devem ser registradas no `CHANGELOG.md`, especialmente quando envolverem:

- API pública;
- processamento de ordens ou regras de pareamento;
- atualização patrimonial;
- coordenação temporal;
- reprodutibilidade;
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

- estratégias ou comportamentos experimentais acoplados ao núcleo;
- alterações nas regras de pareamento sem testes que demonstrem o comportamento;
- mudanças que deixem caixa, posições, ordens e transações inconsistentes;
- quebra de API pública sem justificativa e documentação de migração;
- abstrações prematuras ou sem caso de uso demonstrável;
- cenários pseudoaleatórios sem seed ou configuração experimental explícita;
- alegações de desempenho sem evidência reproduzível;
- mudanças grandes sem documentação do impacto arquitetural.

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
