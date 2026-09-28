@echo off
REM ==============================================================================
REM Executa a isencao de loopback para permitir que o Minecraft deste mesmo PC conecte em localhost
REM ==============================================================================
title Habilitar Conexao Local (Loopback)
cd /d "%~dp0"

net session >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [INFO] Solicitando privilegios de Administrador para configurar o Loopback...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process cmd.exe -ArgumentList '/c \"\"%~f0\"\"' -Verb RunAs"
    exit /b
)

powershell -NoProfile -ExecutionPolicy Bypass -File ".\enable-loopback.ps1"
echo.
pause

