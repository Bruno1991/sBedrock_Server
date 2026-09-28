<#
.SYNOPSIS
    Habilita isencao de isolamento de loopback para o Minecraft Bedrock no Windows.
.DESCRIPTION
    Executa a ferramenta oficial CheckNetIsolation da Microsoft para permitir
    que o jogo Minecraft instalado no mesmo computador se conecte ao servidor local
    em 127.0.0.1 / localhost sem ser bloqueado pela sandbox UWP.
#>

[CmdletBinding()]
param ()

$ErrorActionPreference = "Stop"

$packageFamilyName = "Microsoft.MinecraftUWP_8wekyb3d8bbwe"

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host " Configuracao de Isencao de Loopback UWP (CheckNetIsolation)" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan

Write-Host "[INFO] Adicionando isencao de rede para: $packageFamilyName..." -ForegroundColor Cyan

$process = Start-Process -FilePath "CheckNetIsolation.exe" -ArgumentList "LoopbackExempt -a -n=$packageFamilyName" -Wait -PassThru -NoNewWindow

if ($process.ExitCode -eq 0) {
    Write-Host "[SUCESSO] Isencao de loopback configurada com sucesso!" -ForegroundColor Green
    Write-Host "Agora o seu Minecraft no Windows conseguira conectar em '127.0.0.1' ou 'localhost' na porta 19132." -ForegroundColor Green
} else {
    Write-Host "[AVISO] CheckNetIsolation retornou codigo de saida: $($process.ExitCode)." -ForegroundColor Yellow
    Write-Host "Se o comando falhou por falta de privilegios, execute o PowerShell como Administrador." -ForegroundColor Yellow
}
