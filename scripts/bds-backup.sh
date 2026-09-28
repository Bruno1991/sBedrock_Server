#!/usr/bin/env bash
# ==============================================================================
# Script: bds-backup.sh
# Responsabilidade: Execucao do pipeline oficial de backup a quente do BDS
# utilizando os comandos da engine 'save hold', 'save query' e 'save resume',
# com truncamento exato em bytes dos arquivos LevelDB, empacotamento comprimido,
# geracao de checksum SHA-256 e rotacao por retencao temporal.
# ==============================================================================
# Referencia Oficial: BDS v1.26.52.3 - bedrock_server_how_to.html (Backups)
# ==============================================================================

set -euo pipefail

# Parametros de configuracao e diretorios
BASE_DIR="${BDS_BASE_DIR:-/opt/bds}"
DATA_DIR="${BDS_DATA_DIR:-${BASE_DIR}/data}"
WORLDS_DIR="${DATA_DIR}/worlds"
CONFIG_DIR="${DATA_DIR}/config"
BACKUP_DIR="${BDS_BACKUP_DIR:-${DATA_DIR}/backups}"
TMUX_SESSION="${BDS_TMUX_SESSION:-bds-server}"
RETENTION_DAYS="${BDS_BACKUP_RETENTION_DAYS:-14}"
QUERY_TIMEOUT_SECONDS=60

mkdir -p "$BACKUP_DIR"

# 1. Validacao de prerequisitos
if ! command -v tmux >/dev/null 2>&1; then
    echo "[ERRO] Utilitario 'tmux' nao encontrado no sistema." >&2
    exit 1
fi

if ! tmux has-session -t "$TMUX_SESSION" 2>/dev/null; then
    echo "[ERRO] Sessao Tmux '$TMUX_SESSION' nao esta ativa. O servidor precisa estar rodando para backup a quente." >&2
    exit 1
fi

echo "[INFO] Iniciando pipeline de backup a quente oficial do Bedrock Dedicated Server..."
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
STAGING_DIR="${BACKUP_DIR}/staging_${TIMESTAMP}"
mkdir -p "$STAGING_DIR"

# 2. Funcao de seguranca para garantir 'save resume' em qualquer saida/erro
RESUME_EXECUTED=0
cleanup_on_exit() {
    local exit_code=$?
    if [[ $RESUME_EXECUTED -eq 0 ]]; then
        echo "[WARN] Finalizacao inesperada; garantindo envio de 'save resume' a engine..."
        tmux send-keys -t "$TMUX_SESSION" "save resume" ENTER 2>/dev/null || true
    fi
    if [[ -d "$STAGING_DIR" ]]; then
        rm -rf "$STAGING_DIR"
    fi
    exit $exit_code
}
trap cleanup_on_exit EXIT INT TERM

# 3. Disparar 'save hold'
echo "[INFO] Enviando comando 'save hold' para o console do BDS..."
tmux send-keys -t "$TMUX_SESSION" "save hold" ENTER

# 4. Polling com 'save query' ate que os arquivos estejam prontos
echo "[INFO] Aguardando consolidacao dos arquivos via 'save query'..."
START_TIME=$(date +%s)
READY=0
FILE_LIST_RAW=""

while [[ $READY -eq 0 ]]; do
    CURRENT_TIME=$(date +%s)
    ELAPSED=$((CURRENT_TIME - START_TIME))

    if [[ $ELAPSED -gt $QUERY_TIMEOUT_SECONDS ]]; then
        echo "[ERRO] Timeout de ${QUERY_TIMEOUT_SECONDS}s aguardando confirmacao de 'save query'." >&2
        exit 1
    fi

    # Enviar comando de consulta
    tmux send-keys -t "$TMUX_SESSION" "save query" ENTER
    sleep 1.5

    # Capturar ultimas 30 linhas do console
    OUTPUT=$(tmux capture-pane -pt "$TMUX_SESSION" -S -30)

    # Verificar se a mensagem de sucesso foi emitida
    # Formato oficial: "Data saved. Files are now ready to be copied." seguido da lista
    if echo "$OUTPUT" | grep -q "Files are now ready to be copied"; then
        READY=1
        # Extrair a linha ou bloco que contem a lista de arquivos
        # As entradas seguem o formato: arquivo:bytes, arquivo:bytes...
        FILE_LIST_RAW=$(echo "$OUTPUT" | awk '/Files are now ready to be copied/{flag=1; next} flag{print} /A previous save has not been completed/{flag=0}' | tr -d '\r' | tr '\n' ' ')
        
        # Caso a lista esteja na propria linha seguinte ou no restante da sentenca:
        if [[ -z "${FILE_LIST_RAW// }" ]]; then
            FILE_LIST_RAW=$(echo "$OUTPUT" | grep -A 2 "Files are now ready to be copied" | tail -n +2 | tr -d '\r' | tr '\n' ' ')
        fi
        break
    elif echo "$OUTPUT" | grep -q "A previous save has not been completed"; then
        echo "[INFO] Engine ainda preparando arquivos de snapshot... (${ELAPSED}s)"
    elif echo "$OUTPUT" | grep -q "Saving..."; then
        echo "[INFO] Engine gravando memtables no disco... (${ELAPSED}s)"
    fi

    sleep 1
