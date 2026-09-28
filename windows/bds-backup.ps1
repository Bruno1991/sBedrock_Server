<#
.SYNOPSIS
    Pipeline de backup para o Bedrock Dedicated Server no Windows.
.DESCRIPTION
    Realiza o empacotamento comprimido (.zip) dos mundos LevelDB e configuracoes vigentes,
    gerando hash criptografico SHA-256 e aplicando rotacao de retencao temporal.
#>

[CmdletBinding()]
param (
    [string]$ServerDir = "",
    [int]$RetentionDays = 14
)

$ErrorActionPreference = "Stop"

if (-not $ServerDir) {
    $ServerDir = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\server"))
}

$worldsDir = "$ServerDir\data\worlds"
$configDir = "$ServerDir\data\config"
$backupsDir = "$ServerDir\data\backups"

New-Item -ItemType Directory -Force -Path $backupsDir | Out-Null

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$archiveName = "bds-backup-win-$timestamp.zip"
$archivePath = "$backupsDir\$archiveName"
$checksumPath = "$archivePath.sha256"

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host " Backup do Bedrock Dedicated Server (Windows) - $timestamp" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan

# 1. Se o servidor estiver ativo interativamente, alertar o operador
$proc = Get-Process -Name "bedrock_server" -ErrorAction SilentlyContinue
if ($proc) {
    Write-Host "[DICA] Para maxima consistencia durante o jogo ativo, digite 'save hold' no console do BDS" -ForegroundColor Yellow
    Write-Host "       antes de rodar o backup e 'save resume' logo apos." -ForegroundColor Yellow
}

$stagingDir = "$backupsDir\staging_$timestamp"
New-Item -ItemType Directory -Force -Path $stagingDir | Out-Null

try {
    # 2. Copiar mundos e configuracoes para o staging
    if (Test-Path $worldsDir) {
        Copy-Item -Path $worldsDir -Destination "$stagingDir\worlds" -Recurse -Force
    }
    if (Test-Path $configDir) {
        Copy-Item -Path $configDir -Destination "$stagingDir\config" -Recurse -Force
    }

    # 3. Compactar em arquivo .zip
    Write-Host "[INFO] Compactando arquivo de backup em: $archivePath..." -ForegroundColor Cyan
    Compress-Archive -Path "$stagingDir\*" -DestinationPath $archivePath -Force

    # 4. Gerar hash SHA-256
    $hash = (Get-FileHash -Path $archivePath -Algorithm SHA256).Hash.ToLower()
    Set-Content -Path $checksumPath -Value "$hash  $archiveName" -Encoding UTF8

    $sizeMb = [math]::Round((Get-Item $archivePath).Length / 1MB, 2)
    Write-Host "[SUCESSO] Backup concluido com sucesso! ($sizeMb MB)" -ForegroundColor Green
    Write-Host "Checksum SHA-256: $hash" -ForegroundColor Green
} finally {
    if (Test-Path $stagingDir) {
        Remove-Item -Recurse -Force $stagingDir
    }
}

# 5. Rotacao por data de modificacao
Write-Host "[INFO] Aplicando politica de retencao ($RetentionDays dias)..." -ForegroundColor Cyan
$limitDate = (Get-Date).AddDays(-$RetentionDays)
Get-ChildItem -Path $backupsDir -Filter "bds-backup-win-*.zip*" | Where-Object { $_.LastWriteTime -lt $limitDate } | ForEach-Object {
    Write-Host "[ROTACAO] Removendo backup antigo: $($_.Name)" -ForegroundColor Gray
    Remove-Item $_.FullName -Force
}
