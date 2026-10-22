@echo off
REM ==============================================================================
REM Menu de Gerenciamento Central de Mods e Add-ons - Minecraft Bedrock Dedicated Server
REM ==============================================================================
title Gerenciar Mods e Add-ons - Minecraft BDS
cd /d "%~dp0"
python "%~dp0gerenciar_mods.py" %*
