<#
.SYNOPSIS
    Inicializacao interativa do Bedrock Dedicated Server no Windows.
.DESCRIPTION
    Inicia o executavel bedrock_server.exe no diretorio de runtime com console
    interativo em primeiro plano para administracao em tempo real.
#>

[CmdletBinding()]
param (
    [string]$ServerDir = ""
)

if (-not $ServerDir) {
    $ServerDir = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\server"))
}

$runtimeDir = "$ServerDir\runtime"
$exePath = "$runtimeDir\bedrock_server.exe"

if (-not (Test-Path $exePath)) {
    Write-Host "[ERRO] Executavel nao encontrado em: $exePath" -ForegroundColor Red
    Write-Host "Execute primeiro o instalador: .\windows\bds-install.ps1" -ForegroundColor Yellow
    exit 1
}

Write-Host "======================================================================" -ForegroundColor Green
Write-Host " Iniciando Minecraft Bedrock Dedicated Server (Console Ativo)" -ForegroundColor Green
Write-Host " Diretório: $runtimeDir" -ForegroundColor Cyan
Write-Host " Para parar o servidor de forma limpa, digite 'stop' no console." -ForegroundColor Yellow
Write-Host "======================================================================" -ForegroundColor Green

Push-Location $runtimeDir
try {
    & .\bedrock_server.exe
} finally {
    Pop-Location
}
