# Security Policy — MercadoLab

## Supported Versions

MercadoLab segue a baseline mínima de Python >= 3.11.

Somente a versão mais recente publicada no PyPI é considerada “ativa” para propósito de segurança.

Versões anteriores, experimentais ou ramos antigos não recebem suporte de correção de segurança.

---

## Threat Model

MercadoLab é um framework de pesquisa.

Ele **não** faz:

- rede
- I/O externo
- persistência
- leitura de arquivos
- carregamento dinâmico remoto
- chamadas de sistema

Portanto a superfície de ataque típica é baixa.

O risco primário considerado aqui é:

- exceções não tratadas que permitam execução arbitrária via callback / plugin malicioso

---

## Vulnerabilidades possíveis neste contexto

- Execução de código via plugin (entry point mal-intencionado)
- “side-channel leaks” em hooks se o usuário criar plugins que compartilham estado global
- deadlocks / starvation se executor for substituído por executores não padronizados

**Nota:** estes riscos são inerentes ao design “plugin-based” — não são considerados responsabilidade do framework base.

---

## Como reportar vulnerabilidades

Se você acredita que encontrou um comportamento com impacto de segurança:

por favor abra uma Issue PRIVADA através de:
<https://github.com/Hargenx/mercadolab/security/advisories>

ou se preferir comunicação discreta por e-mail:

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
Correção (se aplicável): 15 a 45 dias úteis após repro

Vulnerabilidades serão publicadas em:
`GitHub Security Advisories`
e
`CHANGELOG.md`

---

## Notas finais

MercadoLab não é um sistema crítico.
É uma ferramenta para pesquisa científica.

Ainda assim — a rastreabilidade formal importa.

Obrigado por colaborar para manter este projeto seguro e previsível.
