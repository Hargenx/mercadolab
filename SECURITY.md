# Política de Segurança — MercadoLab

## Versões suportadas

O MercadoLab requer Python 3.11 ou superior.

O projeto ainda não possui uma versão publicada no PyPI. Durante esta fase de desenvolvimento, o suporte de segurança considera apenas o estado atual da branch `main` do repositório oficial.

Instalações baseadas em commits antigos, forks, versões experimentais ou ramos descontinuados não recebem correções de segurança.

---

## Modelo de ameaça

O MercadoLab é uma framework voltada principalmente a pesquisa, ensino e experimentação computacional.

O núcleo não realiza automaticamente:

- comunicação de rede;
- persistência externa;
- carregamento remoto de código;
- chamadas privilegiadas ao sistema;
- leitura de arquivos fornecidos pelo usuário.

Cenários e extensões construídos sobre a framework podem utilizar arquivos, bibliotecas opcionais ou integrações externas. Nesses casos, a segurança também depende do código e das dependências adicionadas pelo usuário.

A superfície de risco mais relevante para o núcleo está relacionada à validação de entradas, à consistência do estado da simulação e ao consumo de recursos.

---

## Vulnerabilidades possíveis neste contexto

Comportamentos que devem ser reportados incluem:

- aceitação de ordens ou valores inválidos que comprometam o estado da simulação;
- inconsistências entre ordens, transações, caixa e posições;
- possibilidade de contornar validações patrimoniais ou de negociação;
- consumo descontrolado de memória ou processamento causado por entradas especialmente construídas;
- exposição involuntária de dados pelo núcleo;
- vulnerabilidades em dependências obrigatórias ou opcionais distribuídas pelo projeto;
- contratos públicos ambíguos que permitam comportamentos inseguros não documentados.

Problemas causados exclusivamente por estratégias, cenários ou integrações externas escritos pelo usuário não são, por si só, vulnerabilidades do núcleo. Ainda assim, falhas provocadas por validações ausentes ou contratos públicos incorretos devem ser reportadas.

---

## Como reportar vulnerabilidades

Não publique detalhes de uma possível vulnerabilidade em uma Issue pública.

Use preferencialmente o canal de denúncia privada do GitHub:

<https://github.com/Hargenx/mercadolab/security/advisories>

Se o botão **Report a vulnerability** não estiver disponível, envie o relato por e-mail:

<raphael.mauricio@gmail.com>

Inclua, quando possível:

- descrição do comportamento e do possível impacto;
- versão declarada do MercadoLab, obtida com `pip show mercadolab`;
- commit utilizado, obtido com `git rev-parse HEAD`;- versão do Python;
- sistema operacional;
- exemplo mínimo ou passos para reprodução;
- condições necessárias para que o problema ocorra;
- possíveis medidas de mitigação já identificadas.

Não inclua credenciais, tokens, dados pessoais ou informações confidenciais desnecessárias no relato.

---

## Política de divulgação

Os relatos serão tratados pelo mantenedor do projeto seguindo este fluxo:

1. confirmação inicial do recebimento em até 14 dias úteis;
2. análise do impacto e tentativa de reprodução;
3. solicitação de informações adicionais, quando necessária;
4. preparação e validação de uma correção ou mitigação;
5. divulgação coordenada após a disponibilização da correção.

Quando o problema for reproduzido e exigir alteração no projeto, a meta é disponibilizar uma correção ou mitigação entre 15 e 45 dias úteis. Esse prazo pode variar conforme a complexidade, o impacto e a disponibilidade do mantenedor.

Até a divulgação coordenada, solicita-se que os detalhes técnicos não sejam publicados em canais abertos.

Vulnerabilidades confirmadas poderão ser documentadas em:

- GitHub Security Advisories;
- `CHANGELOG.md`;
- notas da versão corrigida.

---

## Notas finais

MercadoLab não é um sistema crítico de produção.
É uma ferramenta voltada principalmente à pesquisa, ensino e experimentação computacional.

Ainda assim, clareza contratual, previsibilidade e rastreabilidade continuam sendo importantes.

Obrigado por colaborar para manter este projeto seguro e confiável.
