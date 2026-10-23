<#
.SYNOPSIS
    Envia comandos diretamente para o Bedrock Dedicated Server no Windows.
.DESCRIPTION
    Wrapper PowerShell para windows/bds_cmd.py que injeta comandos no console do BDS via Win32 API.
#>

[CmdletBinding()]
param (
    [Parameter(Mandatory = $true, Position = 0, ValueFromRemainingArguments = $true)]
    [string[]]$Command
)

$cmdText = $Command -join " "
$scriptPy = Join-Path $PSScriptRoot "bds_cmd.py"

python $scriptPy $cmdText
