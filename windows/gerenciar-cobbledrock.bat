@echo off
REM ==============================================================================
REM Menu de Gerenciamento do Mod CobbleDrock - Minecraft Bedrock Dedicated Server
REM ==============================================================================
title Gerenciar CobbleDrock - Minecraft BDS
cd /d "%~dp0"
python "%~dp0gerenciar_cobbledrock.py" %*
