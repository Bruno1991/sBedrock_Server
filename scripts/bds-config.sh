#!/usr/bin/env bash
# ==============================================================================
# Script: bds-config.sh
# Responsabilidade: Geracao e validacao deterministica das configuracoes do BDS
# a partir dos templates oficiais (server.properties, allowlist.json,
# permissions.json e packetlimitconfig.json), aplicando variaveis de ambiente
# ou arquivo .env local sem alterar o codigo central do servidor.
# ==============================================================================
# Referencia Oficial: BDS v1.26.52.3 - bedrock_server_how_to.html
# ==============================================================================

set -euo pipefail

# Diretorios padrao
BASE_DIR="${BDS_BASE_DIR:-/opt/bds}"
DATA_DIR="${BDS_DATA_DIR:-${BASE_DIR}/data}"
CONFIG_DIR="${DATA_DIR}/config"
TEMPLATE_DIR="${BDS_TEMPLATE_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/templates}"
ENV_FILE="${BDS_ENV_FILE:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/.env}"

echo "[INFO] Iniciando geracao de configuracoes do Bedrock Dedicated Server..."

# 1. Carregar arquivo .env caso exista
if [[ -f "$ENV_FILE" ]]; then
    echo "[INFO] Carregando variaveis de configuracao de: $ENV_FILE"
    # Exportar variaveis ignorando comentarios e linhas vazias
    set -a
    # shellcheck disable=SC1090
    source "$ENV_FILE"
    set +a
fi

# 2. Garantir existencia do diretorio de destino
mkdir -p "$CONFIG_DIR"

# 3. Definir variaveis com valores padrao auditados (v1.26.52.3)
export BDS_SERVER_NAME="${BDS_SERVER_NAME:-Bedrock Dedicated Server}"
export BDS_GAMEMODE="${BDS_GAMEMODE:-survival}"
export BDS_FORCE_GAMEMODE="${BDS_FORCE_GAMEMODE:-false}"
export BDS_DIFFICULTY="${BDS_DIFFICULTY:-normal}"
export BDS_ALLOW_CHEATS="${BDS_ALLOW_CHEATS:-false}"
export BDS_MAX_PLAYERS="${BDS_MAX_PLAYERS:-10}"
export BDS_ONLINE_MODE="${BDS_ONLINE_MODE:-true}"
export BDS_ALLOW_LIST="${BDS_ALLOW_LIST:-true}"
export BDS_DEFAULT_PLAYER_PERMISSION="${BDS_DEFAULT_PLAYER_PERMISSION:-member}"
export BDS_TRANSPORT="${BDS_TRANSPORT:-raknet}"
export BDS_SERVER_PORT="${BDS_SERVER_PORT:-19132}"
export BDS_SERVER_PORT_V6="${BDS_SERVER_PORT_V6:-19133}"
export BDS_ENABLE_LAN_VISIBILITY="${BDS_ENABLE_LAN_VISIBILITY:-true}"
export BDS_VIEW_DISTANCE="${BDS_VIEW_DISTANCE:-20}"
export BDS_TICK_DISTANCE="${BDS_TICK_DISTANCE:-4}"
export BDS_MAX_THREADS="${BDS_MAX_THREADS:-4}"
export BDS_PLAYER_IDLE_TIMEOUT="${BDS_PLAYER_IDLE_TIMEOUT:-30}"
export BDS_LEVEL_NAME="${BDS_LEVEL_NAME:-Bedrock level}"
export BDS_LEVEL_SEED="${BDS_LEVEL_SEED:-}"
export BDS_TEXTUREPACK_REQUIRED="${BDS_TEXTUREPACK_REQUIRED:-false}"
export BDS_ENABLE_PACKET_LIMITER="${BDS_ENABLE_PACKET_LIMITER:-true}"

# 4. Validacoes estritas de valores aceitos pela documentacao oficial
case "$BDS_GAMEMODE" in
    survival|creative|adventure) ;;
    *) echo "[ERRO] gamemode invalido: '$BDS_GAMEMODE'. Permitidos: survival, creative, adventure" >&2; exit 1 ;;
esac

