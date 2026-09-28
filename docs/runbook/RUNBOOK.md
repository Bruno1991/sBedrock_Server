<!--
Responsabilidade: Guia de operacao diaria (Runbook) do Bedrock Dedicated Server no Proxmox LXC.
Instrucoes passo a passo para instalacao, configuracao de firewall, gerenciamento de jogadores,
execucao de backups, recuperacao de desastres, atualizacoes e diagnostico de falhas.
-->

# Runbook de Operação: Bedrock Dedicated Server (BDS) no Proxmox LXC

## 1. Pré-Requisitos e Criação do Container no Proxmox VE

Para manter o consumo equilibrado com os ~12 GB de RAM compartilhados do host, configure o container LXC com as seguintes especificações recomendadas:

| Recurso | Especificação Recomendada | Observações |
| :--- | :--- | :--- |
| **Tipo de Container** | LXC Não Privilegiado (`unprivileged`) | Segurança máxima; sem necessidade de hacks de `nesting`. |
| **Distribuição** | Ubuntu 22.04 LTS ou 24.04 LTS | Suporte oficial declarado no manual `bedrock_server_how_to.html`. |
| **vCPU** | 2 a 4 núcleos | Suficiente para ticks estáveis a 20 TPS com até 10 jogadores. |
| **Memória RAM** | 3.072 MB (3 GB) a 4.096 MB (4 GB) | O processo consome ~1-2 GB com chunks ativos em 20 de view-distance. |
| **Swap** | 1.024 MB (1 GB) | Previne acionamento agressivo do OOM-killer. |
| **Armazenamento** | 20 GB a 30 GB (ext4 ou ZFS) | Espaço para o banco LevelDB e rotação de backups (14 dias). |
| **Rede** | Modo Bridge (`vmbr0`), IPv4 estático ou DHCP fixado | Exemplo: `192.168.1.50/24`, Gateway: `192.168.1.1`. |

---

## 2. Procedimento de Instalação e Ativação

Acesse o terminal do container LXC via Proxmox Console ou SSH:

```bash
# 1. Clonar ou transferir o repositório para o container
cd /tmp
git clone <URL_DO_REPOSITORIO> s_Bedrock_Server
cd s_Bedrock_Server

# 2. Executar o provisionamento automatizado idempotente como root
sudo ./scripts/bds-install.sh

# 3. Configurar e reforçar as regras de firewall UFW
sudo ./firewall/setup-firewall.sh

# 4. Habilitar e iniciar o serviço do servidor BDS
sudo systemctl enable --now minecraft-bedrock

# 5. Habilitar o temporizador de backup a quente diário
sudo systemctl enable --now minecraft-bedrock-backup.timer

# 6. Executar o smoke test para confirmar a saúde operacional
bds-healthcheck
```

---

## 3. Guia de Operação Diária

### 3.1. Gerenciamento da Allowlist (Controle de Acesso)
O servidor opera por padrão com `allow-list=true` para proteção contra acessos não autorizados.

- **Adicionar jogador via console**:
  ```bash
  bds-cmd "allowlist add \"NomeDoGamertag\""
  ```
- **Remover jogador via console**:
  ```bash
  bds-cmd "allowlist remove \"NomeDoGamertag\""
  ```
- **Listar jogadores autorizados**:
  ```bash
  bds-cmd "allowlist list"
  ```
- **Edição direta em arquivo**:
  Edite `/opt/bds/data/config/allowlist.json` e aplique a alteração imediatamente sem reiniciar o servidor:
  ```bash
  bds-cmd "allowlist reload"
  ```

### 3.2. Gerenciamento de Operadores e Permissões
- **Promover jogador a Operador**:
  ```bash
  bds-cmd "op NomeDoGamertag"
  ```
- **Rebaixar jogador para Membro comum**:
  ```bash
  bds-cmd "deop NomeDoGamertag"
  ```
- **Recarregar arquivo de permissões**:
  ```bash
  bds-cmd "permission reload"
  ```

### 3.3. Acesso ao Console Interativo
Para interagir diretamente com o console do BDS (digitar comandos com autocompletar ou monitorar eventos ao vivo):
```bash
bds-console
```
> [!IMPORTANT]
> Para sair do console interativo sem encerrar o servidor, pressione sequencialmente:
> `Ctrl + B`, solte as teclas e pressione `D` (Detach).

---

## 4. Manutenção, Backups e Recuperação

### 4.1. Backup a Quente Manual
O backup pode ser disparado a qualquer momento sem desconectar jogadores:
```bash
bds-backup
```
O arquivo compactado `.tar.gz` e o `.sha256` serão gerados em `/opt/bds/data/backups/`.

### 4.2. Recuperação de Desastres (Restaurar Mundo)
Caso o mundo seja corrompido ou sofra griefing:
```bash
# 1. Listar backups disponíveis
ls -lh /opt/bds/data/backups/

# 2. Executar a restauração (o script cuida da parada, isolamento e validação de hash)
bds-restore bds-backup-20260928_040000.tar.gz

# 3. Validar a saúde do servidor restaurado
bds-healthcheck
```

### 4.3. Atualização de Versão do BDS
Quando a Mojang lançar uma nova versão:
```bash
# Executa backup prévio, baixa a nova versão, reatribui links e testa saúde
bds-update

# Se o smoke test falhar, o rollback é acionado automaticamente.
```

### 4.4. Rollback Manual de Versão
Caso seja necessário forçar o retorno para a versão anterior:
```bash
bds-rollback
```

---

## 5. Diagnóstico de Falhas e Logs

| Sintoma | Ação Recomendada |
| :--- | :--- |
| **Serviço não sobe (`failed`)** | Verificar logs do systemd: `journalctl -u minecraft-bedrock -n 50 --no-pager` |
| **Jogadores não conseguem conectar via LAN** | Confirmar regras de firewall: `sudo ufw status`. Confirmar que o processo está escutando na porta 19132: `ss -ulpn \| grep 19132`. |
| **Console Xbox não visualiza o servidor** | Verificar se o Xbox está na mesma sub-rede L2 do container LXC. Em caso de restrição de Wi-Fi/switch, consultar as opções de relay no documento [NETWORKING.md](file:///C:/dev/s_Bedrock_Server/docs/architecture/NETWORKING.md). |
| **Erro "Outdated Server" no cliente** | O jogo atualizou no celular/PC; execute `bds-update` no servidor para acompanhar a versão oficial. |
