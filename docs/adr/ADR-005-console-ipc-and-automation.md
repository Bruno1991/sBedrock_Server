<!--
Responsabilidade: Decisão de arquitetura sobre a interface de comunicação entre processos (IPC)
com o console do BDS para envio de comandos de automação (backup, reload de allowlist, shutdown limpo).
-->
---
document_id: adr-005-console-ipc-and-automation
title: Comunicação entre Processos (IPC) e Controle do Console do BDS
document_type: adr
status: proposed
version: 1.0.0
language: pt-BR
owners: [architecture-maintainers]
last_updated: "2026-09-28"
review_cycle_days: 365
license: MIT
---

# ADR-005: Comunicação entre Processos (IPC) e Controle do Console do BDS

## Estado

`proposed` — 2026-09-28 — Decisores: Equipe de Engenharia / Mantenedor do Projeto.

## Contexto

O executável oficial `bedrock_server` é uma aplicação que lê comandos de administração exclusivamente através da entrada padrão (`stdin`) e imprime respostas na saída padrão (`stdout`/`stderr`). Não há API HTTP ou protocolo RCON nativo embutido no BDS oficial da Mojang.

Para executar tarefas automatizadas sem intervenção humana — tais como:
1. Enviar os comandos de backup a quente (`save hold`, `save query`, `save resume`) e ler a lista de arquivos retornada;
2. Recarregar a lista de permissões e de acesso (`allowlist reload`, `permission reload`);
3. Desligar o servidor de forma limpa (`stop`) antes de atualizações ou reinicializações do sistema;
4. Permitir que o operador humano anexe interativamente um terminal ao console quando necessário para emitir comandos manuais (`bds-console`).

É indispensável definir uma arquitetura de IPC robusta, que mantenha um pseudoterminal (PTY) ou canal persistente sem causar encerramento precoce por `EOF` (End of File).

## Opções consideradas

### Opção 1: Sessão Tmux Isolada Gerenciada pelo Systemd (Recomendada)
- **Funcionamento**: A unit do systemd inicia o binário dentro de uma sessão desacoplada do Tmux (`tmux new-session -d -s bds-server 'LD_LIBRARY_PATH=. ./bedrock_server'`).
- **Envio de Comandos**: Scripts executam `tmux send-keys -t bds-server "<comando>" ENTER`.
- **Leitura de Respostas**: Scripts capturam as últimas linhas do terminal via `tmux capture-pane -pt bds-server -S -50`.
- **Acesso Interativo do Operador**: Um comando simples `bds-console` faz `tmux attach -t bds-server`. Para sair sem fechar o servidor, o operador usa `Ctrl+B, D`.
- **Vantagens**:
  - Fornece um pseudoterminal (PTY) completo, evitando problemas de buffering de stdout no `bedrock_server`.
  - Permite tanto automação por scripts quanto conexão interativa direta pelo operador humano.
  - Consumo de memória desprezível (< 3 MB de RAM).
- **Desvantagens**:
  - Requer o pacote `tmux` instalado no container LXC.

### Opção 2: Named Pipe (FIFO) com Redirecionamento de Stdin
- **Funcionamento**: Cria-se um named pipe (`mkfifo /run/bds/stdin.fifo`). O serviço systemd inicia o binário lendo do pipe (`./bedrock_server < /run/bds/stdin.fifo`).
- **Vantagens**: Não requer dependências de pacotes externos como Tmux.
- **Desvantagens**:
  - **Problema de EOF no Linux**: Se o processo escritor fechar o pipe, o `bedrock_server` detecta EOF e encerra o processo imediatamente, exigindo truques de shell complexos (`cat` em loop ou redirecionamento de descritores).
  - **Captura de Saída Complexa**: Dificuldade em correlacionar respostas a comandos específicos via arquivo de log plano sem race conditions.
  - **Acesso Interativo Inconveniente**: Não oferece visualização bidirecional em tempo real para o operador humano.

## Decisão

Adotar a **Opção 1: Sessão Tmux Isolada Gerenciada pelo Systemd**.

A unit `minecraft-bedrock.service` iniciará o processo em uma sessão Tmux dedicada (`bds-server`) sob o usuário de sistema `bedrock`.

Serão fornecidas as seguintes ferramentas de controle:
- Utilitário de linha de comando `bds-cmd <comando>`: Envia comandos ao console via Tmux e registra a ação no log de auditoria.
- Utilitário interativo `bds-console`: Anexa o terminal do operador diretamente à sessão Tmux para monitoramento ao vivo.
- Wrapper de parada limpa no systemd (`ExecStop=/opt/bds/scripts/bds-cmd stop` com timeout de 30s).

## Consequências

- **Efeitos Positivos**:
  - O fluxo de backup oficial (`save hold` / `save query` / `save resume`) pode injetar comandos e ler com segurança os arquivos retornados usando `tmux capture-pane`.
  - Parada graciosa segura através de comando `stop` antes de SIGTERM, garantindo que o mundo seja salvo no disco sem chunks órfãos.
  - Experiência fluida para o administrador entrar e sair do console do servidor.
- **Efeitos Negativos**:
  - Dependência do pacote `tmux` (adicionado à lista de pacotes pré-requisitos do container LXC).

## Plano de validação e reversão

- **Sinais de Sucesso**:
  - `systemctl start minecraft-bedrock` cria a sessão `bds-server`.
  - `bds-cmd "help"` imprime a ajuda oficial do console do BDS.
  - `bds-cmd "allowlist reload"` recarrega a allowlist com sucesso.
  - `systemctl stop minecraft-bedrock` envia `stop` e aguarda o desligamento limpo antes de encerrar o processo.
- **Procedimento de Reversão**:
  - Caso o uso de Tmux apresente qualquer incompatibilidade, a unit pode ser revertida para execução de processo direto com `StandardInput=null`.

## Referências

- Documentação Oficial BDS: `bedrock_server_how_to.html` (v1.26.52.3) - Seção *Commands*.
- Tmux Documentation: [tmux(1) manual](https://man7.org/linux/man-pages/man1/tmux.1.html).
