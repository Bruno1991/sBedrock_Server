<#
.SYNOPSIS
    Geracao e validacao deterministica das configuracoes do Bedrock Dedicated Server (BDS) para Windows.
.DESCRIPTION
    Le o template server.properties.template e substitui as variaveis com base no arquivo .env
    ou variaveis de ambiente, validando valores permitidos de acordo com a documentacao oficial v1.26.52.3.
#>

[CmdletBinding()]
param (
    [string]$ServerDir = "",
    [string]$TemplateDir = "",
    [string]$EnvFile = ""
)

$ErrorActionPreference = "Stop"

if (-not $ServerDir) {
    $ServerDir = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\server"))
}
if (-not $TemplateDir) {
    $TemplateDir = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\templates"))
}
if (-not $EnvFile) {
    $EnvFile = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\.env"))
}

Write-Host "[INFO] Iniciando geracao de configuracoes do BDS para Windows..." -ForegroundColor Cyan

# 1. Carregar arquivo .env caso exista
if (Test-Path $EnvFile) {
    Write-Host "[INFO] Carregando definicoes de: $EnvFile" -ForegroundColor Cyan
    Get-Content $EnvFile | ForEach-Object {
        $line = $_.Trim()
        if ($line -and -not $line.StartsWith("#") -and $line.Contains("=")) {
            $key, $value = $line.Split("=", 2)
            $key = $key.Trim()
            $value = $value.Trim()
            # Remover aspas se presentes
            if ($value.StartsWith('"') -and $value.EndsWith('"')) {
                $value = $value.Substring(1, $value.Length - 2)
            }
            [System.Environment]::SetEnvironmentVariable($key, $value, "Process")
        }
    }
}

# 2. Diretorios de destino
$configDir = "$ServerDir\data\config"
$runtimeDir = "$ServerDir\runtime"
New-Item -ItemType Directory -Force -Path $configDir | Out-Null
New-Item -ItemType Directory -Force -Path $runtimeDir | Out-Null

# 3. Definir variaveis com valores padrao auditados (v1.26.52.3)
function Get-EnvOrDefault([string]$name, [string]$default) {
    $val = [System.Environment]::GetEnvironmentVariable($name, "Process")
    if ([string]::IsNullOrWhiteSpace($val)) { return $default }
    return $val
}

$BDS_SERVER_NAME = Get-EnvOrDefault "BDS_SERVER_NAME" "Bedrock Dedicated Server"
$BDS_GAMEMODE = Get-EnvOrDefault "BDS_GAMEMODE" "survival"
$BDS_FORCE_GAMEMODE = Get-EnvOrDefault "BDS_FORCE_GAMEMODE" "false"
$BDS_DIFFICULTY = Get-EnvOrDefault "BDS_DIFFICULTY" "normal"
$BDS_ALLOW_CHEATS = Get-EnvOrDefault "BDS_ALLOW_CHEATS" "false"
$BDS_MAX_PLAYERS = Get-EnvOrDefault "BDS_MAX_PLAYERS" "10"
$BDS_ONLINE_MODE = Get-EnvOrDefault "BDS_ONLINE_MODE" "true"
$BDS_ALLOW_LIST = Get-EnvOrDefault "BDS_ALLOW_LIST" "true"
$BDS_DEFAULT_PLAYER_PERMISSION = Get-EnvOrDefault "BDS_DEFAULT_PLAYER_PERMISSION" "member"
$BDS_TRANSPORT = Get-EnvOrDefault "BDS_TRANSPORT" "raknet"
$BDS_SERVER_PORT = Get-EnvOrDefault "BDS_SERVER_PORT" "19132"
$BDS_SERVER_PORT_V6 = Get-EnvOrDefault "BDS_SERVER_PORT_V6" "19133"
$BDS_ENABLE_LAN_VISIBILITY = Get-EnvOrDefault "BDS_ENABLE_LAN_VISIBILITY" "true"
$BDS_VIEW_DISTANCE = Get-EnvOrDefault "BDS_VIEW_DISTANCE" "20"
$BDS_TICK_DISTANCE = Get-EnvOrDefault "BDS_TICK_DISTANCE" "4"
$BDS_MAX_THREADS = Get-EnvOrDefault "BDS_MAX_THREADS" "4"
$BDS_PLAYER_IDLE_TIMEOUT = Get-EnvOrDefault "BDS_PLAYER_IDLE_TIMEOUT" "30"
$BDS_LEVEL_NAME = Get-EnvOrDefault "BDS_LEVEL_NAME" "Bedrock level"
$BDS_LEVEL_SEED = Get-EnvOrDefault "BDS_LEVEL_SEED" ""
$BDS_TEXTUREPACK_REQUIRED = Get-EnvOrDefault "BDS_TEXTUREPACK_REQUIRED" "false"
$BDS_ENABLE_PACKET_LIMITER = Get-EnvOrDefault "BDS_ENABLE_PACKET_LIMITER" "true"

