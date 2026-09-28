#!/usr/bin/env bash
# ==============================================================================
# Script: bds-install.sh
# Responsabilidade: Instalacao e provisionamento automatizado e idempotente do
# Bedrock Dedicated Server (BDS) v1.26.52.3 em container Linux (Ubuntu 22.04/24.04 LTS).
# Cria o usuario sem privilegios 'bedrock', particiona o layout de pastas,
# valida o checksum criptografico SHA-256 do pacote oficial, gera a chave ECDSA P-384,
# aplica configuracoes a partir dos templates e instala as units do systemd.
# ==============================================================================
# Referencia Oficial: BDS v1.26.52.3 - bedrock_server_how_to.html
# SHA-256: f6348d84fa714d04ca194f207e89453ca6bba0a1359396475271a52a150471c6
# ==============================================================================

set -euo pipefail

# 1. Verificacao de privilegios de root para instalacao
if [[ $(id -u) -ne 0 ]]; then
    echo "[ERRO] Este script de provisionamento deve ser executado como root (ou com sudo)." >&2
    exit 1
fi

BDS_VERSION="${BDS_VERSION:-1.26.52.3}"
EXPECTED_SHA256="${BDS_EXPECTED_SHA256:-f6348d84fa714d04ca194f207e89453ca6bba0a1359396475271a52a150471c6}"
OFFICIAL_DOWNLOAD_URL="https://www.minecraft.net/bedrockdedicatedserver/bin-linux/bedrock-server-${BDS_VERSION}.zip"

BASE_DIR="/opt/bds"
VERSIONS_DIR="${BASE_DIR}/versions"
TARGET_VERSION_DIR="${VERSIONS_DIR}/${BDS_VERSION}"
DATA_DIR="${BASE_DIR}/data"
CONFIG_DIR="${DATA_DIR}/config"
WORLDS_DIR="${DATA_DIR}/worlds"
KEYS_DIR="${DATA_DIR}/keys"
BACKUPS_DIR="${DATA_DIR}/backups"
CUSTOM_PACKS_DIR="${DATA_DIR}/custom_packs"
RUNTIME_DIR="${BASE_DIR}/runtime"
BIN_DIR="${BASE_DIR}/bin"

SCRIPT_SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_SRC_DIR}/.." && pwd)"

echo "======================================================================"
echo " Provisionamento Automatizado: Bedrock Dedicated Server v${BDS_VERSION}"
echo "======================================================================"

# 2. Instalar pacotes de prerequisitos no sistema operacional
echo "[1/9] Verificando e instalando pacotes necessarios via apt..."
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq \
    curl \
    unzip \
    jq \
    tmux \
    libssl3 \
    ca-certificates \
    openssl \
    tar \
    gzip \
    ufw \
    iproute2 \
    procps

# 3. Criar usuario e grupo dedicado 'bedrock' (sem privilegios, sem shell de login)
echo "[2/9] Configurando usuario de sistema 'bedrock'..."
if ! getent group bedrock >/dev/null 2>&1; then
    groupadd -r bedrock
fi

if ! id -u bedrock >/dev/null 2>&1; then
    useradd -r -g bedrock -d "$RUNTIME_DIR" -s /usr/sbin/nologin -c "Minecraft Bedrock Service User" bedrock
    passwd -l bedrock >/dev/null 2>&1 || true
fi

# 4. Criar estrutura de diretorios particionada conforme ADR-003
echo "[3/9] Criando layout de diretorios sob ${BASE_DIR}..."
mkdir -p \
    "$VERSIONS_DIR" \
    "$TARGET_VERSION_DIR" \
    "$CONFIG_DIR" \
    "$WORLDS_DIR" \
    "$KEYS_DIR" \
    "$BACKUPS_DIR" \
    "$CUSTOM_PACKS_DIR" \
    "$RUNTIME_DIR" \
    "$BIN_DIR"

# 5. Baixar pacote oficial do BDS e verificar hash SHA-256
ARCHIVE_CACHE="/tmp/bedrock-server-${BDS_VERSION}.zip"
if [[ ! -f "${TARGET_VERSION_DIR}/bedrock_server" ]]; then
    echo "[4/9] Baixando binario oficial v${BDS_VERSION}..."
    curl -fsSL -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64)" "$OFFICIAL_DOWNLOAD_URL" -o "$ARCHIVE_CACHE"

    echo "[INFO] Verificando checksum criptografico SHA-256..."
    CALCULATED_SHA256=$(sha256sum "$ARCHIVE_CACHE" | cut -d' ' -f1)
    if [[ "$CALCULATED_SHA256" != "$EXPECTED_SHA256" ]]; then
        echo "[ERRO CRITICO] O checksum SHA-256 do arquivo baixado ($CALCULATED_SHA256) nao confere com o oficial esperado ($EXPECTED_SHA256)!" >&2
        rm -f "$ARCHIVE_CACHE"
        exit 1
    fi
    echo "[INFO] Checksum verificado com sucesso ($CALCULATED_SHA256)."

    echo "[INFO] Extraindo binarios imutaveis em ${TARGET_VERSION_DIR}..."
    unzip -q -o "$ARCHIVE_CACHE" -d "$TARGET_VERSION_DIR"
    chmod +x "${TARGET_VERSION_DIR}/bedrock_server"
    rm -f "$ARCHIVE_CACHE"
