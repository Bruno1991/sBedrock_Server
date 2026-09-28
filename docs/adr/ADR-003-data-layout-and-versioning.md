<!--
Responsabilidade: Decisão de arquitetura sobre a estrutura de diretórios, desacoplamento
entre binários imutáveis por versão e dados persistentes mutáveis, viabilizando rollback atômico.
-->
---
document_id: adr-003-data-layout-and-versioning
title: Desacoplamento de Binários Imutáveis e Dados Persistentes
document_type: adr
status: proposed
version: 1.0.0
language: pt-BR
owners: [architecture-maintainers]
last_updated: "2026-09-28"
review_cycle_days: 365
license: MIT
---

# ADR-003: Desacoplamento de Binários Imutáveis e Dados Persistentes

## Estado

`proposed` — 2026-09-28 — Decisores: Equipe de Engenharia / Mantenedor do Projeto.

## Contexto

A distribuição oficial em arquivo compactado do BDS mescla na raiz arquivos de naturezas distintas:
1. **Binários e Ativos Imutáveis**: Executável `bedrock_server`, bibliotecas, pastas `definitions/`, `resource_packs/vanilla_*` e `behavior_packs/vanilla_*`.
2. **Configurações e Controle de Acesso**: `server.properties`, `allowlist.json`, `permissions.json`, `packetlimitconfig.json`.
3. **Estado Persistente do Jogo**: Pastas geradas dinamicamente como `worlds/` (bancos LevelDB), `keys/` (identidade do servidor) e logs de conteúdo.

Se uma nova versão do BDS for descompactada diretamente sobre a pasta do servidor em execução, as seguintes falhas graves ocorrem:
- Sobrescrita de arquivos de configuração personalizados pelos padrões da Mojang (`server.properties` e `allowlist.json` vazios).
- Acúmulo de arquivos órfãos de versões antigas.
- Impossibilidade de reversão rápida (rollback) para a versão anterior em caso de quebra ou incompatibilidade.

## Opções consideradas

### Opção 1: Pasta Única Plana com Sobrescrita Manual
- **Funcionamento**: Todos os arquivos ficam em `/opt/bedrock`. Atualizações exigem backup manual prévio, descompactação com exclusão de arquivos protegidos (`server.properties`) e mescla em loco.
- **Desvantagens**: Risco humano crítico de perda de mundos e sobrescrita de regras de segurança; rollback trabalhoso e propenso a erros.

### Opção 2: Separação em Camadas: Versões Imutáveis, Dados Persistentes e Runtime Simbólico (Recomendada)
- **Funcionamento**:
  - `/opt/bds/versions/<versao>/`: Diretório somente leitura contendo a extração limpa e verificada por hash de cada versão do BDS (ex.: `/opt/bds/versions/1.26.52.3/`).
  - `/opt/bds/data/`: Diretório persistente contendo todo o estado mutável do operador (`worlds/`, `config/`, `keys/`, `backups/`, `allowlist.json`, `permissions.json`, etc.).
  - `/opt/bds/runtime/`: Diretório de trabalho (`WorkingDirectory` do systemd). Contém links simbólicos apontando para os binários da versão ativa e links para os dados persistentes em `/opt/bds/data/`.
- **Vantagens**:
  - **Atualização Atômica**: Instalar nova versão consiste em extrair em `/opt/bds/versions/<nova_versao>/` e reatribuir os links simbólicos de runtime.
  - **Rollback Instantâneo**: Em caso de falha, reverter os symlinks para a versão anterior leva menos de 2 segundos.
  - **Isolamento de Estado**: Os mundos e configurações nunca são tocados pelo processo de download/extração de binários.

## Decisão

Adotar a **Opção 2: Separação em Camadas: Versões Imutáveis, Dados Persistentes e Runtime Simbólico**.

### Estrutura de Diretórios Padronizada:
```
/opt/bds/
├── versions/                      # Binários imutáveis versionados
│   ├── 1.26.52.3/                 # Versão estável auditada
│   │   ├── bedrock_server
│   │   ├── definitions/
│   │   ├── resource_packs/
│   │   └── behavior_packs/
│   └── <versao_anterior>/         # Mantida para rollback imediato
├── data/                          # Estado persistente do servidor
│   ├── config/
│   │   ├── server.properties      # Gerado a partir do template
│   │   ├── allowlist.json         # Gerenciado pelo operador/servidor
│   │   ├── permissions.json       # Papéis de permissão
│   │   └── packetlimitconfig.json # Limites de pacotes
│   ├── worlds/                    # Bancos LevelDB dos mundos
│   ├── keys/                      # server_identity_key.pem
│   ├── custom_packs/              # Add-ons e scripts do usuário
│   └── backups/                   # Snapshots a quente comprimidos
└── runtime/                       # Diretório ativo de execução (CWD)
    ├── bedrock_server -> /opt/bds/versions/1.26.52.3/bedrock_server
    ├── definitions -> /opt/bds/versions/1.26.52.3/definitions
    ├── resource_packs -> /opt/bds/versions/1.26.52.3/resource_packs
    ├── behavior_packs -> /opt/bds/versions/1.26.52.3/behavior_packs
    ├── server.properties -> /opt/bds/data/config/server.properties
    ├── allowlist.json -> /opt/bds/data/config/allowlist.json
    ├── permissions.json -> /opt/bds/data/config/permissions.json
    ├── packetlimitconfig.json -> /opt/bds/data/config/packetlimitconfig.json
    ├── worlds -> /opt/bds/data/worlds
    └── keys -> /opt/bds/data/keys
```

## Consequências

- **Efeitos Positivos**:
  - Separação clara de responsabilidades no sistema de arquivos.
  - O processo de atualização é estritamente não destrutivo.
  - Facilita backups (basta arquivar `/opt/bds/data/`).
- **Efeitos Negativos / Modos de Falha**:
  - Exige que o script de setup e atualização garanta a consistência de links simbólicos e permissões de acesso (`chown -R bedrock:bedrock`).

## Plano de validação e reversão

- **Sinais de Sucesso**:
  - O executável sobe no runtime e carrega mundos e propriedades sem erro de link quebrado.
  - Teste de troca de versão aponta os links para outra pasta e restaura em seguida com sucesso.
- **Procedimento de Reversão**:
  - Script dedicado `bds-rollback` reatribui os symlinks para a versão n-1 e reinicia o serviço.

## Referências

- Documentação Oficial BDS: `bedrock_server_how_to.html` (v1.26.52.3) - Seções *Folders* e *Server Identity*.
- Filesystem Hierarchy Standard (FHS): Padrão `/opt` para pacotes de software adicionais.
