"""
Utilitario CLI Unificado e Inteligente do Minecraft Bedrock Dedicated Server (BDS).

Menu Centralizado de Alta Performance:
 [1] Iniciar Servidor (Janela Dedicada / Background ou Primeiro Plano)
 [2] Parar / Reiniciar Servidor com Parada Graciosa (Flush LevelDB)
 [3] Enviar Comando ao Console Vivo do BDS (Win32 Console IPC)
 [4] Gerenciador Inteligente de Mundos (Lucky OneBlock, Cobbled Farms, Backups, Troca)
 [5] Gerenciador de Mods e Add-ons (Lucky Block, CobbleDrock, Spikes, Avaritia, Spectrite)
 [6] Central CurseForge: Instalador Inteligente via URL ou 1-Clique
 [7] Conceder Privilégios de Operador (dar_op / Auto-OP de amigos)
 [8] Diagnóstico de Saúde e Auto-Reparo (Healthcheck / Self-Healing)
 [9] Resetar Mapa Padrão (Arquivar e restaurar limpo)
 [L] Visualizar Logs Recentes do Servidor
 [0] Sair
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

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
DATA_DIR = SERVER_DIR / "data"
WORLDS_DIR = DATA_DIR / "worlds"
BDS_EXE = RUNTIME_DIR / "bedrock_server.exe"

# Modulos do ecossistema BDS
try:
    from bds_cmd import get_bds_pid, send_command
except ImportError:
    get_bds_pid = lambda: None
    send_command = lambda cmd, wait_ms=50: False

try:
    import server_manager as sm
except ImportError:
    sm = None

try:
    import gerenciar_mods
    from gerenciar_mods import (
        enable_mod,
        disable_mod,
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
    disable_mod = lambda key, lvl=None: False
    get_mod_status = lambda key, lvl=None: {"is_active": False}


# ==============================================================================
# ACOES OPERACIONAIS DO SERVIDOR
# ==============================================================================

def start_server(detached: bool = False):
    """Opcao [1]: Inicia o servidor Bedrock Dedicated Server."""
    if not BDS_EXE.is_file():
        print(f"[ERRO] Executavel nao encontrado em: {BDS_EXE}")
        print("       Execute primeiro a instalacao do servidor via bds-install.ps1.")
        return

    pid = get_bds_pid()
    if pid:
        print("\n" + "=" * 65)
        print(f"[AVISO] O servidor ja esta em execucao (PID: {pid})!")
        print("        Para parar, acesse a janela do console ou use a opcao [2].")
        print("=" * 65)
        return

    if sm is not None:
        sm.sync_packs_to_runtime()

    if detached:
        if sm is not None:
            ok, msg = sm.start_server_process(detached=True)
            print(f"\n[*] {msg}")
            return
        else:
            subprocess.Popen([str(BDS_EXE)], cwd=str(RUNTIME_DIR), creationflags=subprocess.CREATE_NEW_CONSOLE)
            print("\n[+] Servidor iniciado em janela destacada.")
            return

    start_ps1 = ROOT_DIR / "scripts" / "windows" / "bds-start.ps1"
    if start_ps1.is_file():
        cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(start_ps1)]
    else:
        cmd = [str(BDS_EXE)]

    print("\n" + "=" * 65)
    print("      MINECRAFT BEDROCK SERVER: INICIANDO SERVIDOR")
    print("=" * 65)
    print(f" [*] Mundo Selecionado: {read_level_name()}")
    print(" [*] Porta: 19132 (IPv4) / 19133 (IPv6)")
    print(" [*] Digite 'stop' no console para desligar com seguranca.\n")
    try:
        subprocess.run(cmd, cwd=str(RUNTIME_DIR))
    except KeyboardInterrupt:
        print("\n[*] Retornando ao menu principal...")


def stop_server_flow():
    """Opcao [2]: Parada graciosa ou reinicializacao do servidor."""
    pid = get_bds_pid()
    if not pid:
        print("\n[!] O servidor BDS ja esta parado.")
        return

    print("\n" + "=" * 65)
    print(f"       CONTROLE DE PROCESSO BDS ATIVO (PID: {pid})")
    print("=" * 65)
    print(" [1] Parar Servidor com Seguranca (Flush LevelDB)")
    print(" [2] Reiniciar Servidor (Parar -> Iniciar em Janela Dedicada)")
    print(" [0] Cancelar")
    print("-" * 65)
    choice = input(" Escolha uma opcao (0-2): ").strip()

    if choice == "1":
        if sm is not None:
            ok, msg = sm.stop_server_gracefully()
            print(f"\n[{'SUCESSO' if ok else 'AVISO'}] {msg}")
        else:
            send_command("stop")
            print("\n[*] Comando 'stop' enviado.")
    elif choice == "2":
        if sm is not None:
            ok, msg = sm.restart_server()
            print(f"\n[{'SUCESSO' if ok else 'ERRO'}] {msg}")
        else:
            send_command("stop")
            time.sleep(3)
            subprocess.Popen([str(BDS_EXE)], cwd=str(RUNTIME_DIR), creationflags=subprocess.CREATE_NEW_CONSOLE)
            print("\n[+] Servidor reiniciado.")


def live_command_console():
    """Opcao [3]: Envio interativo de comandos ao console do servidor BDS."""
    pid = get_bds_pid()
    if not pid:
        print("\n[!] O servidor BDS nao esta rodando. Inicie-o primeiro para enviar comandos.")
        return

    print("\n" + "=" * 65)
    print(f"     CONSOLE INTERATIVO DO BDS (SERVIDOR ATIVO - PID: {pid})")
    print("=" * 65)
    print(" Digite qualquer comando nativo do Minecraft para enviar ao console.")
    print(" Exemplos: list, time set day, weather clear, say Ola amigos!, op Gamertag")
    print(" Digite 'sair' ou pressione ENTER vazio para voltar ao menu.")
    print("-" * 65)

    while True:
        try:
            cmd = input(" BDS Console > ").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if not cmd or cmd.lower() in ["sair", "exit", "quit"]:
            break

        ok = send_command(cmd)
        if ok:
            print(f" [OK] '{cmd}' executado.")
        else:
            print(f" [FALHA] Nao foi possivel transmitir '{cmd}' ao console.")


def manage_mods():
    """Opcao [5]: Gerenciador de Mods e Add-ons (ativar/desativar)."""
    script = WINDOWS_DIR / "gerenciar_mods.py"
    if not script.is_file():
        print(f"[ERRO] Script de mods nao encontrado: {script}")
        return
    subprocess.run([sys.executable, str(script)], cwd=str(WINDOWS_DIR))


def manage_worlds():
    """Opcao [4]: Gerenciador Inteligente de Mundos e Mapas."""
    while True:
        current_world = read_level_name()
        available_worlds = list_available_worlds()
        pid = get_bds_pid()

        print("\n" + "=" * 70)
        print("           GERENCIADOR INTELIGENTE DE MUNDOS E MAPAS (BDS)")
        print("=" * 70)
        print(f" Mundo Ativo no BDS:   {current_world}")
        print(f" Status do Processo:   {'ATIVO (PID: ' + str(pid) + ')' if pid else 'PARADO'}")
        print("-" * 70)

        detailed = sm.list_worlds_detailed() if sm is not None else []
        if detailed:
            print(" Mundos Instalados:")
            for idx, w in enumerate(detailed, 1):
                active_tag = " [ATIVO]" if w["is_active"] else ""
                packs_tag = f" ({w['bp_count']} BPs / {w['rp_count']} RPs)" if w["bp_count"] or w["rp_count"] else ""
                print(f"  [{idx}] {w['name']:<25} {w['size_mb']:>6} MB | Modificado: {w['last_modified']}{active_tag}{packs_tag}")
        else:
            print(f" Mundos Disponiveis: {', '.join(available_worlds)}")

        print("-" * 70)
        print(" Ações Rápidas:")
        print("  [L] Ativar 'Lucky OneBlock' (Mapa OneBlock)")
        print("  [C] Ativar 'Cobbled Farms' (Mapa Cobblemon)")
        print("  [P] Ativar 'Bedrock level' (Mundo Sobrevivência Padrão)")
        print("  [S] Ativar 'Tryzz\\'s Parkour Spiral' (Mapa de Desafio)")
        print("  [D] Desativar TODOS os Mods no Mundo Ativo (Deixar Vanilla / Limpo)")
        print("  [B] Fazer Backup do Mundo Ativo Agora (Snapshot ZIP)")
        print("  [R] Ver Backups Existentes")
        print("  [0] Voltar ao Menu Principal")
        print("=" * 70)

        try:
            choice = input(" Digite o numero do mundo para ativar, ou uma letra (0 para voltar): ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            break

        if choice == "0":
            break

        elif choice == "l":
            if "Lucky OneBlock" in available_worlds:
                switch_active_world_smart("Lucky OneBlock")
            else:
                print("\n[!] 'Lucky OneBlock' nao esta instalado. Deseja instalar agora do CurseForge?")
                conf = input(" Instalar Lucky OneBlock? (s/N): ").strip().lower()
                if conf == "s":
                    install_lucky_oneblock_flow(activate=True)
            input("\nPressione ENTER para continuar...")

        elif choice == "c":
            if "Cobbled Farms" in available_worlds:
                switch_active_world_smart("Cobbled Farms")
            else:
                print("\n[!] 'Cobbled Farms' nao esta instalado. Deseja instalar agora do CurseForge?")
                conf = input(" Instalar Cobbled Farms? (s/N): ").strip().lower()
                if conf == "s":
                    install_cobbled_farms_flow(activate=True)
            input("\nPressione ENTER para continuar...")

        elif choice == "p":
            if "Bedrock level" in available_worlds:
                switch_active_world_smart("Bedrock level")
            else:
                print("\n[!] Mundo 'Bedrock level' nao encontrado.")
            input("\nPressione ENTER para continuar...")

        elif choice == "s":
            if "Tryzz's Parkour Spiral" in available_worlds:
                switch_active_world_smart("Tryzz's Parkour Spiral")
            else:
                print("\n[!] Mundo 'Tryzz\\'s Parkour Spiral' nao encontrado.")
            input("\nPressione ENTER para continuar...")

        elif choice == "d":
            if sm is not None:
                ok, msg = sm.disable_all_mods()
                print(f"\n[{'SUCESSO' if ok else 'ERRO'}] {msg}")
            else:
                gerenciar_mods.disable_all_mods()
            input("\nPressione ENTER para continuar...")

        elif choice == "b":
            if sm is not None:
                ok, msg = sm.backup_world()
                print(f"\n[{'SUCESSO' if ok else 'ERRO'}] {msg}")
            else:
                print("\n[!] Modulo server_manager nao disponivel.")
            input("\nPressione ENTER para continuar...")

        elif choice == "r":
            if sm is not None:
                backups = sm.list_world_backups()
                print("\n" + "=" * 65)
                print("              BACKUPS DE MUNDOS DISPONIVEIS")
                print("=" * 65)
                if not backups:
                    print(" Nenhum backup arquivado em server/data/backups/worlds/.")
                else:
                    for b in backups:
                        print(f" * {b['name']} ({b['size_mb']} MB) - {b['date']}")
                print("=" * 65)
            input("\nPressione ENTER para continuar...")

        elif choice.isdigit():
            idx = int(choice)
            if detailed and 1 <= idx <= len(detailed):
                chosen_name = detailed[idx - 1]["name"]
                switch_active_world_smart(chosen_name)
            elif 1 <= idx <= len(available_worlds):
                chosen_name = available_worlds[idx - 1]
                switch_active_world_smart(chosen_name)
            else:
                print("\n[!] Numero de mundo fora do intervalo.")
            input("\nPressione ENTER para continuar...")

        else:
            print("\n[!] Opcao invalida.")
            time.sleep(1)


def switch_active_world_smart(world_name: str) -> bool:
    """Troca de mundo inteligentemente com aviso/reinicio de processo se ativo."""
    pid = get_bds_pid()
    auto_restart = False

    if pid:
        print(f"\n[!] AVISO: O servidor BDS esta ativo (PID: {pid}).")
        ans = input(" Deseja reiniciar o servidor automaticamente para aplicar o novo mundo? (s/N): ").strip().lower()
        auto_restart = (ans == "s")

    if sm is not None:
        ok, msg = sm.switch_world(world_name, auto_restart=auto_restart)
        print(f"\n[{'SUCESSO' if ok else 'ERRO'}] {msg}")
        return ok
    else:
        return switch_active_world(world_name)


def install_lucky_oneblock_flow(activate: bool = True):
    """Executa o script instalador oficial do Lucky OneBlock."""
    script = WINDOWS_DIR / "instalar_lucky_oneblock.py"
    if not script.is_file():
        print(f"[ERRO] Script instalador nao encontrado: {script}")
        return
    cmd = [sys.executable, str(script)]
    if activate:
        cmd.append("--activate")
    subprocess.run(cmd, cwd=str(WINDOWS_DIR))


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


def curseforge_hub_flow():
    """Opcao [6]: Central CurseForge para instalacao de mundos e mods."""
    print("\n" + "=" * 65)
    print("          CENTRAL CURSEFORGE: INSTALADOR INTELIGENTE")
    print("=" * 65)
    print(" [1] Instalar / Atualizar 'Lucky OneBlock' (CurseForge 872580)")
    print(" [2] Instalar / Atualizar 'Cobbled Farms' (CurseForge 924311)")
    print(" [3] Informar URL ou Slug do CurseForge...")
    print(" [0] Voltar")
    print("-" * 65)
    c = input(" Escolha uma opcao (0-3): ").strip()

    if c == "1":
        install_lucky_oneblock_flow(activate=True)
    elif c == "2":
        install_cobbled_farms_flow(activate=True)
    elif c == "3":
        raw = input(" Cole a URL do CurseForge: ").strip()
        if raw:
            if sm is not None:
                ok, msg = sm.install_from_curseforge(raw, activate=True)
                print(f"\n[{'SUCESSO' if ok else 'AVISO'}] {msg}")
            else:
                print("[!] Modulo server_manager nao carregado.")
    input("\nPressione ENTER para continuar...")


def healthcheck_flow():
    """Opcao [8]: Diagnostico de integridade e auto-reparo do servidor."""
    if sm is None:
        print("[!] Modulo server_manager nao disponivel.")
        return

    hc = sm.run_healthcheck()
    print("\n" + "=" * 70)
    print("           DIAGNOSTICO DE SAUDE DO SERVIDOR BEDROCK")
    print("=" * 70)
    for c in hc["checks"]:
        badge = "[PASS]" if c["status"] == "PASS" else f"[{c['status']}]"
        print(f" {badge:<8} {c['name']:<42} : {c['details']}")
    print("-" * 70)
    print(f" Status Geral: {'100% SAUDAVEL E INTEGRADO' if hc['overall_ok'] else 'ATENCAO NECESSARIA'}")
    print("=" * 70)

    if not hc["overall_ok"]:
        fix = input("\n Deseja aplicar os reparos automaticos (Self-Healing)? (s/N): ").strip().lower()
        if fix == "s":
            actions = sm.auto_heal_server()
            print("\n[*] Ações executadas:")
            for a in actions:
                print(f"  + {a}")
            print("\n[+] Auto-reparo finalizado.")


def view_logs_flow():
    """Opcao [L]: Exibe as ultimas linhas do log do BDS."""
    if sm is None:
        print("[!] Modulo server_manager nao disponivel.")
        return
    logs = sm.get_recent_logs(max_lines=35)
    print("\n" + "=" * 70)
    print("                    LOGS RECENTES DO BDS")
    print("=" * 70)
    for line in logs:
        print(f"  {line}")
    print("=" * 70)


def grant_operator(gamertag: str | None = None, xuid: str | None = None):
    """Opcao [7]: Conceder Privilegios de Operador (dar_op)."""
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
    """Opcao [9]: Resetar Mapa (voltar ao original limpo)."""
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


# ==============================================================================
# MENU INTERATIVO PRINCIPAL
# ==============================================================================

def interactive_menu():
    """Menu CLI principal interativo e inteligente."""
    while True:
        status_info = sm.get_server_status() if sm is not None else {}
        pid = status_info.get("pid") or get_bds_pid()
        if pid:
            ram_info = f", RAM: {status_info.get('memory_mb')} MB" if status_info.get("memory_mb") else ""
            status_tag = f"ATIVO (PID: {pid}{ram_info})"
        else:
            status_tag = "PARADO"

        current_world = read_level_name()
        total_worlds = status_info.get("total_worlds", len(list_available_worlds()))

        print("\n" + "=" * 70)
        print("      S_BEDROCK_SERVER: UTILITARIO DE GERENCIA INTELIGENTE")
        print("=" * 70)
        print(f" Status do Servidor BDS: {status_tag}")
        print(f" Mundo Ativo no BDS:     {current_world} (Total: {total_worlds} mundos)")
        if status_info.get("active_mods"):
            print(f" Mods Ativos:            {', '.join(status_info['active_mods'][:3])}...")
        print("-" * 70)
        print(" [1] Iniciar Servidor (Janela Dedicada / Background ou 1º Plano)")
        print(" [2] Parar / Reiniciar Servidor (Parada Graciosa com Flush)")
        print(" [3] Enviar Comando ao Console Vivo do BDS (list, time, say...)")
        print(" [4] Gerenciador de Mundos & Mapas (Lucky OneBlock, Cobbled, Backups)")
        print(" [5] Gerenciador de Mods e Add-ons (Ativar / Desativar Pacotes)")
        print(" [6] Central CurseForge: Instalar Lucky OneBlock / Cobbled / URL")
        print(" [7] Conceder Privilegios de Operador (dar_op / Auto-OP)")
        print(" [8] Diagnóstico de Saúde e Auto-Reparo (Healthcheck / Fix)")
        print(" [9] Resetar Mapa Padrao (voltar ao original limpo)")
        print(" [L] Visualizar Logs Recentes do Servidor")
        print(" [0] Sair")
        print("=" * 70)

        try:
            choice = input(" Escolha uma opcao: ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\nAte logo!")
            break

        if choice == "1":
            print("\n Iniciar Servidor:")
            print("  [1] Janela Dedicada (Recomendado - Mantem este utilitario liberado)")
            print("  [2] Primeiro Plano (Modo Console Direto)")
            s_mode = input("  Modo (1 ou 2, padrao 1): ").strip()
            if s_mode == "2":
                start_server(detached=False)
            else:
                start_server(detached=True)
            input("\nPressione ENTER para voltar ao menu...")
        elif choice == "2":
            stop_server_flow()
            input("\nPressione ENTER para voltar ao menu...")
        elif choice == "3":
            live_command_console()
            input("\nPressione ENTER para voltar ao menu...")
        elif choice == "4":
            manage_worlds()
        elif choice == "5":
            manage_mods()
        elif choice == "6":
            curseforge_hub_flow()
        elif choice == "7":
            print("\n" + "-" * 65)
            print(" Conceder Privilegios de Operador (dar_op)")
            print(" Deixe vazio e pressione ENTER para sincronizar todos os amigos")
            print(" configurados em 'amigos_operadores.txt'.")
            print("-" * 65)
            gt = input(" Gamertag do jogador (ou ENTER para lista): ").strip()
            grant_operator(gamertag=gt if gt else None)
            input("\nPressione ENTER para voltar ao menu...")
        elif choice == "8":
            healthcheck_flow()
            input("\nPressione ENTER para voltar ao menu...")
        elif choice == "9":
            reset_map()
            input("\nPressione ENTER para voltar ao menu...")
        elif choice == "l":
            view_logs_flow()
            input("\nPressione ENTER para voltar ao menu...")
        elif choice == "0":
            print("\nAte logo!")
            break
        else:
            print("\n[!] Opcao invalida.")
            time.sleep(1)


# ==============================================================================
# PONTO DE ENTRADA CLI E PARSER DE ARGUMENTOS
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(description="Utilitario CLI Unificado do Minecraft Bedrock Server")

    # Modos de ciclo de vida
    parser.add_argument("--start", action="store_true", help="[1] Inicia o servidor")
    parser.add_argument("--detached", action="store_true", help="Inicia o servidor em janela separada de background")
    parser.add_argument("--stop", action="store_true", help="Para o servidor BDS de forma graciosa")
    parser.add_argument("--restart", action="store_true", help="Reinicia o servidor BDS de forma limpa")
    parser.add_argument("--cmd", type=str, help="Envia um comando ao console do servidor BDS vivo")

    # Mundos e Mods
    parser.add_argument("--mods", action="store_true", help="[2] Abre o gerenciador de mods e add-ons")
    parser.add_argument("--worlds", action="store_true", help="[3] Abre o gerenciador de mundos e mapas")
    parser.add_argument("--world", type=str, help="Define o mundo ativo em server.properties")
    parser.add_argument("--list-worlds", action="store_true", help="Lista todos os mundos instalados")
    parser.add_argument("--disable-all", action="store_true", help="Desativa todos os mods no mundo ativo ou especificado (modo vanilla limpo)")
    parser.add_argument("--backup-world", nargs="?", const="", help="Gera backup ZIP do mundo informado ou ativo")
    parser.add_argument("--list-backups", action="store_true", help="Lista os backups de mundos arquivados")

    # Atalhos de mundos oficiais
    parser.add_argument("--lucky-oneblock", action="store_true", help="Ativa Lucky OneBlock com Lucky Block Engine imediatamente")
    parser.add_argument("--install-lucky-oneblock", action="store_true", help="Executa o instalador do Lucky OneBlock do CurseForge")
    parser.add_argument("--cobbled-farms", action="store_true", help="Ativa Cobbled Farms com CobbleDrock imediatamente")
    parser.add_argument("--install-cobbled-farms", action="store_true", help="Executa o instalador do Cobbled Farms do CurseForge")
    parser.add_argument("--install-curseforge", type=str, help="Instala mapa/mod a partir de URL ou slug do CurseForge")

    # Administracao e Diagnostico
    parser.add_argument("--op", type=str, help="[4] Gamertag para conceder operador")
    parser.add_argument("--reset-map", action="store_true", help="[5] Reseta o mapa para o original")
    parser.add_argument("--status", action="store_true", help="Exibe o status do servidor e mundo ativo")
    parser.add_argument("--healthcheck", action="store_true", help="Executa auditoria de integridade do servidor")
    parser.add_argument("--fix", action="store_true", help="Aplica auto-reparos (Self-Healing) ao servidor")
    parser.add_argument("--logs", nargs="?", const=40, type=int, help="Exibe as ultimas linhas do log do servidor")

    args = parser.parse_args()

    if args.start:
        start_server(detached=args.detached)
    elif args.stop:
        if sm is not None:
            ok, msg = sm.stop_server_gracefully()
            print(msg)
        else:
            send_command("stop")
    elif args.restart:
        if sm is not None:
            ok, msg = sm.restart_server()
            print(msg)
        else:
            send_command("stop")
            time.sleep(2)
            start_server(detached=True)
    elif args.cmd:
        if sm is not None:
            ok, msg = sm.send_console_command(args.cmd)
            print(msg)
        else:
            ok = send_command(args.cmd)
            print(f"Comando {'enviado' if ok else 'falhou'}: {args.cmd}")
    elif args.mods:
        manage_mods()
    elif args.worlds:
        manage_worlds()
    elif args.world:
        if sm is not None:
            sm.switch_world(args.world)
        else:
            switch_active_world(args.world)
    elif args.lucky_oneblock:
        if switch_active_world("Lucky OneBlock"):
            enable_mod("luckyblock", "Lucky OneBlock")
            print("[SUCESSO] Lucky OneBlock ativado com Lucky Block Engine!")
    elif args.install_lucky_oneblock:
        install_lucky_oneblock_flow(activate=True)
    elif args.cobbled_farms:
        if switch_active_world("Cobbled Farms"):
            enable_mod("cobbledrock", "Cobbled Farms")
            print("[SUCESSO] Cobbled Farms ativado com CobbleDrock!")
    elif args.install_cobbled_farms:
        install_cobbled_farms_flow(activate=True)
    elif args.install_curseforge:
        if sm is not None:
            ok, msg = sm.install_from_curseforge(args.install_curseforge, activate=True)
            print(f"[{'SUCESSO' if ok else 'ERRO'}] {msg}")
    elif args.list_worlds:
        current = read_level_name()
        worlds = list_available_worlds()
        print("Mundos instalados no BDS:")
        for w in worlds:
            active = " [ATIVO]" if w == current else ""
            print(f" - {w}{active}")
    elif args.disable_all:
        target = args.world if args.world else None
        if sm is not None:
            ok, msg = sm.disable_all_mods(target)
            print(f"[{'SUCESSO' if ok else 'ERRO'}] {msg}")
        else:
            gerenciar_mods.disable_all_mods(target)
    elif args.backup_world is not None:
        target = args.backup_world if args.backup_world else None
        if sm is not None:
            ok, msg = sm.backup_world(target)
            print(msg)
    elif args.list_backups:
        if sm is not None:
            bks = sm.list_world_backups()
            print("Backups de mundos:")
            for b in bks:
                print(f" - {b['name']} ({b['size_mb']} MB, {b['date']})")
    elif args.op:
        grant_operator(gamertag=args.op)
    elif args.reset_map:
        reset_map()
    elif args.status:
        if sm is not None:
            st = sm.get_server_status()
            pid_str = f"ATIVO (PID: {st['pid']})" if st["running"] else "PARADO"
            if st["running"] and st["memory_mb"]:
                pid_str += f" [RAM: {st['memory_mb']} MB]"
            print(f"Status do Servidor BDS: {pid_str}")
            print(f"Mundo Ativo no BDS:     {st['active_world']}")
            if st["active_mods"]:
                print(f"Mods Ativos:            {', '.join(st['active_mods'])}")
        else:
            pid = get_bds_pid()
            current = read_level_name()
            print(f"Status do Servidor BDS: {'ATIVO (PID: ' + str(pid) + ')' if pid else 'PARADO'}")
            print(f"Mundo Ativo no BDS:     {current}")
    elif args.healthcheck:
        if sm is not None:
            hc = sm.run_healthcheck()
            print(f"Auditoria de Saúde do BDS: {'100% PASS' if hc['overall_ok'] else 'ALERTA'}")
            for c in hc["checks"]:
                print(f" - [{c['status']}] {c['name']}: {c['details']}")
    elif args.fix:
        if sm is not None:
            actions = sm.auto_heal_server()
            print("Auto-reparos aplicados:")
            for a in actions:
                print(f" + {a}")
    elif args.logs is not None:
        if sm is not None:
            lines = sm.get_recent_logs(max_lines=args.logs)
            for l in lines:
                print(l)
    else:
        interactive_menu()


if __name__ == "__main__":
    main()
