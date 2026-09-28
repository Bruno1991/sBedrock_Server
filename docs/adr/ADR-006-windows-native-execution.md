<!--
Responsabilidade: Decisao de arquitetura para execucao nativa do BDS no sistema operacional Windows.
Detalha os requisitos de sistema (Windows 10/11), tratamento de isolamento de loopback UWP (CheckNetIsolation),
regras do Firewall do Windows Defender e desacoplamento de runtime via NTFS HardLinks e Junctions.
-->
---
document_id: adr-006-windows-native-execution
title: Execucao Nativa do Bedrock Dedicated Server no Windows 10/11
document_type: adr
status: proposed
version: 1.0.0
language: pt-BR
owners: [architecture-maintainers]
last_updated: "2026-09-28"
review_cycle_days: 365
license: MIT
---

# ADR-006: Execução Nativa do BDS no Windows 10/11

## Estado

`proposed` — 2026-09-28 — Decisores: Equipe de Engenharia / Mantenedor do Projeto.

## Contexto

Embora o projeto tenha sido inicialmente especificado com foco em container LXC Proxmox, o operador solicitou a execução direta no ambiente de desenvolvimento local (Windows 10/11 x64).

A distribuição oficial da Mojang disponibiliza um pacote nativo para Windows:
- **Download Oficial**: `https://www.minecraft.net/bedrockdedicatedserver/bin-win/bedrock-server-1.26.52.3.zip`
- **Requisitos Oficiais**: Windows 10 versão 1703+ ou Windows Server 2016+ (x64).
- **Binário Central**: `bedrock_server.exe`.

Desafios específicos da plataforma Windows:
1. **Isolamento de Loopback UWP (Universal Windows Platform)**:
   O aplicativo cliente do Minecraft Bedrock no Windows roda em sandbox UWP. Por padrão de segurança do Windows, aplicações UWP são proibidas de se conectar a endereços de loopback (`127.0.0.1` ou `localhost`). Sem uma isenção explícita de loopback, o jogador não consegue conectar ao servidor rodando na mesma máquina.
   A solução oficial documentada pela Microsoft é:
   `CheckNetIsolation.exe LoopbackExempt -a -n=Microsoft.MinecraftUWP_8wekyb3d8bbwe`
2. **Firewall do Windows Defender**:
   Para que clientes na rede local (celulares Android, consoles Xbox e outros computadores) alcancem o servidor, a porta `19132/udp` (e opcionalmente `19133/udp`) deve ser liberada nas regras de entrada do Windows Defender Firewall.
3. **Links Simbólicos no NTFS**:
   Links simbólicos padrão (`symlink`) no Windows exigem privilégios elevados de Administrador ou Modo Desenvolvedor ativo. Para contornar essa restrição sem comprometer o desacoplamento de versões (ADR-003), a implementação no Windows adota **NTFS Junctions** (`New-Item -ItemType Junction`) para diretórios e **NTFS HardLinks** (`New-Item -ItemType HardLink`) para arquivos individuais, permitindo operação sem necessidade de privilégios administrativos.

## Decisão

Adotar a **Arquitetura Dual-Platform (Linux/Proxmox + Windows Nativo)**:
- Manter todos os scripts e units Linux/Proxmox em `scripts/`, `systemd/` e `firewall/` para futura migração ou publicação em container.
- Implementar o conjunto completo de automação em PowerShell no diretório `windows/`:
  - `bds-install.ps1`: Download do pacote Windows v1.26.52.3, verificação de hash SHA-256 e montagem do layout.
  - `bds-config.ps1`: Geração e validação de `server.properties` e arquivos JSON a partir dos templates.
  - `bds-start.ps1`: Inicialização do servidor com console interativo visível para o operador.
  - `enable-loopback.ps1`: Execução do `CheckNetIsolation.exe` para permitir conexão no mesmo PC.
  - `setup-firewall.ps1`: Configuração automatizada de regras no Windows Defender Firewall.
  - `bds-backup.ps1`: Procedimento de backup e compressão de mundos.
  - `bds-healthcheck.ps1`: Verificação de processo ativo e socket UDP de rede.

## Consequências

- **Efeitos Positivos**:
  - O operador pode rodar e jogar imediatamente em sua máquina Windows sem depender de VM ou container externo.
  - Clientes externos na mesma rede local (Android, Xbox) conseguem se conectar normalmente através do IP local da máquina Windows.
  - O repositório permanece 100% interoperável para ambos os sistemas operacionais.
- **Efeitos Negativos**:
  - Requer manutenção de scripts em Bash (para Linux) e PowerShell (para Windows).

## Referências

- Documentação Oficial BDS: `bedrock_server_how_to.html` (v1.26.52.3) - Seção *Platforms -> Windows*.
- Documentação Microsoft Learn: [CheckNetIsolation Utility](https://learn.microsoft.com/windows/security/operating-system-security/network-security/windows-firewall/configure-network-isolation-for-windows-store-apps).
- Hash SHA-256 Oficial do Pacote Windows: `2c9b98d07d2504786996f2335980e88bd969b4a77514925e75471a1349995825`.
