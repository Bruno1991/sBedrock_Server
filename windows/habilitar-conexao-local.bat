@echo off
REM ==============================================================================
REM Executa a isencao de loopback para permitir que o Minecraft deste mesmo PC conecte em localhost
REM ==============================================================================
title Habilitar Conexao Local (Loopback)
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File ".\enable-loopback.ps1"
pause