done

echo "[INFO] Arquivos do snapshot confirmados pelo servidor!"

# 5. Processar e truncar cada arquivo reportado
# A lista bruta contem itens separados por virgula: caminho/arquivo:bytes
# Exemplo: Bedrock level/db/000005.ldb:2097152, Bedrock level/level.dat:2348
IFS=',' read -r -a ENTRIES <<< "$FILE_LIST_RAW"

COPIED_COUNT=0
for entry in "${ENTRIES[@]}"; do
    # Remover espacos em branco nas extremidades
    clean_entry=$(echo "$entry" | xargs)
    if [[ -z "$clean_entry" || "$clean_entry" != *:* ]]; then
        continue
    fi

    file_path="${clean_entry%:*}"
    file_bytes="${clean_entry##*:}"

    # Limpeza adicional de espacos
    file_path=$(echo "$file_path" | xargs)
    file_bytes=$(echo "$file_bytes" | xargs)

    src_file="${WORLDS_DIR}/${file_path}"
    dest_file="${STAGING_DIR}/worlds/${file_path}"

    if [[ ! -f "$src_file" ]]; then
        echo "[WARN] Arquivo reportado nao encontrado no disco: $src_file"
        continue
    fi

    mkdir -p "$(dirname "$dest_file")"

    # Copiar e truncar para o comprimento exato em bytes especificado pela doc oficial
    if command -v truncate >/dev/null 2>&1; then
        cp "$src_file" "$dest_file"
        truncate -s "$file_bytes" "$dest_file"
    else
        # Fallback portavel caso truncate nao esteja presente
        head -c "$file_bytes" "$src_file" > "$dest_file"
    fi

    COPIED_COUNT=$((COPIED_COUNT + 1))
done

echo "[INFO] Total de arquivos copiados e truncados com sucesso: $COPIED_COUNT"

# 6. Enviar 'save resume' imediatamente para liberar retencao de logs na engine
echo "[INFO] Enviando 'save resume' para o BDS..."
tmux send-keys -t "$TMUX_SESSION" "save resume" ENTER
RESUME_EXECUTED=1
sleep 1

# 7. Incluir configuracoes ativas no pacote de backup
if [[ -d "$CONFIG_DIR" ]]; then
    mkdir -p "${STAGING_DIR}/config"
    cp -r "$CONFIG_DIR"/* "${STAGING_DIR}/config/" 2>/dev/null || true
fi

# 8. Empacotar e compactar o backup final
ARCHIVE_NAME="bds-backup-${TIMESTAMP}.tar.gz"
ARCHIVE_PATH="${BACKUP_DIR}/${ARCHIVE_NAME}"
CHECKSUM_PATH="${ARCHIVE_PATH}.sha256"

echo "[INFO] Compactando arquivo final de backup: $ARCHIVE_NAME..."
tar -czf "$ARCHIVE_PATH" -C "$STAGING_DIR" worlds config

# 9. Gerar checksum criptografico SHA-256
cd "$BACKUP_DIR"
sha256sum "$ARCHIVE_NAME" > "$CHECKSUM_PATH"

ARCHIVE_SIZE=$(du -h "$ARCHIVE_PATH" | cut -f1)
echo "[INFO] Backup concluido com sucesso! Tamanho: $ARCHIVE_SIZE | Checksum: $CHECKSUM_PATH"

# 10. Rotacao automatica de backups antigos
echo "[INFO] Aplicando politica de retencao (${RETENTION_DAYS} dias)..."
find "$BACKUP_DIR" -name "bds-backup-*.tar.gz" -type f -mtime +"$RETENTION_DAYS" -delete
find "$BACKUP_DIR" -name "bds-backup-*.sha256" -type f -mtime +"$RETENTION_DAYS" -delete

echo "[INFO] Pipeline de backup finalizado com exito."
