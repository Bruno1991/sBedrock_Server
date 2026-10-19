"""
Gerenciador e Desativador do Mod CobbleDrock - Minecraft Bedrock Dedicated Server.

Permite desativar, reativar e verificar o status dos pacotes do mod CobbleDrock:
- CobbleDrock Core (BP: 301ce48a-eef2-51b7-926d-b8a68eabcfea / RP: 3e2975ad-9c9f-5098-8ac6-86bfb6cb6917)
- CobbleDrock Content (BP: 56a52fe3-c4d8-588d-9cce-6c6e6c381013 / RP: 266755bb-c9eb-5e1f-ad3e-f4e062d58c48)

Preserva outros add-ons ativos (ex: Avaritia) e gera backup automatico antes de cada modificacao.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from datetime import datetime
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
# DEFINICOES DOS PACOTES DO COBBLEDROCK
# ======================================================================

COBBLEDROCK_PACKS = {
    "bp": [
        {
            "pack_id": "301ce48a-eef2-51b7-926d-b8a68eabcfea",
            "name": "CobbleDrock Core BP",
            "default_version": [1, 3, 1],
            "manifest_rel": "data/custom_packs/behavior_packs/CobbleDrock_Core_BP/manifest.json",
        },
        {
            "pack_id": "56a52fe3-c4d8-588d-9cce-6c6e6c381013",
            "name": "CobbleDrock Content BP",
            "default_version": [1, 3, 1],
            "manifest_rel": "data/custom_packs/behavior_packs/CobbleDrock_Content_BP/manifest.json",
        },
    ],
    "rp": [
        {
            "pack_id": "3e2975ad-9c9f-5098-8ac6-86bfb6cb6917",
            "name": "CobbleDrock Core RP",
            "default_version": [1, 3, 1],
            "manifest_rel": "data/custom_packs/resource_packs/CobbleDrock_Core_RP/manifest.json",
        },
        {
            "pack_id": "266755bb-c9eb-5e1f-ad3e-f4e062d58c48",
            "name": "CobbleDrock Content RP",
            "default_version": [1, 3, 1],
            "manifest_rel": "data/custom_packs/resource_packs/CobbleDrock_Content_RP/manifest.json",
        },
    ],
}

COBBLEDROCK_BP_IDS = {p["pack_id"] for p in COBBLEDROCK_PACKS["bp"]}
COBBLEDROCK_RP_IDS = {p["pack_id"] for p in COBBLEDROCK_PACKS["rp"]}

# ======================================================================
# CAMINHOS DO PROJETO
# ======================================================================

PROJECT_ROOT = WINDOWS_DIR.parent
SERVER_DIR = PROJECT_ROOT / "server"
RUNTIME_DIR = SERVER_DIR / "runtime"
DATA_DIR = SERVER_DIR / "data"
SERVER_PROPERTIES = RUNTIME_DIR / "server.properties"
WORLDS_DIR = DATA_DIR / "worlds"
BACKUPS_DIR = DATA_DIR / "backups" / "packs_config"


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


def get_world_paths(level_name: str | None = None) -> tuple[Path, Path, Path]:
    """Retorna os caminhos da pasta do mundo, world_behavior_packs.json e world_resource_packs.json."""
    if level_name is None:
        level_name = read_level_name()
    world_dir = WORLDS_DIR / level_name
    bp_json = world_dir / "world_behavior_packs.json"
    rp_json = world_dir / "world_resource_packs.json"
    return world_dir, bp_json, rp_json


def load_json_file(path: Path) -> list[dict]:
    """Le com seguranca um arquivo JSON de pacotes do mundo."""
    if not path.exists():
        return []
    try:
        content = path.read_text(encoding="utf-8-sig")
        data = json.loads(content)
        if isinstance(data, list):
            return data
    except Exception as exc:
        print(f"[AVISO] Falha ao ler {path.name}: {exc}")
    return []


def save_json_file(path: Path, data: list[dict]):
    """Grava formatado com identacao o arquivo JSON de pacotes."""
    path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    path.write_text(content, encoding="utf-8")


def resolve_pack_version(pack_info: dict) -> list[int]:
    """Tenta obter a versao real do manifest.json se presente no servidor."""
    manifest_path = SERVER_DIR / pack_info["manifest_rel"]
    if manifest_path.exists():
        try:
            data = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
            ver = data.get("header", {}).get("version")
            if isinstance(ver, list) and len(ver) == 3:
                return ver
        except Exception:
            pass
    return pack_info["default_version"]


def create_backup_of_packs(world_dir: Path) -> Path | None:
    """Cria copia de seguranca com timestamp dos arquivos de packs antes de alterar."""
    bp_json = world_dir / "world_behavior_packs.json"
    rp_json = world_dir / "world_resource_packs.json"

    if not bp_json.exists() and not rp_json.exists():
        return None

    BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_folder = BACKUPS_DIR / f"packs_{timestamp}"
    backup_folder.mkdir(parents=True, exist_ok=True)

    if bp_json.exists():
        shutil.copy2(bp_json, backup_folder / "world_behavior_packs.json")
    if rp_json.exists():
        shutil.copy2(rp_json, backup_folder / "world_resource_packs.json")

    return backup_folder


def get_cobbledrock_status(level_name: str | None = None) -> dict:
    """Verifica se o CobbleDrock esta ativado no mundo ativo."""
    world_dir, bp_json, rp_json = get_world_paths(level_name)
    bps = load_json_file(bp_json)
    rps = load_json_file(rp_json)

    active_bp_ids = {entry.get("pack_id") for entry in bps if isinstance(entry, dict)}
    active_rp_ids = {entry.get("pack_id") for entry in rps if isinstance(entry, dict)}

    cobble_bp_active = [p for p in COBBLEDROCK_PACKS["bp"] if p["pack_id"] in active_bp_ids]
    cobble_rp_active = [p for p in COBBLEDROCK_PACKS["rp"] if p["pack_id"] in active_rp_ids]

    other_bps = [b for b in bps if b.get("pack_id") not in COBBLEDROCK_BP_IDS]
    other_rps = [r for r in rps if r.get("pack_id") not in COBBLEDROCK_RP_IDS]

    is_active = len(cobble_bp_active) > 0 or len(cobble_rp_active) > 0
    is_complete = (len(cobble_bp_active) == len(COBBLEDROCK_PACKS["bp"]) and
                   len(cobble_rp_active) == len(COBBLEDROCK_PACKS["rp"]))

    return {
        "world_dir": world_dir,
        "bp_json": bp_json,
        "rp_json": rp_json,
        "is_active": is_active,
        "is_complete": is_complete,
        "cobble_bp_active": cobble_bp_active,
        "cobble_rp_active": cobble_rp_active,
        "other_bps": other_bps,
        "other_rps": other_rps,
        "total_bps": len(bps),
        "total_rps": len(rps),
    }


def stop_server_if_running() -> bool:
    """Encerra o servidor de forma limpa se estiver rodando."""
    pid = get_bds_pid()
    if not pid:
        return True

    print(f"[INFO] Servidor BDS detectado em execucao (PID: {pid}).")
    print("[INFO] Enviando comando 'stop' para desligamento seguro...")
    send_command("say [BDS] Atualizando configuracao de mods... Encerrando servidor.")
    send_command("stop")

    for _ in range(15):
        time.sleep(0.5)
        if not get_bds_pid():
            print("[OK] Servidor finalizado com sucesso.")
            return True

    print("[AVISO] Servidor ainda esta em execucao. Aguarde ou encerre-o manualmente.")
    return False


def disable_cobbledrock(level_name: str | None = None, auto_stop: bool = False) -> bool:
    """Desativa os pacotes do CobbleDrock no mundo ativo."""
    world_dir, bp_json, rp_json = get_world_paths(level_name)
    if not world_dir.exists():
        print(f"[ERRO] Pasta do mundo nao encontrada em: {world_dir}")
        return False

    pid = get_bds_pid()
    if pid:
        if auto_stop:
            stop_server_if_running()
        else:
            print(f"[AVISO] O servidor esta rodando (PID: {pid}).")
            print("        Recomenda-se fechar o servidor antes de alterar os pacotes.")

    status = get_cobbledrock_status(level_name)
    if not status["is_active"]:
        print("[INFO] CobbleDrock ja esta DESATIVADO no mundo atual.")
        return True

    # Criar backup antes de modificar
    backup_path = create_backup_of_packs(world_dir)
    if backup_path:
        print(f"[BACKUP] Copia de seguranca gerada em: {backup_path}")

    # Filtrar pacotes removendo CobbleDrock
    bps = load_json_file(bp_json)
    rps = load_json_file(rp_json)

    filtered_bps = [b for b in bps if b.get("pack_id") not in COBBLEDROCK_BP_IDS]
    filtered_rps = [r for r in rps if r.get("pack_id") not in COBBLEDROCK_RP_IDS]

    save_json_file(bp_json, filtered_bps)
    save_json_file(rp_json, filtered_rps)

    print("\n" + "=" * 65)
    print(" [SUCESSO] MOD COBBLEDROCK DESATIVADO COM SUCESSO!")
    print("=" * 65)
    print(f" Mundo: {world_dir.name}")
    print(f" Behavior Packs ativos restantes: {len(filtered_bps)}")
    for b in filtered_bps:
        print(f"   - Pack ID: {b.get('pack_id')} (v{b.get('version')})")
    print(f" Resource Packs ativos restantes: {len(filtered_rps)}")
    for r in filtered_rps:
        print(f"   - Pack ID: {r.get('pack_id')} (v{r.get('version')})")
    print("=" * 65 + "\n")
    return True


def enable_cobbledrock(level_name: str | None = None, auto_stop: bool = False) -> bool:
    """Reativa os pacotes do CobbleDrock no mundo ativo."""
    world_dir, bp_json, rp_json = get_world_paths(level_name)
    if not world_dir.exists():
        print(f"[ERRO] Pasta do mundo nao encontrada em: {world_dir}")
        return False

    pid = get_bds_pid()
    if pid:
        if auto_stop:
            stop_server_if_running()
        else:
            print(f"[AVISO] O servidor esta rodando (PID: {pid}).")

    backup_path = create_backup_of_packs(world_dir)
    if backup_path:
        print(f"[BACKUP] Copia de seguranca gerada em: {backup_path}")

    bps = load_json_file(bp_json)
    rps = load_json_file(rp_json)

    existing_bp_ids = {b.get("pack_id") for b in bps}
    existing_rp_ids = {r.get("pack_id") for r in rps}

    # Adicionar BPs do CobbleDrock
    for pack in COBBLEDROCK_PACKS["bp"]:
        if pack["pack_id"] not in existing_bp_ids:
            version = resolve_pack_version(pack)
            bps.insert(0, {"pack_id": pack["pack_id"], "version": version})

    # Adicionar RPs do CobbleDrock
    for pack in COBBLEDROCK_PACKS["rp"]:
        if pack["pack_id"] not in existing_rp_ids:
            version = resolve_pack_version(pack)
            rps.insert(0, {"pack_id": pack["pack_id"], "version": version})

    save_json_file(bp_json, bps)
    save_json_file(rp_json, rps)

    print("\n" + "=" * 65)
    print(" [SUCESSO] MOD COBBLEDROCK ATIVADO COM SUCESSO!")
    print("=" * 65)
    print(f" Mundo: {world_dir.name}")
    print(f" Total Behavior Packs: {len(bps)}")
    print(f" Total Resource Packs: {len(rps)}")
    print("=" * 65 + "\n")
    return True


def print_status(level_name: str | None = None):
    """Exibe no console o status detalhado do servidor e add-ons."""
    lvl = read_level_name() if level_name is None else level_name
    pid = get_bds_pid()
    status = get_cobbledrock_status(lvl)

    print()
    print("=" * 68)
    print("      STATUS DE ADD-ONS E MODS - MINECRAFT BEDROCK SERVER")
    print("=" * 68)
    print(f" Servidor BDS:    {'ATIVO (PID: ' + str(pid) + ')' if pid else 'PARADO'}")
    print(f" Mundo Ativo:     {lvl}")
    print(f" Pasta do Mundo:  {status['world_dir']}")
    print("-" * 68)

    if status["is_complete"]:
        print(" CobbleDrock:     [ATIVADO] - Todos os modulos (Core e Content) estao ativos.")
    elif status["is_active"]:
        print(" CobbleDrock:     [PARCIALMENTE ATIVO] - Apenas alguns modulos estao ativos.")
    else:
        print(" CobbleDrock:     [DESATIVADO] - Nenhum modulo do CobbleDrock carregado.")

    print(f"\n Detalhes Behavior Packs ({status['total_bps']} no total):")
    for bp in status["cobble_bp_active"]:
        print(f"   [CobbleDrock] {bp['name']} (UUID: {bp['pack_id']})")
    for b in status["other_bps"]:
        print(f"   [Outro Addon] Pack ID: {b.get('pack_id')} (v{b.get('version')})")

    print(f"\n Detalhes Resource Packs ({status['total_rps']} no total):")
    for rp in status["cobble_rp_active"]:
        print(f"   [CobbleDrock] {rp['name']} (UUID: {rp['pack_id']})")
    for r in status["other_rps"]:
        print(f"   [Outro Addon] Pack ID: {r.get('pack_id')} (v{r.get('version')})")

    print("=" * 68)
    print()


def interactive_menu():
    """Menu interativo para administracao via console."""
    while True:
        print_status()
        print("Opcoes disponiveis:")
        print("  [1] Desativar mod CobbleDrock")
        print("  [2] Ativar mod CobbleDrock")
        print("  [3] Atualizar status")
        print("  [0] Sair")
        print()

        try:
            choice = input("Escolha uma opcao (0-3): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nEncerrando.")
            break

        if choice == "1":
            confirm = input("Confirmar desativacao do CobbleDrock? (s/n): ").strip().lower()
            if confirm in ("s", "sim", "y", "yes"):
                disable_cobbledrock()
                input("\nPressione ENTER para continuar...")
        elif choice == "2":
            enable_cobbledrock()
            input("\nPressione ENTER para continuar...")
        elif choice == "3":
            continue
        elif choice == "0":
            break
        else:
            print("[AVISO] Opcao invalida. Digite 1, 2, 3 ou 0.")
            time.sleep(1)


def main():
    parser = argparse.ArgumentParser(
        description="Gerenciador e Desativador do Mod CobbleDrock para BDS Windows"
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--disable", "-d", action="store_true", help="Desativa o mod CobbleDrock")
    group.add_argument("--enable", "-e", action="store_true", help="Ativa o mod CobbleDrock")
    group.add_argument("--status", "-s", action="store_true", help="Exibe o status atual do CobbleDrock")

    parser.add_argument("--world", "-w", type=str, default=None, help="Nome do mundo (padrao: level-name do server.properties)")
    parser.add_argument("--stop-server", action="store_true", help="Para o servidor automaticamente se estiver rodando")

    args = parser.parse_args()

    if args.disable:
        disable_cobbledrock(level_name=args.world, auto_stop=args.stop_server)
    elif args.enable:
        enable_cobbledrock(level_name=args.world, auto_stop=args.stop_server)
    elif args.status:
        print_status(level_name=args.world)
    else:
        interactive_menu()


if __name__ == "__main__":
    main()
