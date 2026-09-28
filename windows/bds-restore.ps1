<#
.SYNOPSIS
    Recuperacao de desastres (Restore) do Bedrock Dedicated Server no Windows.
.DESCRIPTION
    Valida o hash SHA-256 do arquivo de backup (.zip), isola o mundo atual danificado
    e restaura os dados do mundo e configuracoes a partir do backup selecionado.
#>

[CmdletBinding()]
param (
    [Parameter(Mandatory=$true, Position=0)]
    [string]$BackupFile,
    [string]$ServerDir = ""
)

$ErrorActionPreference = "Stop"

if (-not $ServerDir) {
    $ServerDir = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\server"))
}

$backupsDir = "$ServerDir\data\backups"
$dataDir = "$ServerDir\data"

# Resolver caminho
if (-not (Test-Path $BackupFile) -and (Test-Path "$backupsDir\$BackupFile")) {
    $BackupFile = "$backupsDir\$BackupFile"
}

if (-not (Test-Path $BackupFile)) {
    Write-Host "[ERRO] Arquivo de backup nao encontrado: $BackupFile" -ForegroundColor Red
    Write-Host "Backups disponiveis em $($backupsDir):" -ForegroundColor Yellow
    Get-ChildItem -Path $backupsDir -Filter "bds-backup-win-*.zip" | Select-Object Name, Length, LastWriteTime
    exit 1
}

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host " Restauracao de Backup do Bedrock Dedicated Server (Windows)" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan

# 1. Verificar se o servidor esta rodando
$proc = Get-Process -Name "bedrock_server" -ErrorAction SilentlyContinue
if ($proc) {
    Write-Host "[INFO] Parando processo bedrock_server ativo..." -ForegroundColor Yellow
    Stop-Process -Id $proc.Id -Force
    Start-Sleep -Seconds 2
}

# 2. Validar hash SHA-256 se existir arquivo .sha256
$checksumFile = "$BackupFile.sha256"
if (Test-Path $checksumFile) {
    Write-Host "[INFO] Validando integridade SHA-256..." -ForegroundColor Cyan
    $expectedHash = (Get-Content $checksumFile).Trim().Split(" ")[0].ToLower()
    $actualHash = (Get-FileHash -Path $BackupFile -Algorithm SHA256).Hash.ToLower()

    if ($expectedHash -ne $actualHash) {
        throw "ERRO CRITICO: Hash SHA-256 do arquivo ($actualHash) nao confere com o registrado ($expectedHash)!"
    }
    Write-Host "[INFO] Checksum SHA-256 verificado com sucesso!" -ForegroundColor Green
}

# 3. Isolar o mundo danificado atual
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$worldsDir = "$dataDir\worlds"
if (Test-Path $worldsDir) {
    $damagedDir = "$dataDir\worlds.damaged.$timestamp"
    Write-Host "[INFO] Movendo mundo atual para isolamento: $damagedDir" -ForegroundColor Cyan
    Move-Item -Path $worldsDir -Destination $damagedDir -Force
}

# 4. Extrair o backup
Write-Host "[INFO] Restaurando arquivos a partir de: $BackupFile..." -ForegroundColor Cyan
Expand-Archive -Path $BackupFile -DestinationPath $dataDir -Force

Write-Host "======================================================================" -ForegroundColor Green
Write-Host " [SUCESSO] Backup restaurado com sucesso em $dataDir!" -ForegroundColor Green
Write-Host " Para iniciar o servidor novamente: .\windows\bds-start.ps1" -ForegroundColor Yellow
Write-Host "======================================================================" -ForegroundColor Green
