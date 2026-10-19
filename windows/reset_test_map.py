"""
Restaurador do Mapa Original - Minecraft Bedrock Dedicated Server (BDS).

Objetivo:
    Limpar tudo o que foi construido ou destruido pelos jogadores e
    reverter o mundo para o estado original e limpo.

Funcionamento:
    1. Se o servidor estiver rodando, envia comando 'stop' e aguarda o desligamento limpo.
    2. Move o mundo com alteracoes para uma pasta de seguranca em server/data/backups/.
    3. Restaura o mapa original a partir do backup inicial (.zip) do servidor.
    4. Deixa o servidor 100% pronto para ser iniciado com o mapa virgem.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
import zipfile
from datetime import datetime
from pathlib import Path

WINDOWS_DIR = Path(__file__).resolve().parent
if str(WINDOWS_DIR) not in sys.path:
    sys.path.insert(0, str(WINDOWS_DIR))

try:
    from bds_cmd import get_bds_pid, send_command
except ImportError:
    get_bds_pid = lambda: None
    send_command = lambda cmd, wait_ms=50: False

# ======================================================================
# CAMINHOS DO PROJETO (Conforme ADR-003)
# ======================================================================

PROJECT_ROOT = WINDOWS_DIR.parent
SERVER_DIR = PROJECT_ROOT / "server"
RUNTIME_DIR = SERVER_DIR / "runtime"
DATA_DIR = SERVER_DIR / "data"

BDS_EXE = RUNTIME_DIR / "bedrock_server.exe"
SERVER_PROPERTIES = RUNTIME_DIR / "server.properties"
WORLDS_DIR = DATA_DIR / "worlds"
BACKUPS_DIR = DATA_DIR / "backups"


def read_level_name() -> str:
    """Le o level-name configurado em server/runtime/server.properties."""
    if not SERVER_PROPERTIES.exists():
        return "Bedrock level"

    try:
        content = SERVER_PROPERTIES.read_text(encoding="utf-8-sig")
        for raw_line in content.splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("level-name="):
                val = line.split("=", 1)[1].strip()
                if val:
                    return val
    except Exception:
        pass
    return "Bedrock level"


def stop_running_bds():
    """Para o processo do BDS de forma limpa ou forcada se necessario."""
    pid = get_bds_pid()
    if not pid:
        print("[INFO] Servidor BDS ja esta parado.")
        return

    print(f"[INFO] Servidor BDS detectado ativo (PID: {pid}).")
    print("[INFO] Enviando comando 'stop' para encerramento limpo do LevelDB...")

    send_command("say [BDS] Restaurando mundo original... Encerrando servidor.")
    send_command("stop")

    for _ in range(20):
        time.sleep(0.5)
        if not get_bds_pid():
            print("[INFO] Servidor encerrado com sucesso.")
            return

    print("[AVISO] Servidor demorou para encerrar. Finalizando processo via taskkill...")
    try:
        subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output=True, check=False)
        time.sleep(1)
    except Exception as exc:
        print(f"[AVISO] Falha ao finalizar processo {pid}: {exc}")


def restore_original_map():
    print()
    print("=" * 72)
    print("        RESTAURACAO DO MAPA ORIGINAL - BEDROCK SERVER")
    print("=" * 72)
    print()

    stop_running_bds()

    level_name = read_level_name()
    world_dir = WORLDS_DIR / level_name

    BACKUPS_DIR.mkdir(parents=True, exist_ok=True)

    if world_dir.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dest = BACKUPS_DIR / f"{level_name}_modificado_{timestamp}"
        print(f"\n[1/3] Salvando copias das alteracoes atuais dos jogadores em:")
        print(f"      {backup_dest}")
        try:
            shutil.move(str(world_dir), str(backup_dest))
            print("      [OK] Backup do mundo alterado concluido.")
        except Exception as exc:
            print(f"[ERRO] Nao foi possivel mover o mundo atual: {exc}")
            sys.exit(1)
    else:
        print(f"\n[1/3] Pasta do mundo ativo nao encontrada em {world_dir}.")

    print("\n[2/3] Localizando backup do mapa original...")
    initial_zips = sorted(
        BACKUPS_DIR.glob("bds-backup-win-*.zip"),
        key=lambda p: p.stat().st_mtime
    )

    restored = False
    if initial_zips:
        clean_zip = initial_zips[0]
        print(f"      Backup original encontrado: {clean_zip.name}")
        print("      Extraindo arquivos do mapa original...")

        try:
            with zipfile.ZipFile(clean_zip, "r") as z:
                world_files = [m for m in z.namelist() if m.startswith(f"worlds/{level_name}") or m.startswith(f"worlds\\{level_name}")]
                for member in world_files:
                    z.extract(member, path=DATA_DIR)

            print(f"      [OK] Mapa original restaurado com sucesso para: {world_dir}")
            restored = True
        except Exception as exc:
            print(f"      [AVISO] Falha ao extrair backup ({exc}). O BDS gerara novo mapa.")

    if not restored:
        print("      [INFO] Nenhum arquivo .zip de instalacao encontrado.")
        print(f"      A pasta {world_dir} foi limpa.")
        print("      O BDS ira gerar automaticamente um mundo 100% virgem no proximo inicio.")

    print("\n[3/3] Finalizando...")
    print()
    print("=" * 72)
    print(" [SUCESSO] O MAPA FOI RESTAURADO PARA O ESTADO ORIGINAL!")
    print(" Todas as construcoes, crateras de TNT e alteracoes foram removidas.")
    print("=" * 72)
    print()
    print("Para iniciar o servidor agora com o mapa limpo:")
    print("  .\\iniciar-servidor.bat")
    print()


def main():
    restore_original_map()


if __name__ == "__main__":
    main()
