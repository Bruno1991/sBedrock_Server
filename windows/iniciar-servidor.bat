@echo off
REM ==============================================================================
REM Atalho de execucao com duplo clique para iniciar o Bedrock Dedicated Server no Windows
REM ==============================================================================
title Minecraft Bedrock Dedicated Server
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File ".\bds-start.ps1"
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo O servidor foi encerrado com erro.
    pause
)
