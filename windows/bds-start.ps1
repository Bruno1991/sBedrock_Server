<#
.SYNOPSIS
    Inicializacao interativa do Bedrock Dedicated Server no Windows.
.DESCRIPTION
    Inicia o executavel bedrock_server.exe no diretorio de runtime com console
    interativo em primeiro plano para administracao em tempo real, com validacao
    de processo unico, deteccao de IP de rede e verificacao de dependencias.
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

# 1. Validacao de existencia do binario
if (-not (Test-Path $exePath)) {
    Write-Host "[ERRO] Executavel nao encontrado em: $exePath" -ForegroundColor Red
    Write-Host "Execute primeiro o instalador: .\windows\bds-install.ps1" -ForegroundColor Yellow
    exit 1
}

# 2. Protecao contra instancia duplicada (evita corrupcao do LevelDB)
$existingProc = Get-Process -Name "bedrock_server" -ErrorAction SilentlyContinue
if ($existingProc) {
    Write-Host "[AVISO] O Bedrock Dedicated Server ja esta em execucao (PID: $($existingProc.Id))!" -ForegroundColor Yellow
    Write-Host "Nao e permitido rodar mais de uma instancia simultanea no mesmo diretorio de dados." -ForegroundColor Yellow
    Write-Host "Para acessar ou encerrar o servidor atual, utilize a janela do console correspondente (digite 'stop')." -ForegroundColor Yellow
    return
}

# 3. Verificacao de dependencias essenciais de runtime
$hasVcRuntime = (Test-Path "$env:SystemRoot\System32\vcruntime140.dll") -or (Test-Path "$runtimeDir\vcruntime140.dll")
if (-not $hasVcRuntime) {
    Write-Host "[AVISO] Microsoft Visual C++ 2015-2022 Redistributable (x64) nao detectado no sistema." -ForegroundColor Yellow
    Write-Host "Se o servidor falhar ao iniciar, instale o pacote redistribuivel oficial da Microsoft." -ForegroundColor Yellow
}

# 4. Obter porta configurada e IPs da rede local
$port = "19132"
$propsFile = "$runtimeDir\server.properties"
if (Test-Path $propsFile) {
    Get-Content $propsFile | ForEach-Object {
        if ($_ -match '^\s*server-port\s*=\s*(\d+)') {
            $port = $matches[1]
        }
    }
}

$localIps = [System.Net.Dns]::GetHostAddresses([System.Net.Dns]::GetHostName()) | 
    Where-Object { $_.AddressFamily -eq [System.Net.Sockets.AddressFamily]::InterNetwork } | 
    ForEach-Object { $_.IPAddressToString }
$ipDisplay = if ($localIps) { $localIps -join ", " } else { "127.0.0.1" }

# 5. Dica de loopback para conexao no mesmo PC
$loopbackCheck = (CheckNetIsolation.exe LoopbackExempt -s 2>$null) -match "Microsoft.MinecraftUWP_8wekyb3d8bbwe"

Write-Host "======================================================================" -ForegroundColor Green
Write-Host " Iniciando Minecraft Bedrock Dedicated Server (Console Ativo)" -ForegroundColor Green
Write-Host " Diretório:  $runtimeDir" -ForegroundColor Cyan
Write-Host " IP Local:   $ipDisplay" -ForegroundColor White
Write-Host " Porta UDP:  $port" -ForegroundColor White
if (-not $loopbackCheck) {
    Write-Host " Dica UWP:   Para jogar neste PC, execute: .\windows\habilitar-conexao-local.bat" -ForegroundColor Yellow
}
Write-Host " Parada:     Para encerrar de forma limpa, digite 'stop' no console." -ForegroundColor Yellow
Write-Host "======================================================================" -ForegroundColor Green

Push-Location $runtimeDir
try {
    & .\bedrock_server.exe
} finally {
    Pop-Location
}
