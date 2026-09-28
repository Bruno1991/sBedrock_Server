#!/usr/bin/env bash
# ==============================================================================
# Script: bds-rollback.sh
# Responsabilidade: Reversao atomica (Rollback) para a versao anterior do BDS.
# Reatribui os links simbolicos de runtime para a versao precedente em segundos
# e valida o retorno do servico para o estado operacional saudavel.
# ==============================================================================
# Referencia Oficial: BDS v1.26.52.3 - learn.microsoft.com/minecraft/creator
# ==============================================================================

set -euo pipefail

BASE_DIR="${BDS_BASE_DIR:-/opt/bds}"
VERSIONS_DIR="${BASE_DIR}/versions"
RUNTIME_DIR="${BASE_DIR}/runtime"
DATA_DIR="${BASE_DIR}/data"
BIN_DIR="${BASE_DIR}/bin"
CURRENT_VER_FILE="${DATA_DIR}/current_version.txt"
PREV_VER_FILE="${DATA_DIR}/previous_version.txt"

AUTO_MODE=0
if [[ "${1:-}" == "--auto" ]]; then
    AUTO_MODE=1
fi

echo "======================================================================"
echo " Procedimento de Rollback de Versao do Bedrock Dedicated Server"
echo "======================================================================"

if [[ ! -f "$PREV_VER_FILE" ]]; then
    echo "[ERRO] Arquivo de versao anterior nao encontrado: $PREV_VER_FILE" >&2
    echo "Nao ha registro de versao anterior para realizar rollback." >&2
    exit 1
fi

PREV_VERSION=$(cat "$PREV_VER_FILE" | xargs)
CURRENT_VERSION=$(cat "$CURRENT_VER_FILE" 2>/dev/null | xargs || echo "atual")

if [[ -z "$PREV_VERSION" || "$PREV_VERSION" == "desconhecida" ]]; then
    echo "[ERRO] Versao anterior registrada e invalida: '$PREV_VERSION'" >&2
    exit 1
fi

TARGET_PREV_DIR="${VERSIONS_DIR}/${PREV_VERSION}"

if [[ ! -d "$TARGET_PREV_DIR" || ! -f "${TARGET_PREV_DIR}/bedrock_server" ]]; then
    echo "[ERRO] Diretorio ou binario da versao anterior nao encontrado: $TARGET_PREV_DIR" >&2
    exit 1
fi

echo "[INFO] Revertendo da versao '$CURRENT_VERSION' para '$PREV_VERSION'..."

# 1. Parar o servico atual
echo "[INFO] Parando servico minecraft-bedrock..."
if systemctl is-active --quiet minecraft-bedrock 2>/dev/null; then
    systemctl stop minecraft-bedrock
fi

# 2. Reatribuir links simbolicos para a versao anterior
echo "[INFO] Apontando links de runtime para: $TARGET_PREV_DIR..."
ln -sfn "${TARGET_PREV_DIR}/bedrock_server" "${RUNTIME_DIR}/bedrock_server"
ln -sfn "${TARGET_PREV_DIR}/definitions" "${RUNTIME_DIR}/definitions"
ln -sfn "${TARGET_PREV_DIR}/resource_packs" "${RUNTIME_DIR}/resource_packs"
ln -sfn "${TARGET_PREV_DIR}/behavior_packs" "${RUNTIME_DIR}/behavior_packs"

# 3. Atualizar marcadores de versao
echo "$PREV_VERSION" > "$CURRENT_VER_FILE"
echo "$CURRENT_VERSION" > "$PREV_VER_FILE"

# 4. Reiniciar o servico na versao restaurada
echo "[INFO] Reiniciando servico com a versao restaurada..."
systemctl start minecraft-bedrock

# 5. Executar smoke test
sleep 5
HEALTHCHECK_BIN="${BIN_DIR}/bds-healthcheck.sh"
if [[ ! -x "$HEALTHCHECK_BIN" ]]; then
    HEALTHCHECK_BIN="$(dirname "${BASH_SOURCE[0]}")/bds-healthcheck.sh"
fi

if "$HEALTHCHECK_BIN"; then
    echo "======================================================================"
    echo " [SUCESSO] Rollback para a versao $PREV_VERSION concluido e validado!"
    echo "======================================================================"
    exit 0
else
    echo "======================================================================"
    echo " [ERRO CRITICO] O servico falhou ao reiniciar mesmo na versao revertida!"
    echo " Verifique os logs detalhados: journalctl -u minecraft-bedrock -n 50"
    echo "======================================================================"
    exit 1
fi
