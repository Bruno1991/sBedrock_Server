<!--
Responsabilidade: Plano de rede, topologia local-first, alocação de portas, regras de firewall
e matriz detalhada de conectividade para clientes Android, PC Windows e consoles Xbox.
-->

# Plano de Rede e Conectividade de Clientes

## 1. Topologia de Rede e Arquitetura Local-First

O servidor Bedrock Dedicated Server (BDS) é implantado sob a premissa de **arquitetura estritamente local-first**:
- Todo o processamento, persistência de dados e tráfego de gameplay ocorrem dentro da rede local (LAN).
- O servidor não requer portas encaminhadas para a internet (sem port-forwarding no roteador WAN) por padrão.
- Apenas a autenticação de contas de jogadores (`online-mode=true`) realiza consultas externas pontuais à infraestrutura oficial Xbox Live da Microsoft para validar XUIDs legítimos.

---

## 2. Alocação de Portas e Protocolos

A tabela a seguir especifica as portas conforme o modo de transporte configurado no `server.properties` (v1.26.52.3):

| Serviço / Função | Porta Padrão | Protocolo | Modo Aplicável | Observações Oficiais |
| :--- | :--- | :--- | :--- | :--- |
| **BDS Gameplay (IPv4)** | `19132` | UDP | `transport=raknet` | Porta padrão para todos os clientes Bedrock. |
| **BDS Gameplay (IPv6)** | `19133` | UDP | `transport=raknet` | Porta padrão para conectividade IPv6. |
| **Descoberta LAN (Broadcast)** | `19132` | UDP | Ambos (`enable-lan-visibility=true`) | Escuta e responde a buscas na rede local. |
| **Sinalização NetherNet (HTTP)** | `19132` | TCP | `transport=nethernet` | Socket dual-stack para handshake WebRTC. |
| **Gameplay NetherNet (WebRTC)** | `19132-19140` | UDP | `transport=nethernet` | Intervalo configurado via `server-udp-ports`. |
| **Acesso SSH Administrativo** | `22` | TCP | Host LXC | Apenas para gerenciamento via chave SSH na LAN. |

