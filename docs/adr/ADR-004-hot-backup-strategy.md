<!--
Responsabilidade: Decisão de arquitetura sobre a estratégia de backup a quente e recuperação do BDS.
Especifica a implementação estrita do fluxo oficial 'save hold' / 'save query' / 'save resume',
com truncamento exato de bytes dos arquivos de banco de dados e rotação temporal.
-->
---
document_id: adr-004-hot-backup-strategy
title: Estratégia de Backup a Quente Oficial e Recuperação de Desastres
document_type: adr
status: proposed
version: 1.0.0
language: pt-BR
owners: [architecture-maintainers]
last_updated: "2026-09-28"
review_cycle_days: 365
license: MIT
---

# ADR-004: Estratégia de Backup a Quente Oficial e Recuperação de Desastres

## Estado

`proposed` — 2026-09-28 — Decisores: Equipe de Engenharia / Mantenedor do Projeto.

## Contexto

O Minecraft Bedrock Dedicated Server utiliza o banco de dados LevelDB para persistir os blocos e entidades do mundo. O LevelDB mantém tabelas em memória (`memtables`) e descarrega periodicamente em arquivos de dados (`.ldb`) e logs de transação (`.log`), mantendo arquivos abertos continuamente.
Realizar um backup copiando os arquivos diretamente enquanto o processo está ativo causa corrupção garantida do mundo devido a escritas parciais e estados inconsistentes entre o manifesto e as tabelas LevelDB.

A documentação oficial (`bedrock_server_how_to.html`, v1.26.52.3) define um protocolo de snapshot consistente a quente através de 3 comandos no console do servidor:
1. `save hold`: Congela o estado para backup assincronamente.
2. `save query`: Interrogado em loop até retornar confirmação e a lista de pares `arquivo:tamanho_em_bytes`.
3. `save resume`: Libera o servidor para descartar logs arquivados e retomar a manutenção normal.

Uma exigência técnica crítica documentada é:
> *"The server will not pause while this is happening, so some files can be modified while the backup is taking place. As long as you only copy the files in the given file list and truncate the copied files to the specified lengths, then the backup should be valid."*

## Opções consideradas

### Opção 1: Backup a Frio com Parada do Servidor (`systemctl stop -> tar -> systemctl start`)
- **Funcionamento**: O serviço é finalizado para garantir arquivos fechados no disco, a pasta `worlds/` é compactada e o serviço é reiniciado.
- **Desvantagens**: Desconecta todos os jogadores ativos e interrompe a disponibilidade. Inaceitável para automação periódica (ex.: a cada poucas horas).

### Opção 2: Pipeline de Backup a Quente Conforme Protocolo Oficial da Mojang (Recomendada)
- **Funcionamento**:
  1. O script de backup envia `save hold` via interface IPC do console do servidor.
  2. Executa `save query` periodicamente até obter a mensagem:
     `Data saved. Files are now ready to be copied.`
     seguida da lista de arquivos e comprimentos (ex.: `Bedrock level/db/000005.ldb:2097152, Bedrock level/level.dat:2348, ...`).
  3. Para cada arquivo retornado na lista:
     - Copia para um diretório temporário isolado de staging.
     - Trunca o arquivo no staging exatamente para o número de bytes retornado pelo `save query` (usando `truncate -s <bytes>` ou leitura binária fatiada), descartando dados adicionais escritos após o snapshot.
  4. Envia imediatamente `save resume` ao console do servidor para liberar retenção de logs da engine.
  5. Compacta os arquivos fatiados em arquivo `.tar.gz` datado (ex.: `bds-world-YYYYMMDD_HHMMSS.tar.gz`) com checksum SHA-256.
  6. Aplica rotação automática (ex.: manter últimos 14 backups diários).
- **Vantagens**:
  - Zero interrupção de jogo para os jogadores conectados.
  - Consistência transacional garantida pelo próprio mecanismo oficial do BDS.
  - Conformidade estrita com o manual oficial da versão 1.26.52.3.

## Decisão

Adotar a **Opção 2: Pipeline de Backup a Quente Conforme Protocolo Oficial da Mojang**.

O processo será implementado em um script modular e determinístico (`bds-backup.sh`), com temporizador systemd (`minecraft-bedrock-backup.timer`) ou cron agendado.

### Requisitos Técnicos Obrigatórios do Pipeline:
1. **Timeout de Segurança**: Se o comando `save query` não retornar sucesso em até 60 segundos após `save hold`, o script deve emitir `save resume`, registrar o erro no log e abortar para não reter arquivos indefinidamente no BDS.
2. **Garantia de `save resume`**: Uso de trap shell (`trap 'send_command "save resume"' EXIT INT TERM`) para assegurar que, em caso de erro fatal ou cancelamento, o servidor nunca permaneça congelado no estado de hold.
3. **Truncamento de Bytes**: Cada arquivo deve ser copiado e truncado para o comprimento exato em bytes reportado pela saída de `save query`.
4. **Armazenamento de Metadados e Checksum**: Cada backup comprimido é acompanhado de seu arquivo `.sha256`.

## Consequências

- **Efeitos Positivos**:
  - Backups atômicos e íntegros sem desconectar jogadores.
  - Rotação previsível evitando esgotamento de disco no container LXC.
- **Efeitos Negativos**:
  - Exige um canal de comunicação IPC confiável para enviar comandos ao console do processo `bedrock_server` e ler a resposta (ver ADR-005).

## Plano de validação e reversão

- **Sinais de Sucesso**:
  - Execução bem-sucedida do script gerando arquivo de backup no staging e arquivamento final.
  - Teste de restauração em ambiente isolado: descompactar o backup em uma pasta temporária de teste e verificar se o BDS carrega o mundo sem warnings de corrupção de LevelDB.
- **Procedimento de Restauração (Disaster Recovery)**:
  1. `systemctl stop minecraft-bedrock`
  2. Mover a pasta `worlds/` danificada para `worlds.corrupted.<timestamp>`
  3. Descompactar o arquivo `.tar.gz` de backup verificado
  4. Ajustar permissões para `bedrock:bedrock`
  5. `systemctl start minecraft-bedrock`

## Referências

- Documentação Oficial BDS: `bedrock_server_how_to.html` (v1.26.52.3) - Seção *Backups* e *Commands -> save*.