case "$BDS_DIFFICULTY" in
    peaceful|easy|normal|hard) ;;
    *) echo "[ERRO] difficulty invalida: '$BDS_DIFFICULTY'. Permitidas: peaceful, easy, normal, hard" >&2; exit 1 ;;
esac

case "$BDS_TRANSPORT" in
    raknet|nethernet) ;;
    *) echo "[ERRO] transport invalido: '$BDS_TRANSPORT'. Permitidos: raknet, nethernet" >&2; exit 1 ;;
esac

case "$BDS_DEFAULT_PLAYER_PERMISSION" in
    visitor|member|operator) ;;
    *) echo "[ERRO] default-player-permission-level invalido: '$BDS_DEFAULT_PLAYER_PERMISSION'. Permitidos: visitor, member, operator" >&2; exit 1 ;;
esac

if [[ "$BDS_SERVER_PORT" -lt 1 || "$BDS_SERVER_PORT" -gt 65535 ]]; then
    echo "[ERRO] server-port fora do intervalo [1-65535]: $BDS_SERVER_PORT" >&2
    exit 1
fi

if [[ "$BDS_TICK_DISTANCE" -lt 4 || "$BDS_TICK_DISTANCE" -gt 12 ]]; then
    echo "[ERRO] tick-distance fora do intervalo [4-12]: $BDS_TICK_DISTANCE" >&2
    exit 1
fi

if [[ "$BDS_VIEW_DISTANCE" -lt 5 ]]; then
    echo "[ERRO] view-distance deve ser maior ou igual a 5: $BDS_VIEW_DISTANCE" >&2
    exit 1
fi

# 5. Gerar server.properties por substituicao segura
SERVER_PROP_TARGET="${CONFIG_DIR}/server.properties"
SERVER_PROP_TEMPLATE="${TEMPLATE_DIR}/server.properties.template"

if [[ ! -f "$SERVER_PROP_TEMPLATE" ]]; then
    echo "[ERRO] Template nao encontrado em: $SERVER_PROP_TEMPLATE" >&2
    exit 1
fi

echo "[INFO] Gerando ${SERVER_PROP_TARGET} a partir do template..."

# Substituicao deterministica via awk/sed sem depender de pacotes externos pesados
# Preserva comentarios e substitui os padroes ${VAR:-DEFAULT}
awk '
{
    line = $0;
    while (match(line, /\$\{([A-Z0-9_]+)(:-([^}]*))?\}/, arr)) {
        var_name = arr[1];
        default_val = arr[3];
        val = ENVIRON[var_name];
        if (val == "") {
            val = default_val;
        }
        sub(/\$\{([A-Z0-9_]+)(:-([^}]*))?\}/, val, line);
    }
    print line;
}
' "$SERVER_PROP_TEMPLATE" > "${SERVER_PROP_TARGET}.tmp"

mv "${SERVER_PROP_TARGET}.tmp" "$SERVER_PROP_TARGET"
chmod 644 "$SERVER_PROP_TARGET"

# 6. Copiar ou inicializar arquivos JSON caso ainda nao existam no destino
# (Garante idempotencia e nao sobrescreve cadastros ja existentes feitos pelo operador)
copy_template_if_missing() {
    local template_name="$1"
    local target_name="$2"
    local template_file="${TEMPLATE_DIR}/${template_name}"
    local target_file="${CONFIG_DIR}/${target_name}"

    if [[ ! -f "$target_file" ]]; then
        if [[ -f "$template_file" ]]; then
            echo "[INFO] Inicializando $target_name a partir de $template_name..."
            cp "$template_file" "$target_file"
            chmod 644 "$target_file"
        else
            echo "[WARN] Template $template_file nao encontrado; criando JSON vazio: $target_name"
            echo "[]" > "$target_file"
            chmod 644 "$target_file"
        fi
    else
        echo "[INFO] Arquivo persistente $target_name ja existe; preservando dados atuais."
    fi
}

copy_template_if_missing "allowlist.json.template" "allowlist.json"
copy_template_if_missing "permissions.json.template" "permissions.json"
copy_template_if_missing "packetlimitconfig.json.template" "packetlimitconfig.json"

echo "[INFO] Configuracoes geradas e validadas com sucesso em: $CONFIG_DIR"
