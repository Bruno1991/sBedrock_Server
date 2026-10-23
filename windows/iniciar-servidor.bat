@echo off
REM ==============================================================================
REM Atalho de execucao do utilitario CLI unificado do Bedrock Dedicated Server
REM ==============================================================================
title Minecraft Bedrock Dedicated Server - CLI
cd /d "%~dp0"
chcp 65001 >nul
python cli.py %*
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [!] Processo encerrado com codigo %ERRORLEVEL%.
    pause
)
