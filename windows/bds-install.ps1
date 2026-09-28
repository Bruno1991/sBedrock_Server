<#
.SYNOPSIS
    Instalacao e provisionamento automatizado do Bedrock Dedicated Server no Windows.
.DESCRIPTION
    Baixa o pacote oficial v1.26.52.3 da Mojang para Windows, valida o hash SHA-256,
    organiza o particionamento de versoes e dados persistentes e prepara o runtime.
#>

[CmdletBinding()]
param (
    [string]$ServerDir = "",
    [string]$Version = "1.26.52.3",
    [string]$ExpectedSha256 = "2c9b98d07d2504786996f2335980e88bd969b4a77514925e75471a1349995825"
)

$ErrorActionPreference = "Stop"

if (-not $ServerDir) {
    $ServerDir = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\server"))
}

$officialUrl = "https://www.minecraft.net/bedrockdedicatedserver/bin-win/bedrock-server-$Version.zip"

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host " Instalacao do Minecraft Bedrock Dedicated Server para Windows v$Version" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan

# 1. Criar estrutura de diretorios particionada
$versionsDir = "$ServerDir\versions"
$targetVerDir = "$versionsDir\$Version"
$dataDir = "$ServerDir\data"
$runtimeDir = "$ServerDir\runtime"
$downloadsDir = "$ServerDir\downloads"

$dirs = @(
    $versionsDir, $targetVerDir, $dataDir,
    "$dataDir\config", "$dataDir\worlds", "$dataDir\keys", "$dataDir\backups",
    $runtimeDir, $downloadsDir
)

foreach ($d in $dirs) {
    if (-not (Test-Path $d)) {
        New-Item -ItemType Directory -Force -Path $d | Out-Null
    }
}

# 2. Download do pacote oficial se necessario
$zipPath = "$downloadsDir\bedrock-server-$Version-win.zip"
$localZipInRoot = "$PSScriptRoot\..\bedrock-server-1.26.52.3-win.zip"

if (-not (Test-Path "$targetVerDir\bedrock_server.exe")) {
    if (Test-Path $localZipInRoot) {
        Write-Host "[INFO] Utilizando pacote ja baixado na raiz do projeto..." -ForegroundColor Yellow
        Copy-Item $localZipInRoot $zipPath -Force
    }

    if (-not (Test-Path $zipPath)) {
        Write-Host "[INFO] Baixando pacote oficial de: $officialUrl..." -ForegroundColor Cyan
        Invoke-WebRequest -Uri $officialUrl -Headers @{"User-Agent"="Mozilla/5.0 (Windows NT 10.0; Win64; x64)"} -OutFile $zipPath
    }

    # 3. Validacao criptografica SHA-256
    Write-Host "[INFO] Verificando hash SHA-256 do pacote baixado..." -ForegroundColor Cyan
    $actualHash = (Get-FileHash $zipPath -Algorithm SHA256).Hash.ToLower()

    if ($actualHash -ne $ExpectedSha256) {
        throw "FALHA DE INTEGRIDADE: O hash do arquivo ($actualHash) nao confere com o oficial esperado ($ExpectedSha256)!"
    }
    Write-Host "[INFO] Checksum verificado com sucesso ($actualHash)!" -ForegroundColor Green

    # 4. Extrair para diretorio de versao isolado
    Write-Host "[INFO] Extraindo binarios da versao $Version em $targetVerDir..." -ForegroundColor Cyan
    Expand-Archive -Path $zipPath -DestinationPath $targetVerDir -Force
} else {
    Write-Host "[INFO] Binario oficial v$Version ja instalado em: $targetVerDir" -ForegroundColor Green
}

# 5. Executar bds-config.ps1 para gerar server.properties e JSONs
& "$PSScriptRoot\bds-config.ps1" -ServerDir $ServerDir

# 6. Criar links de Junction para diretorios no runtime
function Setup-Junction([string]$source, [string]$destination) {
    if (Test-Path $destination) {
        # Se for junction ou symlink, remover o link sem deletar o conteudo original
        (Get-Item $destination).Delete()
    }
    New-Item -ItemType Junction -Path $destination -Target $source | Out-Null
    Write-Host "[INFO] Junction configurada: $(Split-Path $destination -Leaf) -> $source" -ForegroundColor Gray
}

Setup-Junction "$targetVerDir\definitions" "$runtimeDir\definitions"
Setup-Junction "$targetVerDir\resource_packs" "$runtimeDir\resource_packs"
Setup-Junction "$targetVerDir\behavior_packs" "$runtimeDir\behavior_packs"
Setup-Junction "$dataDir\worlds" "$runtimeDir\worlds"
Setup-Junction "$dataDir\keys" "$runtimeDir\keys"

# 7. Copiar executavel para o runtime
Copy-Item "$targetVerDir\bedrock_server.exe" "$runtimeDir\bedrock_server.exe" -Force

# Copiar DLLs / pdb se existirem na pasta de versao
Get-ChildItem -Path $targetVerDir -Filter "*.dll" | ForEach-Object {
    Copy-Item $_.FullName "$runtimeDir\$($_.Name)" -Force
}

# Registrar versao atual instalada
Set-Content -Path "$dataDir\current_version.txt" -Value $Version -Encoding UTF8

Write-Host "======================================================================" -ForegroundColor Green
Write-Host " [SUCESSO] Servidor Minecraft Bedrock v$Version instalado para Windows!" -ForegroundColor Green
Write-Host " Localizacao de execucao: $runtimeDir" -ForegroundColor Cyan
Write-Host " Para iniciar o servidor: .\windows\bds-start.ps1" -ForegroundColor Yellow
Write-Host " Para permitir conexao no mesmo PC: .\windows\enable-loopback.ps1" -ForegroundColor Yellow
Write-Host " Para liberar porta no firewall: .\windows\setup-firewall.ps1" -ForegroundColor Yellow
Write-Host "======================================================================" -ForegroundColor Green
