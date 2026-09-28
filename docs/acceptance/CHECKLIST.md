<!--
Responsabilidade: Matriz de rastreabilidade e checklist formal de aceitacao do projeto.
Valida o atendimento rigoroso de cada requisito funcional, operacional e de governanca.
-->

# Checklist Formal de Aceitação Técnica: Bedrock Dedicated Server

Este documento consolida a validação de todos os requisitos funcionais, operacionais e de governança estipulados no projeto.

---

## 1. Matriz de Requisitos Funcionais e Operacionais

| ID | Requisito | Status | Componente de Implementação | Critério de Aceitação e Evidência |
| :---: | :--- | :---: | :--- | :--- |
| **RF-01** | Instalação automatizada e reproduzível | **Atendido** | [`scripts/bds-install.sh`](file:///C:/dev/s_Bedrock_Server/scripts/bds-install.sh) | Script idempotente com download da v1.26.52.3, verificação de hash SHA-256 e particionamento FHS em `/opt/bds`. |
| **RF-02** | Execução como serviço, no-root, reinício e logs | **Atendido** | [`systemd/minecraft-bedrock.service`](file:///C:/dev/s_Bedrock_Server/systemd/minecraft-bedrock.service) | Executa sob `User=bedrock`, `Restart=on-failure`, hardening (`ProtectSystem=full`) e logs centralizados no `journald`. |
| **RF-03** | Configuração completa e comentada com ajuste de hardware | **Atendido** | [`templates/server.properties.template`](file:///C:/dev/s_Bedrock_Server/templates/server.properties.template) e [`scripts/bds-config.sh`](file:///C:/dev/s_Bedrock_Server/scripts/bds-config.sh) | 100% das propriedades da v1.26.52.3 documentadas; view-distance (20), tick-distance (4) e threads (4) ajustados para host com ~12 GB RAM compartilhados. |
| **RF-04** | Segurança: allowlist, Xbox Live, firewall local-first | **Atendido** | [`firewall/setup-firewall.sh`](file:///C:/dev/s_Bedrock_Server/firewall/setup-firewall.sh) e [`docs/architecture/NETWORKING.md`](file:///C:/dev/s_Bedrock_Server/docs/architecture/NETWORKING.md) | `allow-list=true`, `online-mode=true`, UFW com default deny e liberação estrita da porta 19132/udp sem exposição externa. |
| **RF-05** | Backup a quente oficial (`save hold/query/resume`) e restauração | **Atendido** | [`scripts/bds-backup.sh`](file:///C:/dev/s_Bedrock_Server/scripts/bds-backup.sh) e [`scripts/bds-restore.sh`](file:///C:/dev/s_Bedrock_Server/scripts/bds-restore.sh) | Protocolo oficial fiel com truncamento exato em bytes no LevelDB, empacotamento `.tar.gz`, `.sha256` e rotação temporal de 14 dias. |
| **RF-06** | Atualização controlada com rollback atômico | **Atendido** | [`scripts/bds-update.sh`](file:///C:/dev/s_Bedrock_Server/scripts/bds-update.sh) e [`scripts/bds-rollback.sh`](file:///C:/dev/s_Bedrock_Server/scripts/bds-rollback.sh) | Desacoplamento via symlinks conforme ADR-003, consulta automática de API, backup prévio obrigatório e reversão em segundos sob falha. |
| **RF-07** | Extensibilidade para add-ons e scripts | **Atendido** | [`docs/architecture/ADDONS_AND_EXTENSIBILITY.md`](file:///C:/dev/s_Bedrock_Server/docs/architecture/ADDONS_AND_EXTENSIBILITY.md) | Isolamento em `/opt/bds/data/custom_packs/`, suporte a `system_behavior_packs` e governança de script watchdog em `server.properties`. |
| **RF-08** | Healthcheck e smoke test automatizado | **Atendido** | [`scripts/bds-healthcheck.sh`](file:///C:/dev/s_Bedrock_Server/scripts/bds-healthcheck.sh) | Teste automatizado de 5 etapas: status systemd, sessão tmux, processo/UID `bedrock`, socket UDP 19132 ativo e logs limpos. |

---

## 2. Governança e Qualidade de Engenharia

| Item de Governança | Arquivo de Referência | Status | Detalhes |
| :--- | :--- | :---: | :--- |
| **Documentação de Arquitetura (ADRs)** | [`docs/adr/`](file:///C:/dev/s_Bedrock_Server/docs/adr/) | **Aprovado** | 5 ADRs abordando modelo de execução, transporte de rede, layout de dados, backup a quente e IPC. |
| **Plano de Rede e Clientes** | [`docs/architecture/NETWORKING.md`](file:///C:/dev/s_Bedrock_Server/docs/architecture/NETWORKING.md) | **Aprovado** | Conectividade detalhada para Android, PC Windows e Xbox (com limitações oficiais e alternativas da comunidade). |
| **Runbook de Operação** | [`docs/runbook/RUNBOOK.md`](file:///C:/dev/s_Bedrock_Server/docs/runbook/RUNBOOK.md) | **Aprovado** | Manual de operação para dimensionamento no Proxmox, comandos diários, backup, restore e diagnóstico. |
| **Integração Contínua (CI)** | [`.github/workflows/lint.yml`](file:///C:/dev/s_Bedrock_Server/.github/workflows/lint.yml) | **Aprovado** | Workflow com `shellcheck`, validação de arquivos JSON via `jq` e consistência de templates. |
| **Templates de Contribuição** | [`.github/pull_request_template.md`](file:///C:/dev/s_Bedrock_Server/.github/pull_request_template.md) e [`.github/ISSUE_TEMPLATE/`](file:///C:/dev/s_Bedrock_Server/.github/ISSUE_TEMPLATE/) | **Aprovado** | Templates estruturados de PR, Bug Report e Feature Request. |
| **Propriedade e Versionamento** | [`CODEOWNERS`](file:///C:/dev/s_Bedrock_Server/CODEOWNERS) e [`CHANGELOG.md`](file:///C:/dev/s_Bedrock_Server/CHANGELOG.md) | **Aprovado** | Atribuição de proprietários e histórico de mudanças no padrão Keep a Changelog. |
| **Suíte de Testes Automatizados** | [`tests/`](file:///C:/dev/s_Bedrock_Server/tests/) | **Aprovado** | Testes de parsing do `save query`, truncamento exato de bytes, substituição de templates e integridade SHA-256. |

---

## 3. Conclusão da Avaliação

O projeto cumpre **100% dos requisitos estipulados**, seguindo com rigor as fontes oficiais da Mojang/Microsoft e as melhores práticas de engenharia de software para operação no Proxmox LXC.
