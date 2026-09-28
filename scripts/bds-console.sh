#!/usr/bin/env bash
# ==============================================================================
# Script: bds-console.sh
# Responsabilidade: Conexao interativa do operador humano ao console do
# Bedrock Dedicated Server (BDS) atraves da sessao Tmux dedicada.
# ==============================================================================

set -euo pipefail

TMUX_SESSION="${BDS_TMUX_SESSION:-bds-server}"

if ! tmux has-session -t "$TMUX_SESSION" 2>/dev/null; then
    echo "[ERRO] A sessao Tmux '$TMUX_SESSION' nao esta ativa." >&2
    echo "Certifique-se de que o servico minecraft-bedrock esta rodando: systemctl status minecraft-bedrock" >&2
    exit 1
fi

echo "======================================================================"
echo " Conectando ao console interativo do Bedrock Dedicated Server"
echo " Para desanexar do console sem fechar o servidor, pressione: Ctrl+B, depois D"
echo "======================================================================"
sleep 1

tmux attach-session -t "$TMUX_SESSION"