# 4. Validacoes estritas de conformidade oficial
if ($BDS_GAMEMODE -notin @("survival", "creative", "adventure")) {
    throw "Valor invalido para gamemode: '$BDS_GAMEMODE'. Permitidos: survival, creative, adventure"
}
if ($BDS_DIFFICULTY -notin @("peaceful", "easy", "normal", "hard")) {
    throw "Valor invalido para difficulty: '$BDS_DIFFICULTY'. Permitidas: peaceful, easy, normal, hard"
}
if ($BDS_TRANSPORT -notin @("raknet", "nethernet")) {
    throw "Valor invalido para transport: '$BDS_TRANSPORT'. Permitidos: raknet, nethernet"
}
if ([int]$BDS_SERVER_PORT -lt 1 -or [int]$BDS_SERVER_PORT -gt 65535) {
    throw "server-port fora do intervalo [1-65535]: $BDS_SERVER_PORT"
}
if ([int]$BDS_VIEW_DISTANCE -lt 5) {
    throw "view-distance deve ser >= 5: $BDS_VIEW_DISTANCE"
}
if ([int]$BDS_TICK_DISTANCE -lt 4 -or [int]$BDS_TICK_DISTANCE -gt 12) {
    throw "tick-distance deve estar no intervalo [4-12]: $BDS_TICK_DISTANCE"
}

# 5. Processar template server.properties
$templateFile = "$TemplateDir\server.properties.template"
if (-not (Test-Path $templateFile)) {
    throw "Template nao encontrado em: $templateFile"
}

$rawTemplate = Get-Content $templateFile -Raw -Encoding UTF8

$substitutions = @{
    "BDS_SERVER_NAME" = $BDS_SERVER_NAME
    "BDS_GAMEMODE" = $BDS_GAMEMODE
    "BDS_FORCE_GAMEMODE" = $BDS_FORCE_GAMEMODE
    "BDS_DIFFICULTY" = $BDS_DIFFICULTY
    "BDS_ALLOW_CHEATS" = $BDS_ALLOW_CHEATS
    "BDS_MAX_PLAYERS" = $BDS_MAX_PLAYERS
    "BDS_ONLINE_MODE" = $BDS_ONLINE_MODE
    "BDS_ALLOW_LIST" = $BDS_ALLOW_LIST
    "BDS_DEFAULT_PLAYER_PERMISSION" = $BDS_DEFAULT_PLAYER_PERMISSION
    "BDS_TRANSPORT" = $BDS_TRANSPORT
    "BDS_SERVER_PORT" = $BDS_SERVER_PORT
    "BDS_SERVER_PORT_V6" = $BDS_SERVER_PORT_V6
    "BDS_ENABLE_LAN_VISIBILITY" = $BDS_ENABLE_LAN_VISIBILITY
    "BDS_VIEW_DISTANCE" = $BDS_VIEW_DISTANCE
    "BDS_TICK_DISTANCE" = $BDS_TICK_DISTANCE
    "BDS_MAX_THREADS" = $BDS_MAX_THREADS
    "BDS_PLAYER_IDLE_TIMEOUT" = $BDS_PLAYER_IDLE_TIMEOUT
    "BDS_LEVEL_NAME" = $BDS_LEVEL_NAME
    "BDS_LEVEL_SEED" = $BDS_LEVEL_SEED
    "BDS_TEXTUREPACK_REQUIRED" = $BDS_TEXTUREPACK_REQUIRED
    "BDS_ENABLE_PACKET_LIMITER" = $BDS_ENABLE_PACKET_LIMITER
}

$rendered = $rawTemplate
foreach ($key in $substitutions.Keys) {
    $val = $substitutions[$key]
    # Substituir padrao ${VAR:-DEFAULT} e ${VAR}
    $rendered = [System.Text.RegularExpressions.Regex]::Replace($rendered, "\$\{" + $key + "(:-[^}]*)?\}", $val)
}

# Gravar nos destinos de config e runtime
$destFile1 = "$configDir\server.properties"
$destFile2 = "$runtimeDir\server.properties"

[System.IO.File]::WriteAllText($destFile1, $rendered, [System.Text.Encoding]::UTF8)
[System.IO.File]::WriteAllText($destFile2, $rendered, [System.Text.Encoding]::UTF8)

# 6. Copiar templates JSON se nao existirem
function Copy-JsonTemplateIfMissing([string]$fileName) {
    $src = "$TemplateDir\$fileName.template"
    $dstConfig = "$configDir\$fileName"
    $dstRuntime = "$runtimeDir\$fileName"

    if (-not (Test-Path $dstConfig)) {
        if (Test-Path $src) {
            Copy-Item $src $dstConfig -Force
            Write-Host "[INFO] Inicializado: $fileName" -ForegroundColor Gray
        } else {
            "[]" | Out-File -FilePath $dstConfig -Encoding UTF8
        }
    }
    # Sempre sincronizar para o runtime se ausente
    if (-not (Test-Path $dstRuntime)) {
        Copy-Item $dstConfig $dstRuntime -Force
    }
}

Copy-JsonTemplateIfMissing "allowlist.json"
Copy-JsonTemplateIfMissing "permissions.json"
Copy-JsonTemplateIfMissing "packetlimitconfig.json"

Write-Host "[SUCESSO] Configuracoes geradas e validadas com sucesso em $configDir e $runtimeDir" -ForegroundColor Green
