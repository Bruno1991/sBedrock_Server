"""
Utilitario CLI Unificado do Minecraft Bedrock Dedicated Server (BDS).

Menu Centralizado:
 [1] Iniciar Servidor
 [2] Gerenciador de Mods e Add-ons (ativar/desativar)
 [3] Gerenciador de Mundos (Cobbled Farms, Spiral, Padrao)
 [4] Conceder Privilégios de Operador (dar_op)
 [5] Resetar Mapa Padrão (voltar ao original)
 [0] Sair
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

WINDOWS_DIR = Path(__file__).resolve().parent
if str(WINDOWS_DIR) not in sys.path:
    sys.path.insert(0, str(WINDOWS_DIR))

ROOT_DIR = WINDOWS_DIR.parent
SERVER_DIR = ROOT_DIR / "server"
RUNTIME_DIR = SERVER_DIR / "runtime"
BDS_EXE = RUNTIME_DIR / "bedrock_server.exe"

try:
    from bds_cmd import get_bds_pid
except ImportError:
    get_bds_pid = lambda: None

try:
    import gerenciar_mods
    from gerenciar_mods import (
        enable_mod,
        get_mod_status,
        list_available_worlds,
        read_level_name,
        switch_active_world,
    )
except ImportError:
    read_level_name = lambda: "Bedrock level"
    list_available_worlds = lambda: []
    switch_active_world = lambda name: False
    enable_mod = lambda key, lvl=None: False
    get_mod_status = lambda key, lvl=None: {"is_active": False}


def start_server():
    """Opcao [1]: Inicia o servidor Bedrock Dedicated Server de forma interativa."""
    if not BDS_EXE.is_file():
        print(f"[ERRO] Executavel nao encontrado em: {BDS_EXE}")
        print("       Execute primeiro a instalacao do servidor via bds-install.ps1.")
        return

    pid = get_bds_pid()
    if pid:
        print("\n" + "=" * 65)
        print(f"[AVISO] O servidor ja esta em execucao (PID: {pid})!")
        print("        Para parar, acesse a janela do console e digite 'stop'.")
        print("=" * 65)
        return

    start_ps1 = ROOT_DIR / "scripts" / "windows" / "bds-start.ps1"
    if start_ps1.is_file():
        cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(start_ps1)]
    else:
        cmd = [str(BDS_EXE)]

    print("\n" + "=" * 65)
    print("      ⛏ MINECRAFT BEDROCK SERVER: INICIANDO SERVIDOR ⛏")
    print("=" * 65)
    print(f" [*] Mundo Selecionado: {read_level_name()}")
    print(" [*] Porta: 19132 (IPv4) / 19133 (IPv6)")
    print(" [*] Digite 'stop' no console para desligar com seguranca.\n")
    try:
        subprocess.run(cmd, cwd=str(RUNTIME_DIR))
    except KeyboardInterrupt:
        print("\n[*] Retornando ao menu principal...")


def manage_mods():
    """Opcao [2]: Gerenciador de Mods e Add-ons (ativar/desativar)."""
    script = WINDOWS_DIR / "gerenciar_mods.py"
    if not script.is_file():
        print(f"[ERRO] Script de mods nao encontrado: {script}")
        return
    subprocess.run([sys.executable, str(script)], cwd=str(WINDOWS_DIR))


def manage_worlds():
    """Opcao [3]: Gerenciador de Mundos e Mapas (Cobbled Farms, Spiral, Padrao)."""
    while True:
        current_world = read_level_name()
        available_worlds = list_available_worlds()
        pid = get_bds_pid()

        cobble_st = get_mod_status("cobbledrock", "Cobbled Farms") if "Cobbled Farms" in available_worlds else {}
        cobble_tag = " (CobbleDrock [ATIVADO])" if cobble_st.get("is_active") else " (Add-on CobbleDrock [DESATIVADO])"

        print("\n" + "=" * 65)
        print("           GERENCIADOR DE MUNDOS E MAPAS (BDS)")
        print("=" * 65)
        print(f" Mundo Ativo no BDS: {current_world}")
        print(f" Mundos Disponiveis: {', '.join(available_worlds)}")
        if pid:
            print(f" [!] AVISO: O servidor BDS esta ativo (PID: {pid}).")
            print("            Apos alternar de mundo, reinicie o servidor com 'stop' para carregar.")
        print("-" * 65)
        print(f" [1] Ativar 'Cobbled Farms'{cobble_tag if 'Cobbled Farms' in available_worlds else ' [NAO INSTALADO]'}")
        print(" [2] Ativar 'Tryzz\\'s Parkour Spiral' (Mapa de Desafio)")
        print(" [3] Ativar 'Bedrock level' (Mundo Sobrevivencia Padrao)")
        print(" [4] Selecionar outro mundo da lista...")
        print(" [5] Instalar / Atualizar Cobbled Farms do CurseForge (via Chunker)")
        print(" [0] Voltar ao Menu Principal")
        print("=" * 65)

        try:
            choice = input(" Escolha uma opcao (0-5): ").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if choice == "1":
            if "Cobbled Farms" not in available_worlds:
                print("\n[!] 'Cobbled Farms' nao esta instalado. Deseja instalar agora via CurseForge?")
                conf = input(" Instalar Cobbled Farms? (s/N): ").strip().lower()
                if conf == "s":
                    install_cobbled_farms_flow(activate=True)
                continue

            if switch_active_world("Cobbled Farms"):
                enable_mod("cobbledrock", "Cobbled Farms")
                print("\n[SUCESSO] Mundo alternado para 'Cobbled Farms' com CobbleDrock ativo!")
                if pid:
                    print("[!] Lembre-se de reiniciar o servidor para carregar o novo mapa.")
            input("\nPressione ENTER para continuar...")

        elif choice == "2":
            if "Tryzz's Parkour Spiral" in available_worlds:
                switch_active_world("Tryzz's Parkour Spiral")
                print("\n[SUCESSO] Mundo alternado para 'Tryzz\'s Parkour Spiral'!")
            else:
                print("\n[ERRO] Mundo 'Tryzz\'s Parkour Spiral' nao encontrado.")
            input("\nPressione ENTER para continuar...")

        elif choice == "3":
            if "Bedrock level" in available_worlds:
                switch_active_world("Bedrock level")
                print("\n[SUCESSO] Mundo alternado para 'Bedrock level'!")
            else:
                print("\n[ERRO] Mundo 'Bedrock level' nao encontrado.")
            input("\nPressione ENTER para continuar...")

        elif choice == "4":
            print("\nMundos Instalados:")
            for i, w in enumerate(available_worlds, 1):
                marker = " (ATUAL)" if w == current_world else ""
                print(f" [{i}] {w}{marker}")
            w_choice = input(f" Escolha o numero do mundo (1-{len(available_worlds)}): ").strip()
            if w_choice.isdigit() and 1 <= int(w_choice) <= len(available_worlds):
                chosen = available_worlds[int(w_choice) - 1]
                switch_active_world(chosen)
            input("\nPressione ENTER para continuar...")

        elif choice == "5":
            install_cobbled_farms_flow(activate=True)
            input("\nPressione ENTER para continuar...")

        elif choice == "0":
            break
        else:
            print("\n[!] Opcao invalida.")
            time.sleep(1)


def install_cobbled_farms_flow(activate: bool = True):
    """Executa o script de instalacao e conversao do Cobbled Farms."""
    script = WINDOWS_DIR / "instalar_cobbled_farms.py"
    if not script.is_file():
        print(f"[ERRO] Script instalador nao encontrado: {script}")
        return
    cmd = [sys.executable, str(script)]
    if activate:
        cmd.append("--activate")
    subprocess.run(cmd, cwd=str(WINDOWS_DIR))


def grant_operator(gamertag: str | None = None, xuid: str | None = None):
    """Opcao [4]: Conceder Privilegios de Operador (dar_op)."""
    script = WINDOWS_DIR / "dar_op.py"
    if not script.is_file():
        print(f"[ERRO] Script dar_op nao encontrado: {script}")
        return

    cmd = [sys.executable, str(script)]
    if gamertag:
        cmd.extend(["--gamertag", gamertag])
    if xuid:
        cmd.extend(["--xuid", xuid])

    subprocess.run(cmd, cwd=str(WINDOWS_DIR))


def reset_map():
    """Opcao [5]: Resetar Mapa (voltar ao original)."""
    script = WINDOWS_DIR / "reset_test_map.py"
    if not script.is_file():
        print(f"[ERRO] Script reset_test_map nao encontrado: {script}")
        return

    print("\n" + "=" * 65)
    print("           ATENCAO: RESTAURACAO DO MAPA ORIGINAL")
    print("=" * 65)
    print(" O mundo atual sera arquivado em server/data/backups/")
    print(" e o mapa limpo/original sera restaurado.")
    print("-" * 65)
    confirm = input(" Deseja realmente resetar o mapa ao original? (s/N): ").strip().lower()
    if confirm == "s":
        subprocess.run([sys.executable, str(script)], cwd=str(WINDOWS_DIR))
    else:
        print("\n[*] Operacao cancelada. Mapa preservado intacto.")


def interactive_menu():
    """Menu CLI principal interativo."""
    while True:
        pid = get_bds_pid()
        status_tag = f"ATIVO (PID: {pid})" if pid else "PARADO"
        current_world = read_level_name()

        print("\n" + "=" * 65)
        print("      S_BEDROCK_SERVER: UTILITARIO CLI UNIFICADO")
        print("=" * 65)
        print(f" Status do Servidor BDS: {status_tag}")
        print(f" Mundo Ativo no BDS:     {current_world}")
        print("-" * 65)
        print(" [1] Iniciar Servidor")
        print(" [2] Gerenciador de Mods e Add-ons (ativar/desativar)")
        print(" [3] Gerenciador de Mundos / Cobbled Farms")
        print(" [4] Conceder Privilegios de Operador (dar_op)")
        print(" [5] Resetar Mapa Padrao (voltar ao original)")
        print(" [0] Sair")
        print("=" * 65)

        try:
            choice = input(" Escolha uma opcao (0-5): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nAte logo!")
            break

        if choice == "1":
            start_server()
            input("\nPressione ENTER para voltar ao menu...")
        elif choice == "2":
            manage_mods()
        elif choice == "3":
            manage_worlds()
        elif choice == "4":
            print("\n" + "-" * 65)
            print(" Conceder Privilegios de Operador (dar_op)")
            print(" Deixe vazio e pressione ENTER para sincronizar todos os amigos")
            print(" configurados em 'amigos_operadores.txt'.")
            print("-" * 65)
            gt = input(" Gamertag do jogador (ou ENTER para lista): ").strip()
            grant_operator(gamertag=gt if gt else None)
            input("\nPressione ENTER para voltar ao menu...")
        elif choice == "5":
            reset_map()
            input("\nPressione ENTER para voltar ao menu...")
        elif choice == "0":
            print("\nAte logo!")
            break
        else:
            print("\n[!] Opcao invalida. Escolha entre 0 e 5.")
            time.sleep(1)


def main():
    parser = argparse.ArgumentParser(description="Utilitario CLI Unificado do Minecraft Bedrock Server")
    parser.add_argument("--start", action="store_true", help="[1] Inicia o servidor")
    parser.add_argument("--mods", action="store_true", help="[2] Abre o gerenciador de mods e add-ons")
    parser.add_argument("--worlds", action="store_true", help="[3] Abre o gerenciador de mundos e mapas")
    parser.add_argument("--world", type=str, help="Define o mundo ativo em server.properties")
    parser.add_argument("--cobbled-farms", action="store_true", help="Ativa Cobbled Farms com CobbleDrock imediatamente")
    parser.add_argument("--install-cobbled-farms", action="store_true", help="Executa o instalador do Cobbled Farms do CurseForge")
    parser.add_argument("--list-worlds", action="store_true", help="Lista todos os mundos instalados")
    parser.add_argument("--op", type=str, help="[4] Gamertag para conceder operador")
    parser.add_argument("--reset-map", action="store_true", help="[5] Reseta o mapa para o original")
    parser.add_argument("--status", action="store_true", help="Exibe o status do servidor e mundo ativo")
    args = parser.parse_args()

    if args.start:
        start_server()
    elif args.mods:
        manage_mods()
    elif args.worlds:
        manage_worlds()
    elif args.world:
        switch_active_world(args.world)
    elif args.cobbled_farms:
        if switch_active_world("Cobbled Farms"):
            enable_mod("cobbledrock", "Cobbled Farms")
            print("[SUCESSO] Cobbled Farms ativado com CobbleDrock!")
    elif args.install_cobbled_farms:
        install_cobbled_farms_flow(activate=True)
    elif args.list_worlds:
        current = read_level_name()
        worlds = list_available_worlds()
        print("Mundos instalados no BDS:")
        for w in worlds:
            active = " [ATIVO]" if w == current else ""
            print(f" - {w}{active}")
    elif args.op:
        grant_operator(gamertag=args.op)
    elif args.reset_map:
        reset_map()
    elif args.status:
        pid = get_bds_pid()
        current = read_level_name()
        print(f"Status do Servidor BDS: {'ATIVO (PID: ' + str(pid) + ')' if pid else 'PARADO'}")
        print(f"Mundo Ativo no BDS:     {current}")
    else:
        interactive_menu()


if __name__ == "__main__":
    main()
