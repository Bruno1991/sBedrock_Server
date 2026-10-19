@echo off
REM ==============================================================================
REM Atalho para restaurar o mapa original do Bedrock Dedicated Server
REM Remove todas as alteracoes feitas por jogadores e restaura o mapa limpo
REM ==============================================================================
title Restaurar Mapa Original - BDS
cd /d "%~dp0"
python "%~dp0reset_test_map.py"
pause
