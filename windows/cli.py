"""Canivete Suíço Universal do Minecraft Bedrock Server (s_Bedrock_Server).

Interface unificada e centralizada de controle para:
- Iniciar o servidor Bedrock no Windows
- Gerenciar o mod CobbleDrock (ativar / desativar / status dos packs)
- Conceder permissões de Operador a jogadores e amigos
- Resetar mundo / criar mapa limpo de testes
- Habilitar conexão local (UWP Loopback Exemption)
- Configurar regras de firewall do Windows
- Status e monitoramento do servidor
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

WINDOWS_DIR = Path(__file__).resolve().parent
ROOT_DIR = WINDOWS_DIR.parent
SERVER_DIR = ROOT_DIR / "server"


def start_server():
    """Inicia o servidor Bedrock."""
    exe_path = SERVER_DIR / "bedrock_server.exe"
    if not exe_path.is_file():
        print(f"[!] Executável não encontrado em: {exe_path}")
        print("    Execute primeiro a instalação/extração do servidor.")
        return

    print("\n" + "=" * 65)
    print("      ⛏ MINECRAFT BEDROCK SERVER: INICIANDO SERVIDOR ⛏")
    print("=" * 65)
    print(" [*] Porta Padrão: 19132 (IPv4) / 19133 (IPv6)")
    print(" [*] Pressione CTRL+C no console para parar com segurança.\n")
    try:
        subprocess.run([str(exe_path)], cwd=str(SERVER_DIR))
    except KeyboardInterrupt:
        print("\n[*] Servidor encerrado.")


def manage_cobbledrock(action: str = "status"):
    """Gerencia CobbleDrock."""
    script = WINDOWS_DIR / "gerenciar_cobbledrock.py"
    cmd = [sys.executable, str(script)]
    if action == "enable":
        cmd.append("--enable")
    elif action == "disable":
        cmd.append("--disable")
    else:
        cmd.append("--status")
    subprocess.run(cmd, cwd=str(WINDOWS_DIR))


def grant_operator(gamertag: str | None = None, xuid: str | None = None):
    """Concede privilégio de operador."""
    script = WINDOWS_DIR / "dar_op.py"
    cmd = [sys.executable, str(script)]
    if gamertag:
        cmd.extend(["--gamertag", gamertag])
    if xuid:
        cmd.extend(["--xuid", xuid])
    subprocess.run(cmd, cwd=str(WINDOWS_DIR))


def reset_test_map():
    """Reseta o mapa de testes."""
    script = WINDOWS_DIR / "reset_test_map.py"
    subprocess.run([sys.executable, str(script)], cwd=str(WINDOWS_DIR))


def enable_loopback():
    """Habilita loopback para clientes locais na mesma máquina."""
    script = WINDOWS_DIR / "enable-loopback.ps1"
    subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", str(script)], cwd=str(WINDOWS_DIR))


def setup_firewall():
    """Configura regras de firewall."""
    script = WINDOWS_DIR / "setup-firewall.ps1"
    subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", str(script)], cwd=str(WINDOWS_DIR))


def interactive_menu():
    while True:
        print("\n" + "=" * 65)
        print("      ⛏ S_BEDROCK_SERVER: CANIVETE SUÍÇO DO MINECRAFT ⛏")
        print("=" * 65)
        print(" [1] Iniciar Servidor Bedrock (bedrock_server.exe)")
        print(" [2] Gerenciar CobbleDrock (Status / Ativar / Desativar)")
        print(" [3] Conceder Privilégios de Operador (dar_op)")
        print(" [4] Resetar Mapa de Testes")
        print(" [5] Habilitar Conexão Local (Loopback Exemption)")
        print(" [6] Configurar Firewall do Windows (Portas 19132/19133)")
        print(" [0] Sair")
        print("=" * 65)
        choice = input("Escolha uma opção (0-6): ").strip()

        if choice == "1":
            start_server()
        elif choice == "2":
            print("\n  [1] Ver status dos packs")
            print("  [2] Ativar CobbleDrock")
            print("  [3] Desativar CobbleDrock")
            sub = input("Escolha (1-3): ").strip()
            if sub == "1":
                manage_cobbledrock("status")
            elif sub == "2":
                manage_cobbledrock("enable")
            elif sub == "3":
                manage_cobbledrock("disable")
        elif choice == "3":
            gt = input("Gamertag do jogador (Enter para usar lista de amigos): ").strip()
            grant_operator(gamertag=gt if gt else None)
        elif choice == "4":
            confirm = input("Tem certeza que deseja resetar o mapa de testes? (s/N): ").strip().lower()
            if confirm == "s":
                reset_test_map()
        elif choice == "5":
            enable_loopback()
        elif choice == "6":
            setup_firewall()
        elif choice == "0":
            print("\nAté logo!")
            break
        else:
            print("\n[!] Opção inválida.")


def main():
    parser = argparse.ArgumentParser(description="Canivete Suíço do Minecraft Bedrock Server")
    parser.add_argument("--start", action="store_true", help="Inicia o servidor")
    parser.add_argument("--cobbledrock", choices=["status", "enable", "disable"], help="Gerencia o mod CobbleDrock")
    parser.add_argument("--op", type=str, help="Gamertag para conceder operador")
    parser.add_argument("--reset-map", action="store_true", help="Reseta o mapa de testes")
    parser.add_argument("--loopback", action="store_true", help="Habilita loopback local UWP")
    parser.add_argument("--firewall", action="store_true", help="Configura firewall do Windows")
    args = parser.parse_args()

    if args.start:
        start_server()
    elif args.cobbledrock:
        manage_cobbledrock(args.cobbledrock)
    elif args.op:
        grant_operator(gamertag=args.op)
    elif args.reset_map:
        reset_test_map()
    elif args.loopback:
        enable_loopback()
    elif args.firewall:
        setup_firewall()
    else:
        interactive_menu()


if __name__ == "__main__":
    main()
