@echo off
REM ==============================================================================
REM Desativador Rapido do Mod CobbleDrock - Minecraft Bedrock Dedicated Server
REM ==============================================================================
title Desativar CobbleDrock - Minecraft BDS
cd /d "%~dp0"
python "%~dp0gerenciar_cobbledrock.py" --disable
pause
