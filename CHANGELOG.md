# Changelog

Todas as mudanças notáveis neste projeto serão documentadas aqui.

## [Unreleased]

### Changed

- Reposicionamento do MercadoLab como framework para criação de cenários de mercados artificiais baseados em agentes.
- Revisão da API pública do pacote para expor apenas o núcleo estável do domínio.
- Padronização de nomes e contratos em componentes centrais do domínio.
- Atualização da documentação principal para refletir a nova identidade arquitetural do projeto.
- Revisão da interface do scheduler para maior clareza e consistência com o núcleo do domínio.

### Refactored

- Refatoração de `Investidor` como base abstrata com contrato explícito de decisão.
- Refatoração de `Dinheiro` como value object imutável com validação explícita de moeda.
- Refatoração de `Transacao` para nomenclatura consistente com o domínio em português.
- Refatoração de `Mercado` para API em `snake_case`.
- Ajustes em `Ativo`, `Tempo` e `enums` para maior clareza e consistência.
- Revisão inicial da suíte de testes para acompanhar a nova API.

### Documentation

- Atualização do `README.md` com novo posicionamento, novo exemplo de uso e referência correta ao changelog.
- Revisão do `CONTRIBUTING.md` para alinhar o processo de contribuição à arquitetura atual do projeto.

## [0.1.0] - 2025-09-20

### Added

- Estrutura inicial do projeto
- CLI com `quickstart`, `plugins` e `run`
- Plugin de exemplo `RandomTrader`
