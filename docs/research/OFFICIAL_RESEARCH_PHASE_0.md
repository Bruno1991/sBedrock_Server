<!--
Responsabilidade: Registro consolidado de pesquisa oficial da Fase 0 (Minecraft Bedrock Dedicated Server - BDS).
Contém links oficiais, versão auditada, requisitos de sistema operacional, protocolos de rede,
comandos do servidor, limitações de plataformas e parâmetros de configuração extraídos do pacote oficial.
-->

# Fase 0: Pesquisa e Auditoria de Fontes Oficiais do BDS

## 1. Identificação e Metadados do Pacote Oficial
- **Software**: Minecraft Bedrock Dedicated Server (BDS) para Linux.
- **Versão Estável Atual Auditada**: `1.26.52.3`
- **Versão Preview Auditada**: `1.26.60.28`
- **URL de Download Oficial**: [https://www.minecraft.net/bedrockdedicatedserver/bin-linux/bedrock-server-1.26.52.3.zip](https://www.minecraft.net/bedrockdedicatedserver/bin-linux/bedrock-server-1.26.52.3.zip)
- **Endpoint de Resolução de Versões Oficiais**: [https://net-secondary.web.minecraft-services.net/api/v1.0/download/links](https://net-secondary.web.minecraft-services.net/api/v1.0/download/links)
- **Portal Oficial**: [https://www.minecraft.net/en-us/download/server/bedrock](https://www.minecraft.net/en-us/download/server/bedrock)
- **Portal Microsoft Creator**: [https://learn.microsoft.com/minecraft/creator](https://learn.microsoft.com/minecraft/creator)
- **Hash SHA-256 Verificado**:
  `f6348d84fa714d04ca194f207e89453ca6bba0a1359396475271a52a150471c6`
- **Tamanho do Arquivo Compactado**: 94.927.522 bytes (~90,5 MB)
- **Data do Pacote (Last-Modified)**: 25 de setembro de 2026

## 2. Requisitos de Sistema e Plataforma Oficial
*Fonte: `bedrock_server_how_to.html` (incluso no pacote oficial v1.26.52.3)*

- **Hardware Mínimo Recomendado**: Processador Intel ou AMD de 64 bits com no mínimo 2 núcleos e 1 GB de RAM.
- **Sistemas Operacionais Suportados**:
  - **Linux**: Ubuntu 18 ou posterior (recomenda-se Ubuntu 22.04 LTS ou 24.04 LTS). O documento oficial especifica textualmente: *"The Linux version of the Bedrock Server requires Ubuntu 18 or later. Other distributions are not supported."*
  - **Windows**: Windows 10 versão 1703+ ou Windows Server 2016+.
- **Comando Oficial de Execução**:
  ```bash
  LD_LIBRARY_PATH=. ./bedrock_server
  ```
- **Dependências de Bibliotecas no Linux**: `libc6`, `libcurl4`, `libssl3` (OpenSSL), além de utilitários de suporte (`unzip`, `curl`, `jq`).

## 3. Topologia de Rede e Portas
*Fonte: `server.properties` e `bedrock_server_how_to.html` da versão 1.26.52.3*

Na versão 1.26.52.3, a Mojang introduziu oficialmente dois modos de transporte de rede (`transport`):

### 3.1. Modo NetherNet (`transport=nethernet`) — Padrão Atual do BDS
- **Protocolo Base**: Baseado em WebRTC.
- **Sinalização (Handshake)**: O servidor abre um socket TCP dual-stack (IPv4 e IPv6) na porta configurada em `server-port` (padrão: `19132/TCP`), aceitando handshake HTTP.
- **Tráfego de Jogo (Gameplay)**: O tráfego de dados do jogo ocorre via UDP negociado diretamente entre o cliente e o servidor. Por padrão, aloca portas UDP efêmeras do sistema operacional, a menos que seja fixado via propriedade `server-udp-ports` (ex.: `server-udp-ports=19132-19140` ou mapeamentos NAT específicos).
- **Atenção**: No modo NetherNet, a propriedade `server-portv6` é ignorada, pois o socket TCP em `server-port` é dual-stack.

### 3.2. Modo RakNet (`transport=raknet`) — Transporte Tradicional Bedrock
- **Protocolo Base**: UDP puro sobre a biblioteca RakNet.
- **Portas**:
  - IPv4: `server-port=19132` (UDP)
  - IPv6: `server-portv6=19133` (UDP)
- **Descoberta em Rede Local (LAN)**: Quando `enable-lan-visibility=true`, o servidor responde a broadcasts UDP na porta 19132.

## 4. Análise de Conectividade por Plataforma de Cliente

### 4.1. Android
- **Mecanismo**: Aplicativo oficial Minecraft Bedrock (Google Play Store).
- **Conexão Direta**: Nativa e oficial. A aba *Servidores* (*Servers*) permite adicionar servidores externos clicando em *Adicionar Servidor* (*Add Server*), informando o nome, IP local (ex.: `192.168.x.x`) e a porta (padrão: `19132`).
- **Descoberta LAN**: Com `enable-lan-visibility=true`, caso o dispositivo esteja na mesma sub-rede/VLAN, o servidor é exibido automaticamente na aba *Amigos* (*Friends*) sob a seção *Jogos em LAN*.

### 4.2. Windows (PC)
- **Mecanismo**: Minecraft Bedrock Edition via Microsoft Store.
- **Conexão Direta**: Nativa e oficial através da aba *Servidores* -> *Adicionar Servidor* com IP e porta.
- **Descoberta LAN**: Exibição automática na aba *Amigos* quando na mesma rede local.
- **Observação sobre Loopback**: Caso cliente e servidor estivessem na mesma máquina física Windows, seria necessária a exceção `CheckNetIsolation LoopbackExempt`. No cenário deste projeto (servidor em container LXC Proxmox dedicado), a conexão ocorre por IP de rede local padrão, sem restrição de loopback.

### 4.3. Xbox (Xbox One, Xbox Series S/X)
- **Limitação Oficial**: Por diretriz e restrição da Microsoft/plataforma de consoles, os consoles Xbox (bem como PlayStation e Nintendo Switch) **não possuem** o botão oficial *Adicionar Servidor* (*Add Server*) na interface do Minecraft Bedrock. Apenas servidores parceiros oficiais (Featured Servers) e Realms são exibidos na aba de servidores.
- **Soluções Técnicas**:
  1. **Descoberta LAN Nativa (Oficial/Semi-automática)**:
     - Se o console Xbox estiver exatamente no mesmo domínio de broadcast da rede local (mesma sub-rede L2 sem bloqueio de tráfego multicast/broadcast pelo switch/roteador) e `enable-lan-visibility=true`, o servidor Bedrock Dedicated Server pode aparecer sob a aba *Amigos* como jogo em rede local.
  2. **Proxy de Broadcast LAN / Relay de Pacotes (Solução Não Oficial / Comunidade)**:
     - Softwares de relay como *Phantom* ou *MCServerConnector* / *BedrockTogether* rodam na rede local (podendo rodar no próprio LXC ou em um dispositivo local) emitindo anúncios broadcast periódicos emulando um jogo LAN para o Xbox, redirecionando o tráfego para o BDS.
  3. **Redirecionamento de DNS / BedrockConnect (Solução Não Oficial / Comunidade)**:
     - Configuração de servidor DNS local (ex.: Pi-hole, AdGuard Home ou o utilitário BedrockConnect) para apontar o domínio de um dos parceiros oficiais (ex.: `geo.hivebedrock.network`) para o IP do servidor local ou para o proxy BedrockConnect, abrindo um menu de seleção de servidores customizados diretamente na tela do console.

## 5. Estrutura de Arquivos do BDS v1.26.52.3
Arquivos presentes na raiz da distribuição oficial:
- `bedrock_server`: Executável binário ELF 64-bit para Linux.
- `bedrock_server_how_to.html`: Manual oficial com tabela completa de propriedades e comandos.
- `server.properties`: Arquivo principal de configuração no formato chave=valor.
- `allowlist.json`: Lista de controle de acesso (gamertags e XUIDs autorizados).
- `permissions.json`: Definição de papéis de usuários (`operator`, `member`, `visitor`).
- `packetlimitconfig.json`: Configuração de taxa de limitação de pacotes (algoritmo Bucket).
- `profanity_filter.wlist`: Lista de palavras do filtro de conteúdo.
- `release-notes.txt`: Notas de lançamento e links de suporte.
- `behavior_packs/` e `resource_packs/`: Pacotes vanilla de comportamentos e texturas de todas as versões históricas até 1.26.52.
- `definitions/`: Estruturas e regras do motor Bedrock.

Diretórios gerados em tempo de execução:
- `worlds/`: Contém os mundos do servidor, onde a pasta interna leva o nome definido em `level-name`.
- `keys/`: Diretório para `server_identity_key.pem` (chave privada P-384 / secp384r1 para identificação criptográfica do servidor).
- `system_behavior_packs/` e `system_resource_packs/`: Diretórios para pacotes administrativos globais.

## 6. Mecanismo Oficial de Backup a Quente
*Fonte: `bedrock_server_how_to.html` - Seção Backups*

O BDS utiliza o banco de dados LevelDB para armazenar dados de chunks e mundos. Uma cópia crua de arquivos durante a execução corrompe o mundo devido a escritas concorrentes e arquivos `.ldb` abertos.
O protocolo oficial de backup a quente consiste em 3 comandos via console:
1. `save hold`: Notifica o servidor para preparar o snapshot de backup. Comando assíncrono. O servidor fecha e trava arquivos atuais de log e abre novos para escrita.
2. `save query`: Chamado periodicamente até retornar sucesso (`Data saved. Files are now ready to be copied.`). Retorna uma lista de pares `arquivo:comprimento_em_bytes`.
   - **Regra Crítica de Integridade**: O servidor continua em execução e pode escrever além do tamanho reportado. Os arquivos copiados DEVEM ser truncados exatamente ao comprimento reportado pelo `save query`.
3. `save resume`: Notifica o servidor de que a cópia dos arquivos foi concluída, liberando o BDS para expurgar arquivos antigos e retomar a rotação normal de logs.
