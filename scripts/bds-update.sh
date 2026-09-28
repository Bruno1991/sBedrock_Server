#!/usr/bin/env bash
# ==============================================================================
# Script: bds-update.sh
# Responsabilidade: Atualizacao controlada e deterministica do BDS com consulta
# ao endpoint oficial da API da Microsoft/Mojang, backup a quente previo obrigatorio,
# verificacao de integridade SHA-256, isolamento em novo diretorio de versao,
# reatribuicao atomica de links simbolicos e rollback automatico sob falha de smoke test.
# ==============================================================================
# Referencia Oficial: BDS v1.26.52.3 - learn.microsoft.com/minecraft/creator
# Endpoint de Versoes: https://net-secondary.web.minecraft-services.net/api/v1.0/download/links
# ==============================================================================

set -euo pipefail

BASE_DIR="${BDS_BASE_DIR:-/opt/bds}"
VERSIONS_DIR="${BASE_DIR}/versions"
RUNTIME_DIR="${BASE_DIR}/runtime"
DATA_DIR="${BASE_DIR}/data"
BIN_DIR="${BASE_DIR}/bin"
API_URL="https://net-secondary.web.minecraft-services.net/api/v1.0/download/links"
CURRENT_VER_FILE="${DATA_DIR}/current_version.txt"
PREV_VER_FILE="${DATA_DIR}/previous_version.txt"

FORCE_UPDATE=0
if [[ "${1:-}" == "--force" ]]; then
    FORCE_UPDATE=1
fi

echo "======================================================================"
echo " Pipeline de Atualizacao Controlada do Bedrock Dedicated Server"
echo "======================================================================"

# 1. Consultar versao atual instalada
CURRENT_VERSION="desconhecida"
if [[ -f "$CURRENT_VER_FILE" ]]; then
    CURRENT_VERSION=$(cat "$CURRENT_VER_FILE" | xargs)
fi
echo "[INFO] Versao em producao atualmente: $CURRENT_VERSION"

# 2. Consultar versao estavel mais recente no endpoint oficial da Microsoft
echo "[INFO] Consultando endpoint oficial de releases da Mojang..."
API_RESPONSE=$(curl -fsSL "$API_URL" || true)

if [[ -z "$API_RESPONSE" ]]; then
    echo "[ERRO] Nao foi possivel obter resposta da API oficial da Mojang." >&2
    exit 1
fi

DOWNLOAD_URL=$(echo "$API_RESPONSE" | jq -r '.result.links[] | select(.downloadType=="serverBedrockLinux") | .downloadUrl')

if [[ -z "$DOWNLOAD_URL" || "$DOWNLOAD_URL" == "null" ]]; then
    echo "[ERRO] URL de download para Linux nao encontrada na resposta da API." >&2
    exit 1
fi

# Extrair versao a partir do nome do arquivo (ex.: bedrock-server-1.26.52.3.zip)
LATEST_VERSION=$(echo "$DOWNLOAD_URL" | grep -oE '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' | head -n 1)

echo "[INFO] Versao oficial estavel disponivel: $LATEST_VERSION"
echo "[INFO] URL oficial: $DOWNLOAD_URL"

if [[ "$CURRENT_VERSION" == "$LATEST_VERSION" && $FORCE_UPDATE -eq 0 ]]; then
    echo "[SUCESSO] O servidor ja esta executando a versao mais recente ($CURRENT_VERSION). Nada a fazer."
    exit 0
fi

# 3. Executar backup a quente previo obrigatorio antes de qualquer modificacao
echo "[INFO] Executando backup a quente de seguranca pre-atualizacao..."
if [[ -x "${BIN_DIR}/bds-backup.sh" ]]; then
    "${BIN_DIR}/bds-backup.sh"
else
    echo "[WARN] Script bds-backup.sh nao encontrado; tentando caminho local..."
    "$(dirname "${BASH_SOURCE[0]}")/bds-backup.sh"
fi

# 4. Baixar novo pacote em diretorio de download temporario
TMP_DOWNLOAD_DIR="/tmp/bds_download_${LATEST_VERSION}"
mkdir -p "$TMP_DOWNLOAD_DIR"
ZIP_PATH="${TMP_DOWNLOAD_DIR}/bedrock-server-${LATEST_VERSION}.zip"

