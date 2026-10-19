@echo off
title s_Bedrock_Server: Canivete Suíço
chcp 65001 >nul
cd /d "%~dp0windows"

python cli.py %*

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [!] Processo encerrado com código %ERRORLEVEL%.
    pause
)
