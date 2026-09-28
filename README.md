<!--
Responsabilidade: Documento de apresentacao principal do repositorio Bedrock Dedicated Server (BDS).
Apresenta o proposito do projeto, arquitetura de alto nivel, fases de entrega, estrutura de diretorios
e diretrizes de governanca e conformidade oficial.
-->

# Minecraft Bedrock Dedicated Server (BDS) para Proxmox LXC

Infraestrutura de nível de produção para implantação, operação e governança do **Minecraft Bedrock Dedicated Server (BDS)** em ambiente local-first virtualizado via Proxmox VE (container LXC Ubuntu LTS).

[![Versão do BDS](https://img.shields.io/badge/BDS%20Version-1.26.52.3-green.svg)](https://www.minecraft.net/en-us/download/server/bedrock)
[![Licença](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![CI Lint](https://img.shields.io/badge/CI-Shellcheck%20%26%20JSON%20Validation-orange.svg)](.github/workflows/lint.yml)

---

## 1. Princípios de Engenharia

- **Conformidade com Fontes Oficiais**: Todas as decisões técnicas e propriedades de configuração referenciam diretamente os manuais da Mojang (`bedrock_server_how_to.html`, `server.properties`, v1.26.52.3) e do portal Microsoft Creator.
- **Local-First & Privativo**: Nenhuma dependência de nuvens externas ou intermediários para o tráfego de jogo na rede local.
- **Determinismo & Imutabilidade**: Desacoplamento estrito entre binários versionados por hash (`/opt/bds/versions/`) e estado persistente (`/opt/bds/data/`).
- **Segurança Reforçada**: Execução sob usuário restrito sem privilégios (`bedrock`), firewall restritivo, allowlist obrigatória e validação Xbox Live.
- **Confiabilidade Operacional**: Backup consistente a quente com truncamento de bytes LevelDB e rollback instantâneo em caso de falha em atualizações.

---

## 2. Estrutura do Repositório

```
s_Bedrock_Server/
├── .github/
│   ├── workflows/
│   │   └── lint.yml                 # CI com shellcheck e validacao de JSON/templates
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md            # Template estruturado para reporte de bugs
│   │   └── feature_request.md       # Template estruturado para melhorias
│   └── pull_request_template.md     # Template de revisao e checklist de PR
├── docs/
│   ├── adr/                         # Registros de Decisoes Arquiteturais (ADRs)
│   │   ├── ADR-001-runtime-execution-model.md
│   │   ├── ADR-002-network-transport-and-ports.md
│   │   ├── ADR-003-data-layout-and-versioning.md
│   │   ├── ADR-004-hot-backup-strategy.md
│   │   └── ADR-005-console-ipc-and-automation.md
│   ├── architecture/                # Especificacoes tecnicas detalhadas
│   │   ├── ARCHITECTURE.md          # Arquitetura geral e diagrama Mermaid
│   │   ├── NETWORKING.md            # Plano de rede e guia de clientes (Android/PC/Xbox)
│   │   ├── BACKUP_AND_RESTORE.md    # Backup a quente oficial e disaster recovery
│   │   ├── UPDATE_AND_ROLLBACK.md   # Pipeline de atualizacao com rollback atomico
│   │   └── ADDONS_AND_EXTENSIBILITY.md # Guia de pacotes e scripts sem alterar vanilla
│   ├── acceptance/
│   │   └── CHECKLIST.md             # Matriz e checklist formal de aceitacao
│   ├── runbook/
│   │   └── RUNBOOK.md               # Guia passo a passo de operacao diaria
│   └── research/
│       └── OFFICIAL_RESEARCH_PHASE_0.md # Auditoria de fontes oficiais e checksums
├── scripts/
│   ├── bds-install.sh               # Instalacao idempotente e provisionamento
│   ├── bds-config.sh                # Geracao deterministica de configs a partir dos templates
│   ├── bds-cmd.sh                   # Envio de comandos ao console via Tmux
│   ├── bds-console.sh               # Terminal interativo de operacao
│   ├── bds-backup.sh                # Backup a quente oficial (save hold/query/resume + truncate)
│   ├── bds-restore.sh               # Recuperacao de desastres com verificacao de hash
│   ├── bds-update.sh                # Atualizacao controlada com consulta de API e rollback
│   ├── bds-rollback.sh              # Reversao atomica de versao
│   └── bds-healthcheck.sh           # Smoke test e verificacao de integridade
├── systemd/
│   ├── minecraft-bedrock.service    # Unit de execucao como servico sob usuario bedrock
│   ├── minecraft-bedrock-backup.service # Unit oneshot de backup
│   └── minecraft-bedrock-backup.timer   # Temporizador de backup diario programado
├── firewall/
│   └── setup-firewall.sh            # Hardening de firewall UFW (19132/udp)
├── templates/
│   ├── server.properties.template   # Template comentado com propriedades oficiais
│   ├── allowlist.json.template      # Modelo de controle de acesso
│   ├── permissions.json.template    # Modelo de atribuicao de operadores/membros
│   └── packetlimitconfig.json.template # Modelo de limitacao de pacotes
├── tests/
│   ├── test_config_generator.py     # Testes de geracao e validacao de configs
│   ├── test_backup_logic.py         # Testes de parsing e truncamento de bytes
│   ├── test_data_layout.py          # Testes de estrutura FHS e isolamento de dados
│   └── run_all_tests.py             # Executor da suite de testes
├── CHANGELOG.md                     # Historico de mudancas (Keep a Changelog)
├── CODEOWNERS                       # Responsaveis pelo codigo e revisoes
└── README.md                        # Este documento
```

---

## 3. Matriz de Fases do Projeto

| Fase | Escopo | Status Atual |
| :--- | :--- | :--- |
| **Fase 0 – Pesquisa** | Auditoria das fontes oficiais da Mojang/Microsoft, verificação de hash SHA-256, requisitos de SO e limitações de clientes. | **Concluída** |
| **Fase 1 – Arquitetura & Docs** | Elaboração dos ADRs, plano de rede (Android/PC/Xbox), plano de backup a quente oficial, pipeline de atualização com rollback e templates. | **Concluída e Aprovada** |
| **Fase 2 – Implementação** | Desenvolvimento dos scripts modulares (`bds-install`, `bds-backup`, `bds-update`, `bds-rollback`, `bds-cmd`, `bds-console`, `bds-healthcheck`, `bds-restore`) e units systemd. | **Concluída** |
| **Fase 3 – Testes** | Validação automatizada de smoke test, testes unitários de truncamento LevelDB, parsing e integridade de templates. | **Concluída (100% aprovada)** |
| **Fase 4 – Runbook & Aceitação** | Guia de operação diária (Runbook) e checklist final de aceitação técnica. | **Concluída** |

---

## 4. Referências Oficiais
- **Página de Download BDS**: [https://www.minecraft.net/en-us/download/server/bedrock](https://www.minecraft.net/en-us/download/server/bedrock)
- **Endpoint da API de Links**: [https://net-secondary.web.minecraft-services.net/api/v1.0/download/links](https://net-secondary.web.minecraft-services.net/api/v1.0/download/links)
- **Documentação de Criadores Microsoft**: [https://learn.microsoft.com/minecraft/creator](https://learn.microsoft.com/minecraft/creator)
- **Versão Auditada**: `1.26.52.3` (SHA-256: `f6348d84fa714d04ca194f207e89453ca6bba0a1359396475271a52a150471c6`)
