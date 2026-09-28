#!/usr/bin/env bash
# ==============================================================================
# Script: bds-cmd.sh
# Responsabilidade: Interface de comando entre processos (IPC) para envio
# de instrucoes administrativas ao console do Bedrock Dedicated Server (BDS)
# em execucao na sessao isolada do Tmux (bds-server).
# ==============================================================================
# Referencia Oficial: BDS v1.26.52.3 - bedrock_server_how_to.html (Commands)
# ==============================================================================

set -euo pipefail

TMUX_SESSION="${BDS_TMUX_SESSION:-bds-server}"

if [[ $# -lt 1 ]]; then
    echo "Uso: $0 <comando_do_servidor> [argumentos...]" >&2
    echo "Exemplos:" >&2
    echo "  $0 help" >&2
    echo "  $0 allowlist reload" >&2
    echo "  $0 allowlist list" >&2
    echo "  $0 \"tellraw @a {\\\"rawtext\\\":[{\\\"text\\\":\\\"Ola Mundo\\\"}]}\"" >&2
    exit 1
fi

COMMAND="$*"

# Verificar se a sessao do Tmux esta ativa
if ! tmux has-session -t "$TMUX_SESSION" 2>/dev/null; then
    echo "[ERRO] A sessao Tmux '$TMUX_SESSION' nao esta em execucao." >&2
    echo "Verifique se o servico esta ativo: systemctl status minecraft-bedrock" >&2
    exit 1
fi

# Enviar comando para a sessao do Tmux
tmux send-keys -t "$TMUX_SESSION" "$COMMAND" ENTER

# Aguardar breve intervalo para processamento da engine
sleep 0.3

# Opcional: imprimir as ultimas linhas para visualizacao do retorno imediato
if [[ "${BDS_CMD_QUIET:-false}" != "true" ]]; then
    tmux capture-pane -pt "$TMUX_SESSION" -S -8 | sed '/^$/d' | tail -n 5
fi
