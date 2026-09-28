#!/usr/bin/env bash
# ==============================================================================
# Script: bds-restore.sh
# Responsabilidade: Procedimento automatizado e seguro de recuperacao de desastres
# (Disaster Recovery). Valida o checksum SHA-256 do arquivo de backup, interrompe
# o servico, isola o mundo danificado, extrai os dados e reestabelece a operacao.
# ==============================================================================
# Referencia Oficial: BDS v1.26.52.3 - bedrock_server_how_to.html
# ==============================================================================

set -euo pipefail

BASE_DIR="${BDS_BASE_DIR:-/opt/bds}"
DATA_DIR="${BDS_DATA_DIR:-${BASE_DIR}/data}"
BACKUP_DIR="${BDS_BACKUP_DIR:-${DATA_DIR}/backups}"

if [[ $# -lt 1 ]]; then
    echo "Uso: $0 <caminho_ou_nome_do_arquivo_de_backup.tar.gz>" >&2
    echo "Backups disponiveis em $BACKUP_DIR:" >&2
    ls -lh "$BACKUP_DIR"/bds-backup-*.tar.gz 2>/dev/null || echo "Nenhum backup encontrado." >&2
    exit 1
fi

TARGET_BACKUP="$1"

# Resolver caminho absoluto caso seja fornecido apenas o nome do arquivo
if [[ ! -f "$TARGET_BACKUP" && -f "${BACKUP_DIR}/${TARGET_BACKUP}" ]]; then
    TARGET_BACKUP="${BACKUP_DIR}/${TARGET_BACKUP}"
fi

if [[ ! -f "$TARGET_BACKUP" ]]; then
    echo "[ERRO] Arquivo de backup nao encontrado: $TARGET_BACKUP" >&2
    exit 1
fi

CHECKSUM_FILE="${TARGET_BACKUP}.sha256"

# 1. Validacao de integridade criptografica
if [[ -f "$CHECKSUM_FILE" ]]; then
    echo "[INFO] Validando checksum SHA-256 do arquivo de backup..."
    (cd "$(dirname "$TARGET_BACKUP")" && sha256sum -c "$(basename "$CHECKSUM_FILE")")
    echo "[INFO] Checksum verificado com sucesso!"
else
    echo "[WARN] Arquivo de checksum nao encontrado ($CHECKSUM_FILE); procedendo com cautela."
fi

# 2. Interromper o servico
echo "[INFO] Interrompendo servico minecraft-bedrock..."
if systemctl is-active --quiet minecraft-bedrock 2>/dev/null; then
    systemctl stop minecraft-bedrock
fi

# 3. Isolar o mundo danificado atual
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
if [[ -d "${DATA_DIR}/worlds" ]]; then
    CORRUPTED_BACKUP="${DATA_DIR}/worlds.damaged.${TIMESTAMP}"
    echo "[INFO] Movendo mundo atual para isolamento: $CORRUPTED_BACKUP"
    mv "${DATA_DIR}/worlds" "$CORRUPTED_BACKUP"
fi

# 4. Extrair dados do backup
echo "[INFO] Restaurando arquivos a partir de: $TARGET_BACKUP..."
tar -xzf "$TARGET_BACKUP" -C "$DATA_DIR"

# 5. Ajustar permissoes de sistema
echo "[INFO] Ajustando permissoes para o usuario de servico 'bedrock'..."
if id -u bedrock >/dev/null 2>&1; then
    chown -R bedrock:bedrock "${DATA_DIR}/worlds"
    if [[ -d "${DATA_DIR}/config" ]]; then
        chown -R bedrock:bedrock "${DATA_DIR}/config"
    fi
fi

# 6. Reiniciar o servico
echo "[INFO] Reiniciando servico minecraft-bedrock..."
systemctl start minecraft-bedrock

# 7. Validar inicializacao
sleep 3
if systemctl is-active --quiet minecraft-bedrock; then
    echo "[SUCESSO] Servidor restaurado e ativo com sucesso!"
else
    echo "[ERRO] O servico falhou ao reiniciar apos a restauracao. Verifique logs com: journalctl -u minecraft-bedrock -n 50" >&2
    exit 1
fi