> [!NOTE]
> Conforme deliberado no [ADR-002](file:///C:/dev/s_Bedrock_Server/docs/adr/ADR-002-network-transport-and-ports.md), o projeto adota o modo **`transport=raknet`** como padrão, garantindo que apenas a porta `19132/udp` necessite estar aberta no firewall do container.

---

## 3. Política e Regras de Firewall (UFW / Linux)

O firewall no container LXC opera sob o princípio de menor privilégio:
```bash
# Política padrão: negar entrada e permitir saída
ufw default deny incoming
ufw default allow outgoing

# Liberar porta de tráfego de jogo Bedrock (UDP)
ufw allow 19132/udp comment "Minecraft Bedrock Gameplay and LAN Discovery"
ufw allow 19133/udp comment "Minecraft Bedrock IPv6 (Opcional)"

# Liberar SSH administrativo restrito à sub-rede local (exemplo: 192.168.1.0/24)
ufw allow from 192.168.1.0/24 to any port 22 proto tcp comment "SSH Admin Local"

# Ativar firewall
ufw enable
```

---

## 4. Matriz de Conectividade por Plataforma de Cliente

### 4.1. Android (Smartphones e Tablets)
- **Método de Conexão Oficial 1 (Adicionar Servidor)**:
  1. Abrir o Minecraft Bedrock no dispositivo Android.
  2. Clicar em **Jogar** (*Play*) -> aba **Servidores** (*Servers*).
  3. Rolar até o final da lista e clicar em **Adicionar Servidor** (*Add Server*).
  4. Preencher:
     - **Nome do Servidor**: ex.: `BDS Proxmox`
     - **Endereço do Servidor**: IP local do container LXC (ex.: `192.168.1.50`)
     - **Porta**: `19132`
  5. Clicar em **Salvar** (*Save*) ou **Jogar** (*Play*).
- **Método de Conexão Oficial 2 (Descoberta LAN Automática)**:
  - Com o dispositivo conectado ao mesmo Wi-Fi/sub-rede do servidor e `enable-lan-visibility=true`, o servidor aparece automaticamente na aba **Amigos** (*Friends*) na seção **Jogos em LAN** (*LAN Games*).

### 4.2. PC (Windows 10 / Windows 11)
- **Método de Conexão Oficial 1 (Adicionar Servidor)**:
  1. Abrir o Minecraft Bedrock Edition (instalado via Microsoft Store).
  2. Navegar em **Jogar** -> aba **Servidores** -> **Adicionar Servidor**.
  3. Informar o IP local do container LXC e a porta `19132`.
- **Método de Conexão Oficial 2 (Descoberta LAN)**:
  - Exibido automaticamente sob **Amigos** -> **Jogos em LAN**.
- **Nota Técnica sobre Isolamento de Loopback no Windows**:
  - Quando cliente e servidor rodam na mesma máquina física com Windows, a plataforma UWP bloqueia tráfego local por padrão, exigindo o comando `CheckNetIsolation LoopbackExempt -a -n=Microsoft.MinecraftUWP_8wekyb3d8bbwe`. Como nesta arquitetura o servidor BDS roda isolado em um container LXC no Proxmox, essa restrição não se aplica aos computadores clientes na rede local.

### 4.3. Consoles Xbox (Xbox One, Xbox Series S, Xbox Series X)

#### Limitação Oficial da Plataforma
A Microsoft/Xbox não disponibiliza o botão "Adicionar Servidor" (*Add Server*) nas edições de console do Minecraft Bedrock devido a políticas de certificação de plataforma e restrições de ecossistema fechado. Apenas os servidores parceiros oficiais da Mojang (*Featured Servers*) e assinaturas Realms aparecem na lista padrão.

#### Soluções Disponíveis para o Xbox

##### 1. Descoberta LAN Nativa (Oficial / Suportada pelo BDS)
- **Como Funciona**: O Bedrock Dedicated Server possui a diretiva `enable-lan-visibility=true`, emitindo anúncios UDP periódicos de broadcast na porta 19132.
- **Requisitos**: O console Xbox e o container LXC do BDS devem estar **estritamente na mesma sub-rede IP (L2)** sem roteamento intermediário e sem isolamento de portas (Client Isolation) no ponto de acesso Wi-Fi.
- **Como Acessar no Xbox**: Abrir o Minecraft -> aba **Amigos** -> rolar até a seção **Jogos em LAN**. Se o roteador permitir repasse de broadcast/multicast local, o servidor BDS aparecerá diretamente ali.

##### 2. Emulador de Broadcast LAN / Proxy de Pacotes (Solução Não Oficial da Comunidade)
- **Status**: Não documentado oficialmente pela Microsoft; desenvolvido pela comunidade.
- **Ferramentas Comuns**:
  - **Phantom** ([https://github.com/jhead/phantom](https://github.com/jhead/phantom)): Utilitário leve em Go que pode rodar em segundo plano no próprio container LXC do BDS.
  - **MCServerConnector** / **BedrockTogether**: Aplicativos executados em um smartphone Android/iOS conectado ao mesmo Wi-Fi do Xbox.
- **Como Funciona**: A ferramenta envia continuamente pacotes de anúncio LAN UDP formatados para o console Xbox, informando a existência de um jogo local, e retransmite o tráfego do Xbox diretamente para a porta do BDS. O Xbox passa a exibir o servidor instantaneamente na aba "Amigos -> Jogos em LAN".

##### 3. Redirecionamento de DNS / BedrockConnect (Solução Não Oficial da Comunidade)
- **Status**: Não documentado oficialmente pela Microsoft; desenvolvido pela comunidade.
- **Ferramentas Comuns**: **BedrockConnect** ([https://github.com/Pugmatt/BedrockConnect](https://github.com/Pugmatt/BedrockConnect)) ou regras de DNS Rewrite no Pi-hole / AdGuard Home.
- **Como Funciona**:
  1. Configura-se no Xbox um servidor DNS local (ex.: o IP do container LXC ou de um Pi-hole).
  2. Quando o jogador no Xbox clica em um dos servidores oficiais parceiros (ex.: *The Hive* ou *Galaxite*), a requisição DNS de `geo.hivebedrock.network` é interceptada e direcionada para a interface do BedrockConnect.
  3. Uma tela intermediária em formato de menu do jogo é exibida no Xbox, permitindo ao jogador digitar ou selecionar o IP e a porta do servidor local BDS.

---

## 5. Resumo Comparativo para o Operador

| Plataforma | Suporte a Conexão Direta por IP | Suporte a Descoberta LAN | Requer Ferramenta Auxiliar? |
| :--- | :--- | :--- | :--- |
| **Android** | Sim (Oficial) | Sim (Oficial) | Não |
| **PC Windows** | Sim (Oficial) | Sim (Oficial) | Não |
| **Xbox** | Não (Bloqueado pela plataforma) | Sim (Se estiver no mesmo L2) | Opcional (apenas se a rede bloquear broadcast L2) |
