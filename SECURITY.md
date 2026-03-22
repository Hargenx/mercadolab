# Security Policy — MercadoLab

## Supported Versions

MercadoLab segue a baseline mínima de Python >= 3.11.

Somente a versão mais recente publicada no PyPI é considerada “ativa” para propósito de segurança.

Versões anteriores, experimentais ou ramos antigos não recebem suporte de correção de segurança.

---

## Threat Model

MercadoLab é um framework de pesquisa.

Ele **não** realiza, como parte obrigatória do núcleo:

- comunicação de rede
- persistência externa
- carregamento remoto de código
- chamadas de sistema privilegiadas
- leitura automática de arquivos externos

Portanto, a superfície de ataque típica do núcleo é relativamente baixa.

Os riscos mais relevantes neste contexto estão associados a:

- callbacks e hooks definidos pelo usuário
- executores customizados
- extensões locais de cenário ou comportamento
- uso inseguro de código arbitrário em camadas construídas sobre o framework

---

## Vulnerabilidades possíveis neste contexto

- execução inesperada de código por meio de extensões definidas pelo usuário
- vazamento de estado via hooks que compartilhem variáveis globais
- deadlocks, starvation ou comportamento indefinido com executores não padronizados
- inconsistências de validação em componentes centrais do domínio ou da execução

**Nota:** riscos introduzidos por código externo escrito pelo próprio usuário ou por extensões locais não são, por si só, falhas do núcleo do framework. Ainda assim, comportamentos inseguros causados por contratos ambíguos, validações ausentes ou superfícies mal definidas devem ser reportados.

---

## Como reportar vulnerabilidades

Se você acredita que encontrou um comportamento com impacto de segurança, por favor abra uma Issue PRIVADA através de:

<https://github.com/Hargenx/mercadolab/security/advisories>

ou, se preferir comunicação discreta por e-mail:

<raphael.mauricio@gmail.com>

Por favor inclua:

- descritivo do problema
- versão do mercadolab (`pip show mercadolab`)
- plataforma (Windows / Linux / Mac)
- snippet de código que reproduz o problema

---

## Política de divulgação

Responsável por confirmação: mantenedor(a)

Confirmação inicial: até 14 dias úteis  
Correção (se aplicável): 15 a 45 dias úteis após reprodução

Vulnerabilidades serão publicadas em:

- `GitHub Security Advisories`
- `CHANGELOG.md`

---

## Notas finais

MercadoLab não é um sistema crítico de produção.
É uma ferramenta voltada principalmente à pesquisa, ensino e experimentação computacional.

Ainda assim, clareza contratual, previsibilidade e rastreabilidade continuam sendo importantes.

Obrigado por colaborar para manter este projeto seguro e confiável.
