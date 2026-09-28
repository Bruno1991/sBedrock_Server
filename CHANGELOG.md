<!--
Responsabilidade: Registro cronologico de todas as alteracoes do projeto s_Bedrock_Server.
Segue rigorosamente o padrao Keep a Changelog (https://keepachangelog.com) e Semantic Versioning.
-->

# Changelog

Todas as alterações notáveis neste projeto serão documentadas neste arquivo.

O formato baseia-se em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [Unreleased]

### Added
- **Fase 0 (Pesquisa Oficial)**:
  - Auditoria completa do pacote Bedrock Dedicated Server v1.26.52.3 e documentação `bedrock_server_how_to.html`.
  - Mapeamento do endpoint oficial da API de download da Microsoft (`net-secondary.web.minecraft-services.net`).
  - Verificação e fixação do hash criptográfico SHA-256 (`f6348d84fa714d04ca194f207e89453ca6bba0a1359396475271a52a150471c6`).
- **Fase 1 (Arquitetura e Governança)**:
  - `ADR-001-runtime-execution-model.md`: Decisão de serviço nativo systemd sob usuário `bedrock` no LXC vs Docker.
  - `ADR-002-network-transport-and-ports.md`: Comparativo técnico entre RakNet e NetherNet, mapeamento de portas e regras de firewall.
  - `ADR-003-data-layout-and-versioning.md`: Estrutura de diretórios desacoplando `/opt/bds/versions/` de `/opt/bds/data/`.
  - `ADR-004-hot-backup-strategy.md`: Protocolo oficial de backup a quente (`save hold` / `save query` / `save resume`) com truncamento em bytes.
  - `ADR-005-console-ipc-and-automation.md`: Interface IPC via sessão Tmux dedicada para automação não interativa e console de operador.
  - Documentos de arquitetura detalhada: `ARCHITECTURE.md`, `NETWORKING.md`, `BACKUP_AND_RESTORE.md`, `UPDATE_AND_ROLLBACK.md` e `ADDONS_AND_EXTENSIBILITY.md`.
  - Templates de configuração oficiais: `server.properties.template`, `allowlist.json.template`, `permissions.json.template` e `packetlimitconfig.json.template`.
  - Governança de repositório: README, CODEOWNERS, `.gitignore`, templates de PR e Issue, e workflow GitHub Actions com `shellcheck` e validação JSON.
