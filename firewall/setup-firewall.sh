#!/usr/bin/env bash
# ==============================================================================
# Script: setup-firewall.sh
# Responsabilidade: Configuracao e reforco (hardening) do firewall UFW no container
# LXC do Bedrock Dedicated Server (BDS), liberando estritamente as portas necessarias.
# ==============================================================================
# Referencia Oficial: BDS v1.26.52.3 - bedrock_server_how_to.html (Networking)
# ==============================================================================

set -euo pipefail

if [[ $(id -u) -ne 0 ]]; then
    echo "[ERRO] Este script de firewall deve ser executado como root (ou com sudo)." >&2
    exit 1
fi

LAN_SUBNET="${BDS_LAN_SUBNET:-192.168.0.0/16}"
PORT_IPV4="${BDS_SERVER_PORT:-19132}"
PORT_IPV6="${BDS_SERVER_PORT_V6:-19133}"
TRANSPORT_MODE="${BDS_TRANSPORT:-raknet}"

echo "======================================================================"
echo " Configurando Firewall UFW para Minecraft Bedrock Dedicated Server"
echo "======================================================================"

# 1. Instalar UFW caso necessario
if ! command -v ufw >/dev/null 2>&1; then
    apt-get update -qq && apt-get install -y -qq ufw
fi

# 2. Definir politicas padrao restritivas
echo "[1/4] Aplicando politicas padrao (bloquear entrada, permitir saida)..."
ufw default deny incoming
ufw default allow outgoing

# 3. Liberar SSH administrativo restrito a rede local
echo "[2/4] Liberando porta SSH (22/tcp) para a sub-rede local ($LAN_SUBNET)..."
ufw allow from "$LAN_SUBNET" to any port 22 proto tcp comment "SSH Admin Local"

# 4. Liberar portas conforme modo de transporte oficial
if [[ "$TRANSPORT_MODE" == "raknet" ]]; then
    echo "[3/4] Liberando portas UDP do modo RakNet ($PORT_IPV4 e $PORT_IPV6)..."
    ufw allow "$PORT_IPV4"/udp comment "Minecraft BDS Gameplay & LAN Discovery (IPv4)"
    ufw allow "$PORT_IPV6"/udp comment "Minecraft BDS Gameplay (IPv6)"
elif [[ "$TRANSPORT_MODE" == "nethernet" ]]; then
    echo "[3/4] Liberando portas do modo NetherNet (TCP $PORT_IPV4 e range UDP)..."
    ufw allow "$PORT_IPV4"/tcp comment "Minecraft BDS NetherNet Signaling Handshake"
    # Range padrao ou definido pelo operador
    UDP_RANGE="${BDS_NETHERNET_UDP_RANGE:-19132:19140}"
    ufw allow "$UDP_RANGE"/udp comment "Minecraft BDS NetherNet WebRTC Gameplay"
fi

# 5. Ativar firewall
echo "[4/4] Ativando firewall UFW..."
ufw --force enable

echo "======================================================================"
echo " Status atual das regras de firewall:"
ufw status verbose
echo "======================================================================"
