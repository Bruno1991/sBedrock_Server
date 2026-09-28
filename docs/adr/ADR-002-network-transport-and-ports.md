<!--
Responsabilidade: Decisão de arquitetura sobre o protocolo de transporte de rede (NetherNet vs RakNet),
mapeamento de portas, políticas de firewall e regras de descoberta para rede local e consoles.
-->
---
document_id: adr-002-network-transport-and-ports
title: Transporte de Rede, Mapeamento de Portas e Descoberta LAN
document_type: adr
status: proposed
version: 1.0.0
language: pt-BR
owners: [architecture-maintainers]
last_updated: "2026-09-28"
review_cycle_days: 365
license: MIT
---

# ADR-002: Transporte de Rede, Mapeamento de Portas e Descoberta LAN

## Estado

`proposed` — 2026-09-28 — Decisores: Equipe de Engenharia / Mantenedor do Projeto.

## Contexto

A versão 1.26.52.3 do Bedrock Dedicated Server (BDS) oferece duas opções para a propriedade `transport`:
1. `nethernet`: Protocolo baseado em WebRTC (padrão recente introduzido pela Mojang).
2. `raknet`: Protocolo tradicional baseado em UDP sobre a biblioteca RakNet.

O ambiente de implantação é estritamente **local-first** em rede doméstica/empresarial (Proxmox LXC), atendendo clientes Android, Windows PC e consoles Xbox. O firewall do container LXC deve operar no princípio de menor privilégio (bloqueio de entrada padrão, liberando estritamente as portas necessárias).

Forças em consideração:
- **Simplicidade e Previsibilidade de Firewall**: Abrir uma porta fixa previsível facilita auditorias de segurança e regras no UFW/nftables.
- **Descoberta em Rede Local (LAN Discovery)**: A opção `enable-lan-visibility=true` permite que clientes na mesma sub-rede descubram o servidor sem precisar digitar IP e porta manualmente. No console Xbox, onde não existe a opção nativa de "Adicionar Servidor", a visibilidade LAN nativa ou via relay de broadcast é fundamental.
- **Comportamento do NetherNet**: O NetherNet abre um socket TCP em `server-port` (19132) para handshake HTTP e, por padrão, aloca portas UDP efêmeras aleatórias do kernel Linux para o tráfego de gameplay. Sem configuração explícita de `server-udp-ports`, o firewall do container bloquearia as conexões UDP dos clientes.

## Opções consideradas

### Opção 1: Transporte RakNet Tradicional (`transport=raknet`) (Recomendada para LAN Local)
- **Funcionamento**: O servidor opera inteiramente sobre UDP direto. Escuta na porta 19132/UDP (IPv4) e 19133/UDP (IPv6). A descoberta LAN ocorre via broadcast na porta 19132/UDP.
- **Vantagens**:
  - **Superfície de Firewall Mínima e Determinística**: Apenas 1 regra de firewall: liberar `19132/udp` (e opcionalmente `19133/udp` se IPv6 estiver ativo).
  - **Compatibilidade Consagrada**: É o protocolo com maior maturidade em ferramentas de proxy LAN para console (Phantom, BedrockConnect, MCServerConnector).
  - **Sem Tráfego TCP HTTP no Servidor**: Evita a necessidade de gerenciar signaling WebRTC ou terminação proxy.
- **Desvantagens**:
  - É o transporte legado que a Mojang planeja substituir progressivamente por NetherNet em versões futuras.

### Opção 2: Transporte NetherNet (`transport=nethernet`) com Portas UDP Fixadas
- **Funcionamento**: O servidor escuta em `19132/tcp` para sinalização HTTP/WebRTC e utiliza um intervalo estrito fixado via `server-udp-ports=19132-19140` para o tráfego UDP dos clientes.
- **Vantagens**:
  - Utiliza o padrão mais recente da Mojang (v1.26.52.3).
- **Desvantagens**:
  - Exige liberar tanto TCP quanto um range de portas UDP no firewall.
  - Aumenta a complexidade de configuração e a sensibilidade a restrições de NAT/firewall entre sub-redes.

## Decisão

Adotar como padrão recomendado a **Opção 1: Transporte RakNet Tradicional (`transport=raknet`)**, disponibilizando no template de configuração o suporte explícito e documentado para alternância para NetherNet caso desejado pelo operador.

### Configuração Recomendada no Template:
```properties
# Protocolo de transporte selecionado para máxima estabilidade em rede local e consoles
transport=raknet

# Portas oficiais Bedrock
server-port=19132
server-portv6=19133

# Descoberta na rede local ativada para clientes LAN e Xbox
enable-lan-visibility=true
```

### Regras de Firewall (UFW / nftables) no Container LXC:
- **Default Policy**: `DENY incoming`, `ALLOW outgoing`.
- **Regras Liberadas**:
  - `19132/udp` (Tráfego de jogo IPv4 e broadcast LAN)
  - `19133/udp` (Tráfego de jogo IPv6, se habilitado)
  - `22/tcp` (Acesso SSH administrativo restrito à sub-rede local)

*Nota*: Caso o operador opte por alterar para `transport=nethernet`, o firewall deverá liberar adicionalmente `19132/tcp` e o intervalo UDP definido em `server-udp-ports`.

## Consequências

- **Efeitos Positivos**:
  - Comportamento de rede amplamente previsível.
  - Clientes Android e Windows conectam diretamente via IP/porta `19132/udp`.
  - Dispositivos na mesma sub-rede visualizam o servidor automaticamente na aba "Amigos -> Jogos em LAN".
- **Efeitos Negativos**:
  - Requer monitorar futuros lançamentos da Mojang caso a flag `transport=raknet` seja descontinuada.

## Plano de validação e reversão

- **Sinais de Sucesso**:
  - `ss -ulpn | grep 19132` confirma socket UDP aberto pelo executável `bedrock_server`.
  - Cliente Android/Windows na mesma LAN localiza o servidor na aba "Amigos" ou conecta via IP:19132.
- **Procedimento de Reversão**:
  - Para alternar entre protocolos, basta ajustar a linha `transport=` no arquivo gerado via template e reiniciar o serviço (`systemctl restart minecraft-bedrock`).

## Referências

- Documentação Oficial BDS: `bedrock_server_how_to.html` (v1.26.52.3) - Seções *Transport* e *Configuration*.
- Configuração oficial: `server.properties` (v1.26.52.3).
