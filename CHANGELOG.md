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
- **Fase 2 (Implementação Modular)**:
  - `scripts/bds-install.sh`: Script idempotente de provisionamento completo, download oficial, verificação de hash SHA-256 e particionamento FHS em `/opt/bds`.
  - `scripts/bds-config.sh`: Gerador determinístico de `server.properties` e validação de tipos de dados conforme v1.26.52.3.
  - `scripts/bds-cmd.sh` e `scripts/bds-console.sh`: Ferramentas IPC para injeção não interativa de comandos e conexão interativa de operador via Tmux.
  - `scripts/bds-backup.sh`: Pipeline completo do backup a quente com truncamento de bytes LevelDB, compressão `.tar.gz`, `.sha256` e rotação temporal.
  - `scripts/bds-restore.sh`: Procedimento de recuperação de desastres com validação de checksum e isolamento do mundo danificado.
  - `scripts/bds-update.sh` e `scripts/bds-rollback.sh`: Pipeline de atualização controlada via API da Mojang com rollback automático e manual.
  - `scripts/bds-healthcheck.sh`: Smoke test automatizado de 5 etapas para validação de integridade operacional.
  - `systemd/`: Units de serviço (`minecraft-bedrock.service`), job oneshot (`minecraft-bedrock-backup.service`) e temporizador diário (`minecraft-bedrock-backup.timer`).
  - `firewall/setup-firewall.sh`: Configuração e reforço de firewall UFW liberando porta 19132/udp.
- **Fase 3 (Testes e Validação)**:
  - Suíte de testes automatizados (`tests/test_config_generator.py`, `tests/test_backup_logic.py`, `tests/test_data_layout.py`, `tests/run_all_tests.py`).
  - Validação de 100% dos scripts shell via `bash -n` e validação de templates JSON.
- **Fase 4 (Runbook e Aceitação)**:
  - `docs/runbook/RUNBOOK.md`: Guia completo de operação diária, dimensionamento em Proxmox LXC, allowlist, backups, restauração e diagnósticos.
  - `docs/acceptance/CHECKLIST.md`: Matriz e checklist formal de aceitação técnica comprovando o atendimento de 100% dos requisitos.
- **Suporte Nativo ao Windows (Dual-Platform)**:
  - `docs/adr/ADR-006-windows-native-execution.md`: Decisão arquitetural para execução nativa no Windows 10/11 x64 com NTFS Junctions.
  - `windows/bds-install.ps1`: Instalador automatizado para Windows com verificação de hash SHA-256 (`2c9b98d0...`).
  - `windows/bds-config.ps1`: Gerador de configurações para Windows a partir dos templates oficiais.
  - `windows/bds-start.ps1` e `windows/iniciar-servidor.bat`: Inicializadores do servidor com console interativo e duplo clique.
  - `windows/enable-loopback.ps1` e `windows/habilitar-conexao-local.bat`: Isenção de loopback via `CheckNetIsolation` para conexão no mesmo PC.
  - `windows/setup-firewall.ps1`: Configuração automatizada de regras no Firewall do Windows Defender (19132/udp).
  - `windows/bds-backup.ps1` e `windows/bds-restore.ps1`: Procedimentos de backup comprimido (.zip) e restauração no Windows.
  - `windows/bds-healthcheck.ps1`: Smoke test de verificação de processo, socket UDP e loopback no Windows.
- **Expansão de Add-ons e Gerência Inteligente (Fase 5)**:
  - `windows/build_lucky_addon.py`: Construtor automatizado do Behavior Pack e Resource Pack do Lucky Block com scripts `@minecraft/server`, catálogo rico de eventos da sorte, texturas 16x16 douradas, ícones e receitas de bancada.
  - `windows/instalar_lucky_oneblock.py`: Instalador e conversor do mapa oficial do CurseForge (872580 - *el_this_boy*) via Chunker CLI, metadados LevelDB, e ativação com 1 clique.
  - `windows/server_manager.py`: Módulo inteligente de gerenciamento de backend fornecendo telemetria em tempo real (RAM, CPU, Uptime, Socket UDP), parada graciosa com flush de LevelDB, reinício seguro, descoberta dinâmica de mundos, snapshots em ZIP, central CurseForge e diagnóstico profundo com auto-reparo.
  - `windows/cli.py`: Utilitário CLI unificado refatorado com interface moderna, menu rico em telemetria, atalhos de terminal (`--lucky-oneblock`, `--healthcheck`, `--backup-world`, `--cmd`, `--stop`, `--restart`) e 100% de compatibilidade retroativa.
  - `tests/test_lucky_oneblock.py` e `tests/test_server_manager.py`: Suíte expandida para 49 testes unitários e de integração com 100% de aprovação.
- **Port de The Ruby Ore e Inteligência de Mods & Mundos (Fase 6)**:
  - `windows/instalar_ruby_ore.py`: Instalador e port nativo para Bedrock Dedicated Server do mod oficial do CurseForge *The Ruby Ore* (`romhenris-ruby-ore` por *romhenri*), incluindo minérios de rubi (Y: -25 a -49), bloco de rubi, armas e ferramentas superiores a Netherite (durabilidade 2031), martelo de escavação 3x3 (`ruby_hammer`), machado de combate (`ruby_combat_axe`), receitas completas e texturas 16x16 pixel-art oficiais.
  - `windows/gerenciar_mods.py`: Adição do mod `rubyore` ao catálogo central, novas funções `get_all_worlds_mods_matrix()`, `get_active_mods_names()` e `print_worlds_mods_matrix()` fornecendo matriz detalhada e comparativa de mundos e mods.
  - `windows/server_manager.py`: Reconhecimento e roteamento automático da URL oficial do CurseForge (`https://www.curseforge.com/minecraft/mc-mods/romhenris-ruby-ore`), enriquecimento do `get_server_status()` e `list_worlds_detailed()` com lista e contagem de mods ativos por mundo.
  - `windows/cli.py`: Painel centralizado do menu interativo e comandos (`--status`, `--matrix`, `--rubyore`) reformulados para destacar visualmente em tempo real qual mundo está ativo, quais mods estão ativos em cada mundo e atalhos rápidos de instalação e ativação.
  - `tests/test_ruby_ore.py`: Testes unitários cobrindo estrutura de pacotes BP/RP, resolução de URLs do CurseForge, validação de itens, blocos e matriz de telemetria, expandindo a suíte para 57 testes com 100% de aprovação.
