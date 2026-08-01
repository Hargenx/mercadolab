# Changelog

Todas as mudanças notáveis neste projeto serão documentadas aqui.

## [Unreleased]

### Added

- Inclusão do cenário `mercadolab.scenarios.exemplo_coleta_metricas` para coleta e exportação de métricas experimentais.
- Inclusão do cenário `mercadolab.scenarios.exemplo_graficos_metricas` para geração de visualizações a partir das métricas coletadas.
- Inclusão de teste automatizado de reprodutibilidade que compara duas execuções completas do cenário anual com a mesma seed.

### Changed

- Ampliação do teste de integração de `Mercado` para verificar as posições finais do comprador e do vendedor após a liquidação.
- Ajustes de estilo, imports e tipagem verificados com Ruff e Mypy.
- Atualização do `README.md` para explicitar a microestrutura básica com prioridade preço-tempo e separar o comportamento dos agentes do núcleo.
- Atualização do `CONTRIBUTING.md` para refletir a estrutura atual do repositório, os contratos vigentes e as regras de reprodutibilidade.

### Removed

- Remoção do `ParallelScheduler`, incompatível com a API atual baseada em ordens, livro de ofertas, mercado e simulação.
- Remoção do benchmark antigo `bench_scheduler_tick.py`, que dependia do scheduler e dos contratos anteriores.
- Remoção de regras e referências documentais relacionadas ao scheduler antigo.

## [0.2.0] - 2026-04-12

### Added

- Consolidação do núcleo público da framework com as classes:
  - `Ativo`
  - `Tempo`
  - `Investidor`
  - `Carteira`
  - `Posicao`
  - `Ordem`
  - `Transacao`
  - `LivroDeOfertas`
  - `Mercado`
  - `Simulacao`
- Introdução explícita de `Posicao` como componente patrimonial do domínio.
- Reintrodução de `Ordem` como módulo próprio do núcleo público.
- Reintrodução de `LivroDeOfertas` como estrutura pública de organização das ordens por ativo.
- Inclusão de `Simulacao` como camada de orquestração temporal da framework.
- Implementação de submissão de ordens em `Mercado` com:
  - processamento de ordens limitadas e a mercado;
  - geração de `Transacao`;
  - atualização de estado das ordens;
  - liquidação patrimonial via `Carteira` e `Posicao`;
  - registro de histórico de transações.
- Inclusão de exemplos executáveis:
  - `mercadolab.scenarios.exemplo_minimo_fii`
  - `mercadolab.scenarios.exemplo_simulacao_anual`
- Inclusão de suíte inicial de testes automatizados com `pytest` cobrindo o núcleo da framework.

### Changed

- Reposicionamento do MercadoLab como **framework para construção de cenários de mercados artificiais**, e não como implementação fechada de uma microestrutura específica.
- Redefinição da API pública do projeto para refletir o núcleo atual do domínio e da simulação.
- Atualização da modelagem conceitual para separar explicitamente:
  - instrumento negociável;
  - participante;
  - patrimônio;
  - ordem;
  - transação;
  - livro de ofertas;
  - mercado;
  - simulação.
- `Ativo` passou a representar um instrumento negociável com:
  - `ticker`
  - `tipo`
  - `nome`
  - `moeda`
  - `tick_size`
  - `lote_padrao`
  - `negociavel`
- `Tempo` passou a ser tratado como abstração temporal discreta da simulação, com suporte a `tick`, `timestamp` opcional e `sessao` opcional.
- `Investidor` passou a representar apenas o participante do mercado, sem impor estratégia embutida ou contrato obrigatório de decisão.
- `Carteira` passou a centralizar o estado patrimonial do participante.
- `Mercado` deixou de ser apenas catálogo de ativos e passou a agregar:
  - ativos;
  - livros de ofertas;
  - transações;
  - submissão e processamento de ordens.
- `Simulacao` foi desenhada de forma neutra, recebendo ordens geradas externamente sem impor políticas de decisão aos investidores.
- A estratégia de geração de ordens e o comportamento dos agentes passaram a ser explicitamente responsabilidade do usuário da framework, não do núcleo do projeto.

### Refactored

- Refatoração completa da terminologia do domínio para português consistente:
  - `Order` → `Ordem`
  - `Transaction` → `Transacao`
  - nomenclatura associada ao núcleo atual
- Refatoração da modelagem de execução para distinguir claramente:
  - intenção de negociação (`Ordem`)
  - execução efetiva (`Transacao`)
- Refatoração da modelagem patrimonial para separar:
  - `Investidor`
  - `Carteira`
  - `Posicao`
- Refatoração de `Mercado` para assumir papel de coordenador da submissão de ordens no domínio.
- Refatoração dos exemplos para execução como módulos do pacote.
- Limpeza de imports e referências obsoletas em `mercadolab.scenarios`.

### Fixed

- Correção da execução dos exemplos como módulos do pacote via `python -m ...`.
- Correção de imports relativos e absolutos em exemplos e cenários.
- Correção do `__init__.py` de `mercadolab.scenarios` para remover referências a cenários obsoletos.
- Correção da lógica de compatibilidade de ordens em `Mercado` para lidar corretamente com `preco_limite: Decimal | None`.
- Ajustes na ordenação e uso do `LivroDeOfertas` para manter coerência com ordens limitadas ativas.
- Ajustes na tipagem dos exemplos para aceitar sequências de investidores sem conflito com `tuple`.

### Documentation

- Reescrita do `README.md` para refletir a arquitetura atual da framework.
- Atualização do exemplo principal de uso com base no núcleo atual.
- Inclusão de orientação de execução dos exemplos como módulos do pacote.
- Revisão do `CONTRIBUTING.md` para alinhar o processo de contribuição à arquitetura atual do projeto.
- Atualização da documentação conceitual para enfatizar que:
  - a framework fornece infraestrutura;
  - estratégias e regras específicas ficam em aberto;
  - diferentes mercados podem ser construídos sobre a mesma base.

### Testing

- Inclusão de testes automatizados para:
  - `Ativo`
  - `Ordem`
  - `LivroDeOfertas`
  - `Carteira`
  - `Mercado`
  - `Simulacao`
  - `Transacao`
- Validação do fluxo ponta a ponta com testes passando sobre o núcleo atual.

## [0.1.0] - 2025-09-20

### Added

- Estrutura inicial do projeto.
- CLI com `quickstart`, `plugins` e `run`.
- Plugin de exemplo `RandomTrader`.
