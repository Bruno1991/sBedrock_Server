<#
.SYNOPSIS
    Healthcheck e Smoke Test do Bedrock Dedicated Server no Windows.
.DESCRIPTION
    Verifica se o processo bedrock_server.exe esta em execucao, se a porta UDP
    esta escutando na rede e se a isencao de loopback esta ativa para o Minecraft UWP.
#>

[CmdletBinding()]
param (
    [int]$ExpectedPort = 19132
)

$ErrorActionPreference = "Continue"

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host " Healthcheck & Smoke Test: Minecraft Bedrock Server (Windows)" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan

$passed = $true

# 1. Verificar processo
Write-Host -NoNewline "[1/3] Verificando processo bedrock_server.exe... "
$proc = Get-Process -Name "bedrock_server" -ErrorAction SilentlyContinue
if ($proc) {
    Write-Host "OK (PID: $($proc.Id), RAM: $([math]::Round($proc.WorkingSet64 / 1MB, 1)) MB)" -ForegroundColor Green
} else {
    Write-Host "FALHA (processo nao encontrado em execucao)" -ForegroundColor Red
    $passed = $false
}

# 2. Verificar porta de rede UDP
Write-Host -NoNewline "[2/3] Verificando escuta de rede na porta UDP $ExpectedPort... "
$endpoint = Get-NetUDPEndpoint -LocalPort $ExpectedPort -ErrorAction SilentlyContinue
if ($endpoint) {
    Write-Host "OK (Socket UDP aberto em $($endpoint.LocalAddress):$ExpectedPort)" -ForegroundColor Green
} else {
    Write-Host "FALHA (porta $ExpectedPort nao encontrada em escuta)" -ForegroundColor Red
    $passed = $false
}

# 3. Verificar isencao de loopback
Write-Host -NoNewline "[3/3] Verificando isencao de loopback UWP... "
$loopbackStatus = CheckNetIsolation.exe LoopbackExempt -s
if ($loopbackStatus -match "Microsoft.MinecraftUWP_8wekyb3d8bbwe") {
    Write-Host "OK (Minecraft UWP liberado para conectar em localhost)" -ForegroundColor Green
} else {
    Write-Host "AVISO (isencao de loopback nao detectada; execute .\windows\enable-loopback.ps1)" -ForegroundColor Yellow
}

Write-Host "======================================================================" -ForegroundColor Cyan
if ($passed) {
    Write-Host "[RESULTADO] O servidor esta ONLINE, saudavel e pronto para conexoes!" -ForegroundColor Green
} else {
    Write-Host "[RESULTADO] O servidor nao esta ativo no momento." -ForegroundColor Yellow
    Write-Host "Para iniciar, execute: .\windows\bds-start.ps1" -ForegroundColor Yellow
}
Write-Host "======================================================================" -ForegroundColor Cyan