else
    echo "[4/9] Binario oficial v${BDS_VERSION} ja extraido em ${TARGET_VERSION_DIR}."
fi

# 6. Gerar par de chaves ECDSA P-384 oficial para identidade persistente do servidor
# Conforme documentado no bedrock_server_how_to.html (Server Identity)
SERVER_KEY_PEM="${KEYS_DIR}/server_identity_key.pem"
if [[ ! -f "$SERVER_KEY_PEM" ]]; then
    echo "[5/9] Gerando chave oficial de identidade do servidor (secp384r1)..."
    openssl ecparam -name secp384r1 -genkey -noout -out "$SERVER_KEY_PEM"
    chmod 600 "$SERVER_KEY_PEM"
else
    echo "[5/9] Chave de identidade do servidor ja existente em: $SERVER_KEY_PEM"
fi

# 7. Gerar configuracoes oficiais a partir dos templates
echo "[6/9] Gerando e validando configuracoes a partir dos templates..."
export BDS_BASE_DIR="$BASE_DIR"
export BDS_DATA_DIR="$DATA_DIR"
export BDS_TEMPLATE_DIR="${REPO_ROOT}/templates"
export BDS_ENV_FILE="${REPO_ROOT}/.env"

"${SCRIPT_SRC_DIR}/bds-config.sh"

# 8. Montar links simbolicos no diretorio de runtime conforme ADR-003
echo "[7/9] Montando links simbolicos no diretorio de runtime (${RUNTIME_DIR})..."
ln -sfn "${TARGET_VERSION_DIR}/bedrock_server" "${RUNTIME_DIR}/bedrock_server"
ln -sfn "${TARGET_VERSION_DIR}/definitions" "${RUNTIME_DIR}/definitions"
ln -sfn "${TARGET_VERSION_DIR}/resource_packs" "${RUNTIME_DIR}/resource_packs"
ln -sfn "${TARGET_VERSION_DIR}/behavior_packs" "${RUNTIME_DIR}/behavior_packs"

ln -sfn "${CONFIG_DIR}/server.properties" "${RUNTIME_DIR}/server.properties"
ln -sfn "${CONFIG_DIR}/allowlist.json" "${RUNTIME_DIR}/allowlist.json"
ln -sfn "${CONFIG_DIR}/permissions.json" "${RUNTIME_DIR}/permissions.json"
ln -sfn "${CONFIG_DIR}/packetlimitconfig.json" "${RUNTIME_DIR}/packetlimitconfig.json"

ln -sfn "$WORLDS_DIR" "${RUNTIME_DIR}/worlds"
ln -sfn "$KEYS_DIR" "${RUNTIME_DIR}/keys"

# Registrar versao atual
echo "$BDS_VERSION" > "${DATA_DIR}/current_version.txt"

# 9. Copiar scripts operacionais e criar atalhos globais
echo "[8/9] Instalando utilitarios operacionais em ${BIN_DIR} e /usr/local/bin..."
for script in bds-cmd.sh bds-console.sh bds-backup.sh bds-restore.sh bds-update.sh bds-rollback.sh bds-healthcheck.sh bds-config.sh; do
    if [[ -f "${SCRIPT_SRC_DIR}/${script}" ]]; then
        cp "${SCRIPT_SRC_DIR}/${script}" "${BIN_DIR}/${script}"
        chmod 755 "${BIN_DIR}/${script}"
        
        # Criar symlink sem extensao em /usr/local/bin (ex.: 'bds-cmd' chamando 'bds-cmd.sh')
        cmd_name="${script%.sh}"
        ln -sfn "${BIN_DIR}/${script}" "/usr/local/bin/${cmd_name}"
    fi
done

# 10. Instalar units do systemd
echo "[9/9] Instalando units do systemd..."
SYSTEMD_SRC="${REPO_ROOT}/systemd"
if [[ -d "$SYSTEMD_SRC" ]]; then
    cp "${SYSTEMD_SRC}/minecraft-bedrock.service" /etc/systemd/system/
    cp "${SYSTEMD_SRC}/minecraft-bedrock-backup.service" /etc/systemd/system/
    cp "${SYSTEMD_SRC}/minecraft-bedrock-backup.timer" /etc/systemd/system/
    systemctl daemon-reload
fi

# Ajustar todas as permissoes finais para o usuario 'bedrock'
chown -R bedrock:bedrock "$BASE_DIR"

echo "======================================================================"
echo " [SUCESSO] Bedrock Dedicated Server v${BDS_VERSION} instalado com exito!"
echo " Para iniciar o servico execute: systemctl enable --now minecraft-bedrock"
echo " Para ativar backups automaticos: systemctl enable --now minecraft-bedrock-backup.timer"
echo "======================================================================"
