# Contribuindo para pex3

Obrigado por querer contribuir com o pex3! Este documento descreve como reportar problemas, propor melhorias e enviar código para revisão. Se for a sua primeira contribuição, obrigado — qualquer contribuição é bem-vinda.

Sumário
- [Primeiros passos](#primeiros-passos)
- [Reportando bugs e pedindo features](#reportando-bugs-e-pedindo-features)
- [Como abrir um Pull Request (PR)](#como-abrir-um-pull-request-pr)
- [Configuração do ambiente de desenvolvimento](#configuração-do-ambiente-de-desenvolvimento)
- [Testes e Integração Contínua (CI)](#testes-e-integração-contínua-ci)
- [Estilo de código e linters](#estilo-de-código-e-linters)
- [Mensagens de commit](#mensagens-de-commit)
- [Processo de revisão](#processo-de-revisão)
- [Segurança](#segurança)
- [Código de Conduta e licença](#código-de-conduta-e-licença)
- [Agradecimentos](#agradecimentos)

## Primeiros passos
1. Leia o `README.md` para entender o propósito do projeto e o escopo atual.
2. Procure por issues com as labels `good first issue` ou `help wanted` se quiser começar por algo simples.
3. Se for trabalhar em algo significativo, abra uma issue descrevendo a intenção antes de começar — isso evita trabalho duplicado.

## Reportando bugs e pedindo features
Ao abrir uma issue, tente incluir:
- Título curto e claro.
- Descrição do problema ou da funcionalidade desejada.
- Passos para reproduzir (para bugs).
- Resultado esperado x resultado atual.
- Versões relevantes (ex.: versão do Python, navegador, sistema operacional).
- Logs, capturas de tela ou exemplos mínimos quando aplicável.

Modelos de issue (`.github/ISSUE_TEMPLATE/`) são recomendados para padronizar relatórios.

## Como abrir um Pull Request (PR)
1. Fork e clone o repositório:
   - git clone https://github.com/Delean-Mafra/pex3.git
2. Crie uma branch descritiva:
   - git checkout -b feat/minha-nova-funcionalidade
   - ou git checkout -b fix/corrige-xyz
3. Faça commits pequenos e atômicos com mensagens claras.
4. Garanta que os testes passam e que o código segue o estilo do projeto.
5. Abra um PR contra a branch `main` do repositório original com:
   - Um título claro.
   - Descrição do que o PR faz e por quê.
   - Links para issues relacionadas (use `Fixes #<n>` quando apropriado).
6. Esteja disponível para responder comentários e fazer mudanças até o merge.

Observação: se optar pelo merge direto em `main`, prefira usar PRs para manter histórico e revisão.

## Configuração do ambiente de desenvolvimento
Instruções básicas para desenvolver localmente (ajuste conforme necessário):

1. Clone o repositório:
   - git clone https://github.com/Delean-Mafra/pex3.git
   - cd pex3

2. Ambiente Python:
   - python -m venv .venv
   - source .venv/bin/activate  # macOS/Linux
   - .venv\Scripts\Activate     # Windows (PowerShell)
   - pip install -U pip
   - pip install -r requirements.txt  # se existir

3. Frontend / HTML:
   - Se houver ferramentas JS (Node), execute:
     - npm install
   - Caso sejam apenas arquivos HTML estáticos, abra-os no navegador.

4. Rodar testes:
   - pytest  # se o projeto usar pytest

Adicione instruções específicas (como variáveis de ambiente, banco de dados, comandos de build) nesta seção conforme necessário.

## Testes e Integração Contínua (CI)
- Escreva testes automatizados para funcionalidades principais.
- Configure workflows de CI (por exemplo GitHub Actions) para rodar testes e linters em PRs.
- Recomenda-se bloquear merges quando tests/lints falharem.

## Estilo de código e linters
Para manter consistência, sugerimos:
- Python:
  - Formatação automática: `black`
  - Linting: `flake8`
  - Ordenação de imports: `isort`
- HTML/CSS:
  - Validar HTML (ex.: W3C validator) e verificar acessibilidade básica.
- Hooks:
  - Use `pre-commit` para executar formatação/lint antes dos commits.

Exemplo rápido:
- pip install black flake8 isort pre-commit
- pre-commit install
- black .
- flake8

## Mensagens de commit
Use mensagens claras; recomendamos seguir o estilo "Conventional Commits", por exemplo:
- feat: adicionar nova funcionalidade
- fix: corrigir bug
- docs: alteração na documentação
- chore: tarefas de manutenção
- refactor: refatoração sem mudança de comportamento

Exemplo: `feat: adicionar validação no formulário de contato`

## Processo de revisão
- PRs recebem revisão por pelo menos um mantenedor ou contribuidor ativo.
- Feedback pode incluir mudanças de estilo, segurança, testes e documentação.
- Mantenedores podem solicitar rebase ou atualização com a branch `main`.

## Segurança
- Não divulgue vulnerabilidades em issues públicas.
- Para problemas de segurança, por favor contate o mantenedor.
- Inclua impacto, passos para reproduzir e sugestões de mitigação.

## Código de Conduta e licença
- Este projeto segue um Código de Conduta para manter um ambiente acolhedor. Adicione ou consulte `CODE_OF_CONDUCT.md` (recomendado: Contributor Covenant).
- Respeite a licença do projeto (veja `LICENSE` no repositório).

## Agradecimentos
Obrigado por contribuir! Seu tempo e esforço tornam este projeto melhor. Reconhecimentos são bem-vindos em PRs e issues.

---

Se desejar, eu também posso:
- Adicionar templates de issue/PR em `.github/ISSUE_TEMPLATE/` e `.github/PULL_REQUEST_TEMPLATE/`.
- Incluir um `.pre-commit-config.yaml` sugerido.
- Criar um PR automaticamente com este CONTRIBUTING.md (escolha a opção 2) ou commitar direto na `main` (opção 1).
