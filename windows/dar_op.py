"""
Gerenciador de Operadores (OP) para Minecraft Bedrock Dedicated Server (BDS).

Permite conceder e gerenciar privilegios de Operador para amigos no servidor:
1. Em tempo real (Live): Envia comando 'op <gamertag>' via console IPC.
2. Persistente (Offline/Permissions): Registra o XUID em permissions.json.
3. Lista de Amigos: Le o arquivo amigos_operadores.txt para promover em lote ou automaticamente.
4. Sentinela (--watch): Monitora entradas de jogadores e concede OP automaticamente aos amigos.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

# Ajuste de sys.path para imports locais em windows/
WINDOWS_DIR = Path(__file__).resolve().parent
if str(WINDOWS_DIR) not in sys.path:
    sys.path.insert(0, str(WINDOWS_DIR))

try:
    from bds_cmd import get_bds_pid, send_command
except ImportError:
    get_bds_pid = lambda: None
    send_command = lambda cmd, wait_ms=50: False

# ======================================================================
# CAMINHOS DO PROJETO
# ======================================================================

PROJECT_ROOT = WINDOWS_DIR.parent
SERVER_DIR = PROJECT_ROOT / "server"
RUNTIME_DIR = SERVER_DIR / "runtime"
DATA_CONFIG_DIR = SERVER_DIR / "data" / "config"

PERMISSIONS_RUNTIME = RUNTIME_DIR / "permissions.json"
PERMISSIONS_DATA = DATA_CONFIG_DIR / "permissions.json"
LAST_RUN_LOG = SERVER_DIR / "last_run.log"
FRIENDS_FILE = WINDOWS_DIR / "amigos_operadores.txt"


# ======================================================================
# FUNCOES DE SUPORTE E LEITURA
# ======================================================================

def load_permissions() -> list[dict]:
    """Le o arquivo permissions.json do runtime."""
    if not PERMISSIONS_RUNTIME.exists():
        return []
    try:
        content = PERMISSIONS_RUNTIME.read_text(encoding="utf-8")
        data = json.loads(content)
        if isinstance(data, list):
            return data
    except Exception:
        pass
    return []


def save_permissions(data: list[dict]):
    """Salva a lista de permissoes em runtime e em data/config."""
    content = json.dumps(data, indent=2)

    PERMISSIONS_RUNTIME.parent.mkdir(parents=True, exist_ok=True)
    PERMISSIONS_RUNTIME.write_text(content, encoding="utf-8")

    if DATA_CONFIG_DIR.exists():
        PERMISSIONS_DATA.write_text(content, encoding="utf-8")


def load_known_players_from_logs() -> dict[str, str]:
    """
    Extrai mapeamento {gamertag_lowercase: xuid} a partir dos logs do BDS.
    Examina o log em busca de padroes como:
    'Player connected: <gamertag>, xuid: <xuid>'
    """
    mapping: dict[str, str] = {}
    if not LAST_RUN_LOG.exists():
        return mapping

    try:
        raw = ""
        try:
            raw = LAST_RUN_LOG.read_text(encoding="utf-16le", errors="ignore")
        except Exception:
            raw = LAST_RUN_LOG.read_text(encoding="utf-8", errors="ignore")

        pattern = re.compile(r"Player connected:\s*([^,\r\n]+),\s*xuid:\s*(\d+)", re.IGNORECASE)
        for match in pattern.finditer(raw):
            gt = match.group(1).strip()
            xuid = match.group(2).strip()
            mapping[gt.lower()] = xuid
    except Exception:
        pass

    return mapping


def load_friends_list() -> list[str]:
    """Carrega a lista de amigos cadastrados em amigos_operadores.txt."""
    if not FRIENDS_FILE.exists():
        return []
    friends: list[str] = []
    for raw in FRIENDS_FILE.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        friends.append(line)
    return friends


def add_friend_to_file(gamertag: str) -> bool:
    """Adiciona um novo gamertag ao arquivo amigos_operadores.txt se ainda nao constar."""
    current = load_friends_list()
    if any(f.lower() == gamertag.lower() for f in current):
        return False

    with open(FRIENDS_FILE, "a", encoding="utf-8") as f:
        f.write(f"{gamertag}\n")
    return True


# ======================================================================
# ACOES DE OPERADOR
# ======================================================================

def give_op(gamertag: str) -> bool:
    """
    Concede status de operador para o jogador:
    - Se o servidor estiver rodando, envia 'op <gamertag>' via console.
    - Se encontrar o XUID conhecido, garante persistencia em permissions.json.
    """
    gamertag = gamertag.strip()
    if not gamertag:
        return False

    pid = get_bds_pid()
    print(f"\n[OP] Concedendo privilegios de Operador para: '{gamertag}'...")

    if pid:
        print(f"     -> Servidor BDS ativo (PID: {pid}). Enviando comando ao console...")
        send_command(f"op {gamertag}")
        send_command(f'say [BDS] O jogador {gamertag} agora e Operador do servidor!')
        print(f"     [OK] Comando 'op {gamertag}' injetado no console do BDS!")
    else:
        print("     -> Servidor BDS esta offline no momento.")

    # Tentativa de persistencia direta no permissions.json
    known = load_known_players_from_logs()
    xuid = known.get(gamertag.lower())

    if xuid:
        perms = load_permissions()
        exists = any(item.get("xuid") == xuid and item.get("permission") == "operator" for item in perms)
        if not exists:
            perms.append({"permission": "operator", "xuid": xuid})
            save_permissions(perms)
            print(f"     [OK] XUID {xuid} registrado com sucesso em permissions.json!")
        else:
            print(f"     [INFO] XUID {xuid} ja consta como operador em permissions.json.")
    else:
        added = add_friend_to_file(gamertag)
        if added:
            print(f"     [INFO] Gamertag '{gamertag}' salvo em amigos_operadores.txt (Sera promovido ao entrar).")

    return True


def remove_op(gamertag_or_xuid: str) -> bool:
    """Remove status de operador do jogador."""
    target = gamertag_or_xuid.strip()
    if not target:
        return False

    pid = get_bds_pid()
    print(f"\n[DEOP] Removendo privilegios de Operador de: '{target}'...")

    if pid:
        send_command(f"deop {target}")
        send_command(f'say [BDS] Privilegios de Operador de {target} foram revogados.')
        print(f"     [OK] Comando 'deop {target}' enviado ao console.")

    known = load_known_players_from_logs()
    xuid = known.get(target.lower(), target if target.isdigit() else None)

    if xuid:
        perms = load_permissions()
        initial_len = len(perms)
        perms = [p for p in perms if p.get("xuid") != xuid]
        if len(perms) < initial_len:
            save_permissions(perms)
            print(f"     [OK] XUID {xuid} removido de permissions.json.")

    return True


def list_operators():
    """Exibe todos os operadores cadastrados e amigos configurados."""
    perms = load_permissions()
    known = load_known_players_from_logs()
    xuid_to_name = {xuid: gt for gt, xuid in known.items()}

    print()
    print("=" * 68)
    print("           OPERADORES DO BEDROCK DEDICATED SERVER")
    print("=" * 68)

    pid = get_bds_pid()
    status_str = f"ONLINE (PID: {pid})" if pid else "OFFLINE"
    print(f"Status do Servidor: {status_str}")
    print()

    print("1. Operadores ativos no permissions.json:")
    if perms:
        for idx, item in enumerate(perms, 1):
            xuid = item.get("xuid", "desconhecido")
            role = item.get("permission", "operator")
            name = xuid_to_name.get(xuid, "Desconhecido")
            print(f"   [{idx}] {name} (XUID: {xuid}) - Nivel: {role}")
    else:
        print("   (Nenhum operador registrado no arquivo)")

    print()
    print("2. Lista de amigos em amigos_operadores.txt:")
    friends = load_friends_list()
    if friends:
        for idx, f in enumerate(friends, 1):
            xuid = known.get(f.lower(), "XUID pendente (primeiro acesso)")
            print(f"   [{idx}] {f} -> {xuid}")
    else:
        print("   (Nenhum amigo na lista)")
    print("=" * 68)
    print()


def sync_all_friends():
    """Promove todos os amigos da lista amigos_operadores.txt."""
    friends = load_friends_list()
    if not friends:
        print("[AVISO] Nenhum amigo encontrado em amigos_operadores.txt.")
        return

    print(f"\n[SYNC] Sincronizando {len(friends)} amigos da lista...")
    for f in friends:
        give_op(f)


def watch_connections(interval_sec: float = 2.0):
    """
    Modo Sentinela: Monitora a conexao de novos jogadores em tempo real
    e concede OP automaticamente aos amigos cadastrados.
    """
    pid = get_bds_pid()
    if not pid:
        print("[ERRO] O servidor BDS precisa estar rodando para ativar o modo Sentinela!")
        print("Inicie o servidor primeiro com: .\\iniciar-servidor.bat")
        sys.exit(1)

    print()
    print("=" * 68)
    print("        SENTINELA AUTO-OP ATIVADO (BDS RUNNING)")
    print("=" * 68)
    print("Monitorando conexoes de amigos cadastrados...")
    print("Pressione Ctrl+C para encerrar o monitor.")
    print("=" * 68)
    print()

    friends = [f.lower() for f in load_friends_list()]
    promoted: set[str] = set()

    try:
        while True:
            if not get_bds_pid():
                print("\n[SENTINELA] O servidor BDS foi encerrado. Finalizando sentinela.")
                break

            known = load_known_players_from_logs()
            current_friends = [f.lower() for f in load_friends_list()]

            for gt, xuid in known.items():
                if gt in current_friends and gt not in promoted:
                    print(f"\n[SENTINELA] Amigo detectado: {gt} (XUID: {xuid})!")
                    give_op(gt)
                    promoted.add(gt)

            time.sleep(interval_sec)
    except KeyboardInterrupt:
        print("\n[SENTINELA] Monitor encerrado pelo usuario.")


# ======================================================================
# MENU INTERATIVO
# ======================================================================

def interactive_menu():
    while True:
        list_operators()
        print("Escolha uma opcao:")
        print("  [1] Dar OP para um amigo agora (digitar o Gamertag)")
        print("  [2] Adicionar amigo na lista amigos_operadores.txt")
        print("  [3] Sincronizar todos os amigos da lista agora")
        print("  [4] Remover OP de um jogador")
        print("  [5] Ativar modo Sentinela Auto-OP (aguarda amigos entrarem)")
        print("  [0] Sair")
        print()

        try:
            choice = input("Opcao: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if choice == "1":
            gt = input("\nDigite o Gamertag do amigo (nome exato no Xbox/Minecraft): ").strip()
            if gt:
                give_op(gt)
            input("\nPressione Enter para continuar...")
        elif choice == "2":
            gt = input("\nDigite o Gamertag do amigo para adicionar na lista permanente: ").strip()
            if gt:
                if add_friend_to_file(gt):
                    print(f"[OK] '{gt}' adicionado a amigos_operadores.txt!")
                    give_op(gt)
                else:
                    print(f"[INFO] '{gt}' ja esta na lista.")
            input("\nPressione Enter para continuar...")
        elif choice == "3":
            sync_all_friends()
            input("\nPressione Enter para continuar...")
        elif choice == "4":
            tgt = input("\nDigite o Gamertag ou XUID do jogador a remover: ").strip()
            if tgt:
                remove_op(tgt)
            input("\nPressione Enter para continuar...")
        elif choice == "5":
            watch_connections()
            break
        elif choice in ("0", "sair", "exit", "q"):
            print("\nEncerrando...")
            break
        else:
            print("\nOpcao invalida. Tente novamente.")
            time.sleep(1)


# ======================================================================
# PONTO DE ENTRADA
# ======================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Gerenciador de Privilegios de Operador (OP) para Bedrock Dedicated Server."
    )
    parser.add_argument(
        "players",
        nargs="*",
        help="Gamertags dos jogadores para receber privilégios de Operador.",
    )
    parser.add_argument(
        "--remove",
        action="store_true",
        help="Remove o status de operador do(s) jogador(es) especificado(s).",
    )
    parser.add_argument(
        "--sync",
        action="store_true",
        help="Concede OP a todos os amigos cadastrados em amigos_operadores.txt.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Exibe a lista de operadores cadastrados.",
    )
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Modo Sentinela: Monitora entradas e da OP automaticamente quando amigos entrarem.",
    )

    args = parser.parse_args()

    if args.watch:
        watch_connections()
    elif args.sync:
        sync_all_friends()
    elif args.list:
        list_operators()
    elif args.players:
        for p in args.players:
            if args.remove:
                remove_op(p)
            else:
                give_op(p)
    else:
        interactive_menu()


if __name__ == "__main__":
    main()
