<!--
Responsabilidade: Decisão de arquitetura referente ao modelo de execução do Bedrock Dedicated Server no Proxmox LXC.
Compara a execução nativa gerenciada pelo systemd versus Docker encapsulado dentro do container LXC.
-->
---
document_id: adr-001-runtime-execution-model
title: Modelo de Execução do BDS em Container Proxmox LXC
document_type: adr
status: proposed
version: 1.0.0
language: pt-BR
owners: [architecture-maintainers]
last_updated: "2026-09-28"
review_cycle_days: 365
license: MIT
---

# ADR-001: Modelo de Execução do BDS em Container Proxmox LXC

## Estado

`proposed` — 2026-09-28 — Decisores: Equipe de Engenharia / Mantenedor do Projeto.

## Contexto

O servidor Bedrock Dedicated Server (BDS) será hospedado em um ambiente de virtualização Proxmox VE, em um container LXC executando uma distribuição Linux com suporte oficial (Ubuntu 22.04 LTS ou 24.04 LTS). O host possui aproximadamente 12 GB de memória RAM que são compartilhados concorrentemente com outros serviços e containers.

Forças em tensão:
1. **Consumo de Recursos & Eficiência**: O ambiente possui ~12 GB de RAM compartilhados. Todo overhead desnecessário de daemons secundários reduz a memória disponível para o cache de chunks e processamento de entidades do Minecraft.
2. **Suporte Oficial da Mojang**: O manual oficial (`bedrock_server_how_to.html`, v1.26.52.3) declara explicitamente suporte a Ubuntu 18 ou superior via execução ELF nativa de 64 bits (`LD_LIBRARY_PATH=. ./bedrock_server`).
3. **Complexidade Operacional e Segurança**: Rodar Docker dentro de containers LXC não privilegiados (unprivileged LXC) exige a habilitação de recursos avançados no Proxmox como aninhamento (`nesting=1`), `keyctl=1`, e suporte a drivers de armazenamento overlayfs em ZFS/ext4, ampliando a superfície de ataque e a complexidade de manutenção.
4. **Ciclo de Vida do Serviço**: É necessário garantir início automático no boot, reinício em caso de falha (`Restart=on-failure`), limites de recursos (`cgroups`), gerenciamento centralizado de logs via `journalctl` e execução sob usuário sem privilégios de root (`bedrock`).

## Opções consideradas

### Opção 1: Serviço Systemd Nativo sob Usuário sem Privilégios no LXC (Recomendada)
- **Funcionamento**: O BDS é instalado diretamente no filesystem do container LXC (Ubuntu LTS). Um usuário de sistema dedicado (`bedrock:bedrock`) sem privilégios administrativos executa o processo gerenciado por uma unit do `systemd` (`minecraft-bedrock.service`).
- **Vantagens**:
  - **Zero Overhead Adicional**: Não há daemons de contêineres secundários (dockerd, containerd) consumindo memória ou ciclos de CPU.
  - **Integração Total com o SO**: Reinício automático nativo, controle fino de limites de memória/CPU via `cgroups` da unit, rotação de logs automática via `journald` e monitoramento via `systemctl`.
  - **Simplicidade no Proxmox**: O container LXC permanece 100% não privilegiado padrão, sem necessidade de hacks de `nesting` ou manipulação complexa de namespaces no Proxmox.
  - **Aderência Estrita à Documentação Oficial**: Execução direta do binário conforme instruído no `bedrock_server_how_to.html`.
- **Desvantagens**:
  - O isolamento entre versões depende de disciplina de diretórios no filesystem em vez de imagens OCI.

### Opção 2: Docker dentro do Container LXC (Docker-in-LXC)
- **Funcionamento**: Instala-se o daemon do Docker dentro do container LXC do Proxmox para rodar imagens da comunidade (como `itzg/minecraft-bedrock-server`).
- **Vantagens**:
  - Imagens pré-empacotadas da comunidade que encapsulam alguns scripts utilitários.
- **Desvantagens**:
  - **Overhead Desnecessário**: O container Docker roda dentro do container LXC (camada dupla de namespaces), consumindo entre 150 MB e 300 MB extras apenas para os processos do Docker (`dockerd`, `containerd`, `docker-proxy`).
  - **Incompatibilidade com LXC Não Privilegiado Padrão**: Requer ajustes no Proxmox (`features: nesting=1`, `keyctl=1`), podendo introduzir problemas com drivers de storage (fuse-overlayfs) e permissões de UID/GID mapping.
  - **Camada Abstrata Oculta**: Scripts de terceiros encapsulados dificultam a auditoria estrita de conformidade com as fontes oficiais e o controle de versão do binário.

## Decisão

Adotar a **Opção 1: Serviço Systemd Nativo sob Usuário sem Privilégios no LXC**.

O servidor rodará em um container LXC Ubuntu 22.04 LTS ou 24.04 LTS no Proxmox.
A execução será gerenciada por uma unit `minecraft-bedrock.service` do systemd, com as seguintes diretivas obrigatórias:
- `User=bedrock` e `Group=bedrock`.
- `Restart=on-failure` com `RestartSec=10s`.
- `StandardOutput=journal` e `StandardError=journal`.
- Diretivas de reforço de segurança do systemd (`ProtectSystem=full`, `ProtectHome=true`, `NoNewPrivileges=true`).

## Consequências

- **Efeitos Positivos**:
  - Consumo mínimo de memória (~30-50 MB em repouso vs centenas de MB com Docker-in-LXC).
  - Configuração limpa e reproduzível via scripts shell idempotentes e unit systemd versionada.
  - Diagnóstico simples e padronizado via `systemctl status` e `journalctl -u minecraft-bedrock`.
- **Efeitos Negativos / Trabalho Decorrente**:
  - Necessidade de implementar a automação de atualização e backup via scripts shell modulares e auditados no próprio repositório.
- **Modos de Falha**:
  - Se o processo do BDS travar, o systemd reinicia o serviço automaticamente de acordo com o intervalo estipulado.

## Plano de validação e reversão

- **Sinais de Sucesso**:
  - O serviço sobe sem erros: `systemctl is-active minecraft-bedrock` retorna `active`.
  - Processo pertence ao usuário `bedrock`: `ps aux | grep bedrock_server` confirma UID não root.
  - Reinício automático sob falha comprovado por teste com `kill -9`.
- **Procedimento de Reversão**:
  - Em caso de necessidade de desativação: `systemctl stop minecraft-bedrock && systemctl disable minecraft-bedrock`.

## Referências

- Documentação Oficial BDS: `bedrock_server_how_to.html` (v1.26.52.3) - Seção *Platforms -> Linux*.
- URL Oficial de Download: [https://www.minecraft.net/en-us/download/server/bedrock](https://www.minecraft.net/en-us/download/server/bedrock)
- Systemd Service Documentation: [systemd.service(5)](https://www.freedesktop.org/software/systemd/man/systemd.service.html)
