<#
.SYNOPSIS
    Configuracao de regras do Firewall do Windows Defender para o Bedrock Dedicated Server.
.DESCRIPTION
    Cria regras de entrada para as portas UDP 19132 e 19133, permitindo que outros
    dispositivos na mesma rede local (celulares Android, consoles Xbox e outros PCs)
    se conectem ao servidor BDS hospedado nesta maquina Windows.
#>

[CmdletBinding()]
param (
    [int[]]$Ports = @(19132, 19133)
)

$ErrorActionPreference = "Stop"

$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host " Configuracao do Firewall do Windows Defender para Minecraft Bedrock" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan

if (-not $isAdmin) {
    Write-Host "[AVISO] Criar regras de firewall requer permissoes de Administrador." -ForegroundColor Yellow
    Write-Host "Por favor, abra um PowerShell como Administrador e execute este script:" -ForegroundColor Yellow
    Write-Host "  powershell -ExecutionPolicy Bypass -File .\windows\setup-firewall.ps1" -ForegroundColor White
    return
}

$ruleName = "Minecraft Bedrock Server (UDP-In)"

# Remover regra anterior se ja existir para evitar duplicatas
Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue | Remove-NetFirewallRule

Write-Host "[INFO] Criando regra de firewall: '$ruleName' para portas $($Ports -join ', ') UDP..." -ForegroundColor Cyan

New-NetFirewallRule -DisplayName $ruleName `
    -Direction Inbound `
    -Protocol UDP `
    -LocalPort ($Ports | ForEach-Object { "$_" }) `
    -Action Allow `
    -Description "Permite conexoes locais para o Minecraft Bedrock Dedicated Server (BDS)" | Out-Null

Write-Host "[SUCESSO] Regra de firewall configurada com exito!" -ForegroundColor Green
Write-Host "Dispositivos Android e Xbox na mesma rede Wi-Fi agora podem conectar no IP local deste computador." -ForegroundColor Green