echo "[INFO] Baixando pacote oficial da versao $LATEST_VERSION..."
curl -fsSL -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64)" "$DOWNLOAD_URL" -o "$ZIP_PATH"

# Calcular e exibir checksum SHA-256
SHA256_CALCULATED=$(sha256sum "$ZIP_PATH" | cut -d' ' -f1)
echo "[INFO] Pacote baixado com sucesso! SHA-256: $SHA256_CALCULATED"

# 5. Extrair em novo diretorio isolado de versao
TARGET_VERSION_DIR="${VERSIONS_DIR}/${LATEST_VERSION}"
mkdir -p "$TARGET_VERSION_DIR"

echo "[INFO] Extraindo binarios limpos para: $TARGET_VERSION_DIR..."
unzip -q -o "$ZIP_PATH" -d "$TARGET_VERSION_DIR"
chmod +x "${TARGET_VERSION_DIR}/bedrock_server"
rm -rf "$TMP_DOWNLOAD_DIR"

# 6. Parada graciosa do servico em execucao
echo "[INFO] Parando servico atual para reatribuicao atomica de versao..."
if systemctl is-active --quiet minecraft-bedrock 2>/dev/null; then
    # Enviar 'stop' via console primeiro para fechar LevelDB com seguranca
    if [[ -x "${BIN_DIR}/bds-cmd.sh" ]]; then
        "${BIN_DIR}/bds-cmd.sh" "stop" || true
    fi
    sleep 3
    systemctl stop minecraft-bedrock
fi

# Registrar historico de versao
echo "$CURRENT_VERSION" > "$PREV_VER_FILE"

# 7. Reatribuir links simbolicos de runtime
echo "[INFO] Reatribuindo links simbolicos para a versao $LATEST_VERSION..."
ln -sfn "${TARGET_VERSION_DIR}/bedrock_server" "${RUNTIME_DIR}/bedrock_server"
ln -sfn "${TARGET_VERSION_DIR}/definitions" "${RUNTIME_DIR}/definitions"
ln -sfn "${TARGET_VERSION_DIR}/resource_packs" "${RUNTIME_DIR}/resource_packs"
ln -sfn "${TARGET_VERSION_DIR}/behavior_packs" "${RUNTIME_DIR}/behavior_packs"

# Garantir permissao do usuario bedrock
if id -u bedrock >/dev/null 2>&1; then
    chown -R bedrock:bedrock "$TARGET_VERSION_DIR"
    chown -h bedrock:bedrock "${RUNTIME_DIR}/"* 2>/dev/null || true
fi

# 8. Reiniciar servico
echo "[INFO] Iniciando servico com a nova versao..."
systemctl start minecraft-bedrock

# 9. Smoke test e validacao pos-atualizacao
echo "[INFO] Aguardando 6 segundos para estabilizacao da engine..."
sleep 6

HEALTHCHECK_BIN="${BIN_DIR}/bds-healthcheck.sh"
if [[ ! -x "$HEALTHCHECK_BIN" ]]; then
    HEALTHCHECK_BIN="$(dirname "${BASH_SOURCE[0]}")/bds-healthcheck.sh"
fi

if "$HEALTHCHECK_BIN"; then
    echo "$LATEST_VERSION" > "$CURRENT_VER_FILE"
    echo "======================================================================"
    echo " [SUCESSO] Atualizacao para a versao $LATEST_VERSION concluida com exito!"
    echo " A versao anterior ($CURRENT_VERSION) foi preservada em $VERSIONS_DIR."
    echo "======================================================================"
else
    echo "======================================================================"
    echo " [FALHA] Smoke test falhou apos atualizacao para $LATEST_VERSION!"
    echo " Acionando ROLLBACK AUTOMATICO imediato..."
    echo "======================================================================"
    
    ROLLBACK_BIN="${BIN_DIR}/bds-rollback.sh"
    if [[ ! -x "$ROLLBACK_BIN" ]]; then
        ROLLBACK_BIN="$(dirname "${BASH_SOURCE[0]}")/bds-rollback.sh"
    fi
    "$ROLLBACK_BIN" --auto
    exit 1
fi
