#!/usr/bin/env bash
# ==============================================================================
# Script: bds-healthcheck.sh
# Responsabilidade: Verificacao automatizada de integridade operacional (Healthcheck
# e Smoke Test) do Bedrock Dedicated Server. Valida o status da unit systemd,
# o UID do processo, a escuta da porta de rede e ausencia de falhas criticas.
# ==============================================================================
# Referencia Oficial: BDS v1.26.52.3 - bedrock_server_how_to.html
# ==============================================================================

set -euo pipefail

SERVICE_NAME="minecraft-bedrock"
TMUX_SESSION="${BDS_TMUX_SESSION:-bds-server}"
EXPECTED_USER="bedrock"
EXPECTED_PORT="${BDS_SERVER_PORT:-19132}"

echo "======================================================================"
echo " Executando Smoke Test & Healthcheck: $SERVICE_NAME"
echo "======================================================================"

EXIT_CODE=0

# 1. Verificar se a unit do systemd esta com status 'active'
echo -n "[1/5] Verificando status da unit systemd... "
if systemctl is-active --quiet "$SERVICE_NAME" 2>/dev/null; then
    echo "OK (active)"
else
    echo "FALHA (inativo ou em estado de erro)"
    EXIT_CODE=1
fi

# 2. Verificar se a sessao Tmux isolada existe
echo -n "[2/5] Verificando sessao Tmux '$TMUX_SESSION'... "
if tmux has-session -t "$TMUX_SESSION" 2>/dev/null; then
    echo "OK (sessao ativa)"
else
    echo "FALHA (sessao nao encontrada)"
    EXIT_CODE=1
fi

# 3. Verificar se o processo 'bedrock_server' pertence ao usuario nao-root 'bedrock'
echo -n "[3/5] Verificando processo bedrock_server e usuario de execucao... "
BDS_PID=$(pgrep -f "bedrock_server" | head -n 1 || true)
if [[ -n "$BDS_PID" ]]; then
    ACTUAL_USER=$(ps -o user= -p "$BDS_PID" | xargs)
    if [[ "$ACTUAL_USER" == "$EXPECTED_USER" ]]; then
        echo "OK (PID: $BDS_PID rodando sob $ACTUAL_USER)"
    else
        echo "FALHA (PID: $BDS_PID rodando sob usuario inesperado: $ACTUAL_USER, esperado: $EXPECTED_USER)"
        EXIT_CODE=1
    fi
else
    echo "FALHA (processo bedrock_server nao encontrado em execucao)"
    EXIT_CODE=1
fi

# 4. Verificar se a porta de jogo (19132 UDP) esta escutando
echo -n "[4/5] Verificando socket de rede na porta $EXPECTED_PORT... "
if command -v ss >/dev/null 2>&1; then
    if ss -ulpn 2>/dev/null | grep -q ":${EXPECTED_PORT} "; then
        echo "OK (porta UDP $EXPECTED_PORT escutando)"
    elif ss -tlpn 2>/dev/null | grep -q ":${EXPECTED_PORT} "; then
        echo "OK (porta TCP $EXPECTED_PORT escutando em modo NetherNet)"
    else
        echo "FALHA (porta $EXPECTED_PORT nao encontrada aberta)"
        EXIT_CODE=1
    fi
else
    echo "AVISO (utilitario 'ss' nao encontrado, ignorando checagem de socket)"
fi

# 5. Analisar ultimas mensagens do console do servidor em busca de erros fatais
echo -n "[5/5] Analisando console do servidor para confirmacao de inicializacao... "
if tmux has-session -t "$TMUX_SESSION" 2>/dev/null; then
    CONSOLE_OUTPUT=$(tmux capture-pane -pt "$TMUX_SESSION" -S -30)
    if echo "$CONSOLE_OUTPUT" | grep -qi "Server started"; then
        echo "OK (Mensagem 'Server started' confirmada)"
    elif echo "$CONSOLE_OUTPUT" | grep -qi "Crash"; then
        echo "FALHA (Detectado relato de Crash na engine)"
        EXIT_CODE=1
    else
        echo "OK (Sem registros de falha fatal detectados)"
    fi
else
    echo "IGNORADO (Sessao ausente)"
fi

echo "======================================================================"
if [[ $EXIT_CODE -eq 0 ]]; then
    echo "[RESULTADO FINAL] Todos os testes passaram! Servidor 100% saudavel."
else
    echo "[RESULTADO FINAL] Falha em um ou mais testes de saude." >&2
fi
echo "======================================================================"

exit $EXIT_CODE
