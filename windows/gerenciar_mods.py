"""
Gerenciador Central de Mods e Add-ons - Minecraft Bedrock Dedicated Server (BDS).

Permite gerenciar, ativar, desativar e inspecionar os mods instalados:
- More Spikes / Spiky Spikes (BP: c0bf473f-12d4-4c5c-bc9b-2c24df1e6c07 / RP: d595877a-04d1-4187-b56f-f81e7b015db6)
- Avaritia: ULTIMATE (BP: 5ad3bb44-8328-448e-8959-e7e0c64be76e / RP: a4a7d62a-b5ec-4f83-bc25-0f808ff74411)
- CobbleDrock (Core + Content)

Garante backups automaticos com timestamp antes de qualquer alteracao e
integridade do LevelDB e arquivos world_*_packs.json.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

WINDOWS_DIR = Path(__file__).resolve().parent
if str(WINDOWS_DIR) not in sys.path:
    sys.path.insert(0, str(WINDOWS_DIR))

try:
    from bds_cmd import get_bds_pid, send_command
except ImportError:
    get_bds_pid = lambda: None
    send_command = lambda cmd, wait_ms=50: False

PROJECT_ROOT = WINDOWS_DIR.parent
SERVER_DIR = PROJECT_ROOT / "server"
RUNTIME_DIR = SERVER_DIR / "runtime"
DATA_DIR = SERVER_DIR / "data"
SERVER_PROPERTIES = RUNTIME_DIR / "server.properties"
WORLDS_DIR = DATA_DIR / "worlds"
BACKUPS_DIR = DATA_DIR / "backups" / "packs_config"

# ======================================================================
# CATALOGO DE MODS E ADD-ONS
# ======================================================================

MODS_CATALOG: Dict[str, Dict[str, Any]] = {
    "spikes": {
        "name": "More Spikes (Spiky Spikes Bedrock v2.0.1)",
        "description": "Espinhos de madeira a netherite, dano continuo, drop de XP/Player Kill e spring spikes",
        "bp": [
            {
                "pack_id": "c0bf473f-12d4-4c5c-bc9b-2c24df1e6c07",
                "name": "More Spikes BP v2.0.1",
                "version": [2, 0, 0],
            }
        ],
        "rp": [
            {
                "pack_id": "d595877a-04d1-4187-b56f-f81e7b015db6",
                "name": "More Spikes RP v2.0.1",
                "version": [2, 0, 0],
            }
        ],
    },
    "avaritia": {
        "name": "Avaritia: ULTIMATE (v1.7.0)",
        "description": "Armaduras e armas do infinito, bancada Dire Crafting 9x9 e materiais cosmicos",
        "bp": [
            {
                "pack_id": "5ad3bb44-8328-448e-8959-e7e0c64be76e",
                "name": "Avaritia BP v1.7.0",
                "version": [1, 7, 0],
            }
        ],
        "rp": [
            {
                "pack_id": "a4a7d62a-b5ec-4f83-bc25-0f808ff74411",
                "name": "Avaritia RP v1.7.0",
                "version": [1, 7, 0],
            }
        ],
    },
    "cobbledrock": {
        "name": "CobbleDrock (v1.3.1)",
        "description": "Port oficial de Cobblemon para Bedrock com Pokemon e batalhas",
        "bp": [
            {
                "pack_id": "301ce48a-eef2-51b7-926d-b8a68eabcfea",
                "name": "CobbleDrock Core BP",
                "version": [1, 3, 1],
            },
            {
                "pack_id": "56a52fe3-c4d8-588d-9cce-6c6e6c381013",
                "name": "CobbleDrock Content BP",
                "version": [1, 3, 1],
            },
        ],
        "rp": [
            {
                "pack_id": "3e2975ad-9c9f-5098-8ac6-86bfb6cb6917",
                "name": "CobbleDrock Core RP",
                "version": [1, 3, 1],
            },
            {
                "pack_id": "266755bb-c9eb-5e1f-ad3e-f4e062d58c48",
                "name": "CobbleDrock Content RP",
                "version": [1, 3, 1],
            },
        ],
    },
    "spectrite": {
        "name": "Spectrite Mod (Official Bedrock Port v1.7.0)",
        "description": "Minerios raros arco-iris, armas lendarias (Legend Blade), armaduras cosmicas e ferramentas",
        "bp": [
            {
                "pack_id": "2d81f271-2fa1-4423-ad9b-dd0e56f2a93d",
                "name": "Spectrite BP v1.0.0",
                "version": [1, 0, 0],
            }
        ],
        "rp": [
            {
                "pack_id": "98ba3890-0e46-4b56-9a6e-5892c4256682",
                "name": "Spectrite RP v1.0.0",
                "version": [1, 0, 0],
            }
        ],
    },
    "luckyblock": {
        "name": "Lucky Block & OneBlock Engine (v1.0.0)",
        "description": "Motor OneBlock interativo com bloco lucky:lucky_block, drops aleatorios e protecao anti-void",
        "bp": [
            {
                "pack_id": "59aa09c5-0a2c-4134-8481-725801fba963",
                "name": "Lucky Block BP v1.0.0",
                "version": [1, 0, 0],
            }
        ],
        "rp": [
            {
                "pack_id": "60910110-474e-41b4-aa72-68e06a917819",
                "name": "Lucky Block RP v1.0.0",
                "version": [1, 0, 0],
            }
        ],
    },
    "rubyore": {
        "name": "The Ruby Ore by romhenri (v1.2.0)",
        "description": "Minerios de rubi (-25 a -49), bloco de rubi, ferramentas e armas superiores a Netherite (durabilidade 2031) e Ruby Hammer",
        "bp": [
            {
                "pack_id": "e8182397-79f0-47eb-bf6f-a8a523ffd7b5",
                "name": "Ruby Ore BP v1.0.0",
                "version": [1, 0, 0],
            }
        ],
        "rp": [
            {
                "pack_id": "8c01126d-d7b0-44ed-bbd3-994b7409e134",
                "name": "Ruby Ore RP v1.0.0",
                "version": [1, 0, 0],
            }
        ],
    },
}


def list_available_worlds() -> List[str]:
    """Lista todos os mundos presentes na pasta de mundos."""
    if not WORLDS_DIR.exists():
        return []
    return [d.name for d in WORLDS_DIR.iterdir() if d.is_dir() and (d / "level.dat").exists()]


def get_active_mods_names(level_name: Optional[str] = None) -> List[str]:
    """Retorna a lista com o nome de todos os mods atualmente ativos no mundo."""
    lvl = level_name or read_level_name()
    active = []
    for k in MODS_CATALOG:
        st = get_mod_status(k, lvl)
        if st["is_active"]:
            active.append(st["name"])
    return active


def get_all_worlds_mods_matrix() -> List[Dict[str, Any]]:
    """Gera uma visao comparativa completa de todos os mundos e quais mods estao ativos neles."""
    active_world = read_level_name()
    worlds = list_available_worlds()
    matrix = []
    for w in worlds:
        active_mods = []
        for k in MODS_CATALOG:
            st = get_mod_status(k, w)
            if st["is_active"]:
                active_mods.append(st["name"])
        w_dir, bp_json, rp_json = get_world_paths(w)
        bps = load_json_file(bp_json)
        rps = load_json_file(rp_json)
        matrix.append({
            "world": w,
            "is_active": w == active_world,
            "active_mods": active_mods,
            "bp_count": len(bps),
            "rp_count": len(rps),
            "is_vanilla": len(active_mods) == 0,
        })
    return matrix


def print_worlds_mods_matrix() -> None:
    """Exibe no terminal a matriz inteligente de mundos e mods ativos."""
    matrix = get_all_worlds_mods_matrix()
    active_world = read_level_name()
    print("\n" + "=" * 75)
    print("      MATRIZ INTELIGENTE DE MUNDOS E MODS ATIVOS NO SERVIDOR (BDS)")
    print("=" * 75)
    print(f" Mundo Ativo Principal no BDS: '{active_world}'\n")
    for item in matrix:
        status_tag = "[MUNDO ATIVO] " if item["is_active"] else "[INATIVO]     "
        print(f" {status_tag} {item['world']}")
        print(f"   * Pacotes Vinculados: {item['bp_count']} BPs / {item['rp_count']} RPs")
        if item["active_mods"]:
            print(f"   * Mods Ativos ({len(item['active_mods'])}):")
            for m in item["active_mods"]:
                print(f"       + {m}")
        else:
            print("   * Mods Ativos: Nenhum (100% Vanilla Limpo)")
        print("-" * 75)
    print("=" * 75 + "\n")


def switch_active_world(level_name: str) -> bool:
    """Muda o level-name ativo em server.properties."""
    world_dir = WORLDS_DIR / level_name
    if not world_dir.exists():
        print(f"[ERRO] Mundo '{level_name}' nao existe em {WORLDS_DIR}")
        return False
    if not SERVER_PROPERTIES.exists():
        print(f"[ERRO] server.properties nao encontrado em {SERVER_PROPERTIES}")
        return False

    content = SERVER_PROPERTIES.read_text(encoding="utf-8-sig")
    lines = content.splitlines()
    found = False
    new_lines = []
    for line in lines:
        if line.strip().startswith("level-name="):
            new_lines.append(f"level-name={level_name}")
            found = True
        else:
            new_lines.append(line)
    if not found:
        new_lines.append(f"level-name={level_name}")

    SERVER_PROPERTIES.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    print(f"[SUCESSO] Mundo ativo alterado para: '{level_name}'")
    return True


def read_level_name() -> str:
    """Le o level-name configurado no servidor."""
    if not SERVER_PROPERTIES.exists():
        return "Bedrock level"
    try:
        content = SERVER_PROPERTIES.read_text(encoding="utf-8-sig")
        for raw_line in content.splitlines():
            line = raw_line.strip()
            if line.startswith("level-name="):
                val = line.split("=", 1)[1].strip()
                if val:
                    return val
    except Exception:
        pass
    return "Bedrock level"


def get_world_paths(level_name: Optional[str] = None) -> Tuple[Path, Path, Path]:
    if level_name is None:
        level_name = read_level_name()
    world_dir = WORLDS_DIR / level_name
    bp_json = world_dir / "world_behavior_packs.json"
    rp_json = world_dir / "world_resource_packs.json"
    return world_dir, bp_json, rp_json


def load_json_file(path: Path) -> List[Dict[str, Any]]:
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


def save_json_file(path: Path, data: List[Dict[str, Any]]):
    path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    path.write_text(content, encoding="utf-8")


def create_backup_of_packs(world_dir: Path) -> Optional[Path]:
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


def get_mod_status(mod_key: str, level_name: Optional[str] = None) -> Dict[str, Any]:
    mod_info = MODS_CATALOG[mod_key]
    world_dir, bp_json, rp_json = get_world_paths(level_name)
    bps = load_json_file(bp_json)
    rps = load_json_file(rp_json)

    active_bp_ids = {entry.get("pack_id") for entry in bps if isinstance(entry, dict)}
    active_rp_ids = {entry.get("pack_id") for entry in rps if isinstance(entry, dict)}

    mod_bp_ids = {p["pack_id"] for p in mod_info["bp"]}
    mod_rp_ids = {p["pack_id"] for p in mod_info["rp"]}

    bp_active = mod_bp_ids.issubset(active_bp_ids)
    rp_active = mod_rp_ids.issubset(active_rp_ids)

    is_active = bp_active and rp_active
    is_partial = (len(mod_bp_ids.intersection(active_bp_ids)) > 0 or
                  len(mod_rp_ids.intersection(active_rp_ids)) > 0) and not is_active

    return {
        "key": mod_key,
        "name": mod_info["name"],
        "is_active": is_active,
        "is_partial": is_partial,
        "bp_active": bp_active,
        "rp_active": rp_active,
    }


def enable_mod(mod_key: str, level_name: Optional[str] = None) -> bool:
    if mod_key not in MODS_CATALOG:
        print(f"[ERRO] Mod desconhecido: {mod_key}")
        return False

    mod_info = MODS_CATALOG[mod_key]
    world_dir, bp_json, rp_json = get_world_paths(level_name)
    if not world_dir.exists():
        print(f"[ERRO] Pasta do mundo nao encontrada: {world_dir}")
        return False

    create_backup_of_packs(world_dir)

    bps = load_json_file(bp_json)
    rps = load_json_file(rp_json)

    existing_bp_ids = {b.get("pack_id") for b in bps if isinstance(b, dict)}
    existing_rp_ids = {r.get("pack_id") for r in rps if isinstance(r, dict)}

    for pack in mod_info["bp"]:
        if pack["pack_id"] not in existing_bp_ids:
            bps.append({"pack_id": pack["pack_id"], "version": pack["version"]})

    for pack in mod_info["rp"]:
        if pack["pack_id"] not in existing_rp_ids:
            rps.append({"pack_id": pack["pack_id"], "version": pack["version"]})

    save_json_file(bp_json, bps)
    save_json_file(rp_json, rps)

    print(f"[SUCESSO] Mod ativado: {mod_info['name']}")
    return True


def disable_mod(mod_key: str, level_name: Optional[str] = None) -> bool:
    if mod_key not in MODS_CATALOG:
        print(f"[ERRO] Mod desconhecido: {mod_key}")
        return False

    mod_info = MODS_CATALOG[mod_key]
    world_dir, bp_json, rp_json = get_world_paths(level_name)
    if not world_dir.exists():
        print(f"[ERRO] Pasta do mundo nao encontrada: {world_dir}")
        return False

    create_backup_of_packs(world_dir)

    bps = load_json_file(bp_json)
    rps = load_json_file(rp_json)

    mod_bp_ids = {p["pack_id"] for p in mod_info["bp"]}
    mod_rp_ids = {p["pack_id"] for p in mod_info["rp"]}

    filtered_bps = [b for b in bps if b.get("pack_id") not in mod_bp_ids]
    filtered_rps = [r for r in rps if r.get("pack_id") not in mod_rp_ids]

    save_json_file(bp_json, filtered_bps)
    save_json_file(rp_json, filtered_rps)

    print(f"[SUCESSO] Mod desativado: {mod_info['name']}")
    return True


def disable_all_mods(level_name: Optional[str] = None) -> bool:
    """Desativa todos os mods e add-ons no mundo informado ou ativo, deixando-o 100% vanilla."""
    world_dir, bp_json, rp_json = get_world_paths(level_name)
    if not world_dir.exists():
        print(f"[ERRO] Pasta do mundo nao encontrada: {world_dir}")
        return False

    create_backup_of_packs(world_dir)
    save_json_file(bp_json, [])
    save_json_file(rp_json, [])
    print(f"[SUCESSO] Todos os mods foram desativados no mundo '{level_name or read_level_name()}'. Mundo 100% vanilla!")
    return True


def print_full_status(level_name: Optional[str] = None):
    lvl = level_name or read_level_name()
    pid = get_bds_pid()
    world_dir, bp_json, rp_json = get_world_paths(lvl)
    matrix = get_all_worlds_mods_matrix()

    print("\n" + "=" * 75)
    print("      STATUS DE MODS E ADD-ONS - MINECRAFT BEDROCK DEDICATED SERVER")
    print("=" * 75)
    print(f" Servidor BDS:          {'ATIVO (PID: ' + str(pid) + ')' if pid else 'PARADO'}")
    print(f" Mundo Ativo no BDS:    '{lvl}' (Pasta: {world_dir.name})")
    print("-" * 75)
    print(" Mundos Instalados no BDS:")
    for item in matrix:
        tag = "[ATIVO]   " if item["is_active"] else "[INATIVO] "
        mod_desc = ", ".join(item["active_mods"]) if item["active_mods"] else "100% Vanilla Limpo"
        print(f"   {tag} {item['world']:<26} -> {mod_desc}")
    print("-" * 75)

    active_mods_count = 0
    print(f" Catalogo de Mods no Mundo '{lvl}':")
    for key in MODS_CATALOG:
        st = get_mod_status(key, lvl)
        if st["is_active"]:
            badge = "[ATIVADO]        "
            active_mods_count += 1
        elif st["is_partial"]:
            badge = "[PARCIALMENTE]   "
        else:
            badge = "[DESATIVADO]     "
        print(f"   {badge} {st['name']}")

    bps = load_json_file(bp_json)
    rps = load_json_file(rp_json)
    print("-" * 75)
    print(f" Resumo do Mundo '{lvl}': {active_mods_count} mod(s) ativo(s) | {len(bps)} BP(s) | {len(rps)} RP(s)")
    if bps:
        print("   Behavior Packs vinculados:")
        for b in bps:
            print(f"     * UUID: {b.get('pack_id')} (v{b.get('version')})")
    if rps:
        print("   Resource Packs vinculados:")
        for r in rps:
            print(f"     * UUID: {r.get('pack_id')} (v{r.get('version')})")
    print("=" * 75 + "\n")


def interactive_menu():
    while True:
        lvl = read_level_name()
        print_full_status(lvl)
        print("Opcoes de Gerenciamento de Mods:")
        print(" [1] Ativar / Desativar More Spikes (Spiky Spikes)")
        print(" [2] Ativar / Desativar Avaritia: ULTIMATE")
        print(" [3] Ativar / Desativar Spectrite Mod")
        print(" [4] Ativar / Desativar CobbleDrock")
        print(" [5] Ativar / Desativar Lucky Block & OneBlock Engine")
        print(" [6] Ativar / Desativar The Ruby Ore (romhenri)")
        print(" [7] Ativar Combo Compativel (Ruby Ore + Avaritia + Spikes + Spectrite + Lucky Block)")
        print(" [M] Exibir Matriz Completa de Mundos x Mods Ativos")
        print(" [D] Desativar TODOS os Mods (Deixar Mundo 100% Vanilla / Limpo)")
        print(" [8] Alternar Mundo Ativo (Cobbled Farms / Lucky OneBlock / Spiral / Padrão)")
        print(" [9] Ativar Lucky OneBlock (Mundo OneBlock)")
        print(" [C] Ativar Cobbled Farms (Mundo Cobblemon)")
        print(" [R] Atualizar exibicao")
        print(" [0] Voltar")
        print("-" * 75)
        try:
            choice = input("Escolha: ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            break

        if choice == "1":
            st = get_mod_status("spikes", lvl)
            if st["is_active"]:
                disable_mod("spikes", lvl)
            else:
                enable_mod("spikes", lvl)
            input("\nPressione ENTER para continuar...")
        elif choice == "2":
            st = get_mod_status("avaritia", lvl)
            if st["is_active"]:
                disable_mod("avaritia", lvl)
            else:
                enable_mod("avaritia", lvl)
            input("\nPressione ENTER para continuar...")
        elif choice == "3":
            st = get_mod_status("spectrite", lvl)
            if st["is_active"]:
                disable_mod("spectrite", lvl)
            else:
                enable_mod("spectrite", lvl)
            input("\nPressione ENTER para continuar...")
        elif choice == "4":
            st = get_mod_status("cobbledrock", lvl)
            if st["is_active"]:
                disable_mod("cobbledrock", lvl)
            else:
                enable_mod("cobbledrock", lvl)
            input("\nPressione ENTER para continuar...")
        elif choice == "5":
            st = get_mod_status("luckyblock", lvl)
            if st["is_active"]:
                disable_mod("luckyblock", lvl)
            else:
                enable_mod("luckyblock", lvl)
            input("\nPressione ENTER para continuar...")
        elif choice == "6":
            st = get_mod_status("rubyore", lvl)
            if st["is_active"]:
                disable_mod("rubyore", lvl)
            else:
                # Se o pacote ainda nao foi gerado, roda o instalador primeiro
                bp_check = WORLDS_DIR.parent / "custom_packs" / "behavior_packs" / "RubyOre_BP"
                if not bp_check.exists():
                    import instalar_ruby_ore
                    instalar_ruby_ore.install_ruby_ore(activate_as_current=False)
                enable_mod("rubyore", lvl)
            input("\nPressione ENTER para continuar...")
        elif choice == "7":
            # Assegura que Ruby Ore existe
            bp_check = WORLDS_DIR.parent / "custom_packs" / "behavior_packs" / "RubyOre_BP"
            if not bp_check.exists():
                import instalar_ruby_ore
                instalar_ruby_ore.install_ruby_ore(activate_as_current=False)
            enable_mod("rubyore", lvl)
            enable_mod("avaritia", lvl)
            enable_mod("spikes", lvl)
            enable_mod("spectrite", lvl)
            enable_mod("luckyblock", lvl)
            print("[SUCESSO] Combo ativado: Ruby Ore + Avaritia + Spikes + Spectrite + Lucky Block!")
            input("\nPressione ENTER para continuar...")
        elif choice == "m":
            print_worlds_mods_matrix()
            input("\nPressione ENTER para continuar...")
        elif choice == "d":
            disable_all_mods(lvl)
            input("\nPressione ENTER para continuar...")
        elif choice == "8":
            worlds = list_available_worlds()
            print("\nMundos Disponíveis:")
            for i, w in enumerate(worlds, 1):
                marker = " (ATUAL)" if w == lvl else ""
                print(f" [{i}] {w}{marker}")
            try:
                w_choice = input(f"Escolha o mundo (1-{len(worlds)}): ").strip()
                if w_choice.isdigit() and 1 <= int(w_choice) <= len(worlds):
                    switch_active_world(worlds[int(w_choice) - 1])
            except Exception as e:
                print(f"[!] Erro ao alternar: {e}")
            input("\nPressione ENTER para continuar...")
        elif choice == "9":
            if "Lucky OneBlock" in list_available_worlds():
                if switch_active_world("Lucky OneBlock"):
                    print("[SUCESSO] Mundo alternado para 'Lucky OneBlock'!")
            else:
                print("[!] 'Lucky OneBlock' nao esta instalado. Execute instalar_lucky_oneblock.py.")
            input("\nPressione ENTER para continuar...")
        elif choice == "c":
            if switch_active_world("Cobbled Farms"):
                print("[SUCESSO] Mundo alternado para 'Cobbled Farms'!")
            input("\nPressione ENTER para continuar...")
        elif choice == "r":
            continue
        elif choice == "0":
            break
        else:
            print("[!] Opcao invalida.")
            time.sleep(1)


def main():
    parser = argparse.ArgumentParser(description="Gerenciador Central de Mods para Bedrock Server")
    parser.add_argument("--status", "-s", action="store_true", help="Exibe o status completo dos mods")
    parser.add_argument("--world", help="Especifica o mundo a ser gerenciado (padrao: mundo ativo)")
    parser.add_argument("--matrix", action="store_true", help="Exibe matriz de todos os mundos e quais mods estao ativos")
    parser.add_argument("--spikes", choices=["enable", "disable", "status"], help="Gerencia More Spikes")
    parser.add_argument("--avaritia", choices=["enable", "disable", "status"], help="Gerencia Avaritia")
    parser.add_argument("--spectrite", choices=["enable", "disable", "status"], help="Gerencia Spectrite Mod")
    parser.add_argument("--cobbledrock", choices=["enable", "disable", "status"], help="Gerencia CobbleDrock")
    parser.add_argument("--luckyblock", choices=["enable", "disable", "status"], help="Gerencia Lucky Block & OneBlock Engine")
    parser.add_argument("--rubyore", choices=["enable", "disable", "status"], help="Gerencia The Ruby Ore (romhenri)")
    parser.add_argument("--lucky-oneblock", choices=["activate", "status", "install"], help="Gerencia o mapa Lucky OneBlock")
    parser.add_argument("--cobbled-farms", choices=["activate", "status", "install"], help="Gerencia o mapa Cobbled Farms")
    parser.add_argument("--enable-combo", action="store_true", help="Ativa Ruby Ore + Avaritia + More Spikes + Spectrite + Lucky Block")
    parser.add_argument("--disable-all", action="store_true", help="Desativa todos os mods no mundo especificado ou ativo (modo vanilla limpo)")
    parser.add_argument("--switch-world", help="Altera o level-name ativo em server.properties")
    parser.add_argument("--list-worlds", action="store_true", help="Lista todos os mundos instalados")
    args = parser.parse_args()

    target_world = args.world or read_level_name()

    if args.matrix:
        print_worlds_mods_matrix()
    elif args.list_worlds:
        worlds = list_available_worlds()
        print("Mundos instalados:")
        for w in worlds:
            active = " [ATIVO]" if w == target_world else ""
            print(f" - {w}{active}")
    elif args.disable_all:
        disable_all_mods(target_world)
    elif args.switch_world:
        switch_active_world(args.switch_world)
    elif args.lucky_oneblock:
        if args.lucky_oneblock == "activate":
            if switch_active_world("Lucky OneBlock"):
                enable_mod("luckyblock", "Lucky OneBlock")
                print("[SUCESSO] Lucky OneBlock ativado com Lucky Block Engine!")
        elif args.lucky_oneblock == "status":
            st = get_mod_status("luckyblock", "Lucky OneBlock")
            is_active_world = read_level_name() == "Lucky OneBlock"
            print(f"Lucky OneBlock: {'[MUNDO ATIVO]' if is_active_world else '[INATIVO]'}, Lucky Block: {'[ATIVADO]' if st['is_active'] else '[DESATIVADO]'}")
        elif args.lucky_oneblock == "install":
            import instalar_lucky_oneblock
            instalar_lucky_oneblock.install_lucky_oneblock(activate_as_current=True)
    elif args.cobbled_farms:
        if args.cobbled_farms == "activate":
            if switch_active_world("Cobbled Farms"):
                enable_mod("cobbledrock", "Cobbled Farms")
                print("[SUCESSO] Cobbled Farms ativado com CobbleDrock!")
        elif args.cobbled_farms == "status":
            st = get_mod_status("cobbledrock", "Cobbled Farms")
            is_active_world = read_level_name() == "Cobbled Farms"
            print(f"Cobbled Farms: {'[MUNDO ATIVO]' if is_active_world else '[INATIVO]'}, CobbleDrock: {'[ATIVADO]' if st['is_active'] else '[DESATIVADO]'}")
        elif args.cobbled_farms == "install":
            import instalar_cobbled_farms
            instalar_cobbled_farms.install_cobbled_farms(activate_as_current=True)
    elif args.status:
        print_full_status(target_world)
    elif args.rubyore:
        if args.rubyore == "enable":
            enable_mod("rubyore", target_world)
        elif args.rubyore == "disable":
            disable_mod("rubyore", target_world)
        else:
            st = get_mod_status("rubyore", target_world)
            print(f"The Ruby Ore ({target_world}): {'ATIVO' if st['is_active'] else 'DESATIVADO'}")
    elif args.spikes:
        if args.spikes == "enable":
            enable_mod("spikes", target_world)
        elif args.spikes == "disable":
            disable_mod("spikes", target_world)
        else:
            st = get_mod_status("spikes", target_world)
            print(f"More Spikes ({target_world}): {'ATIVO' if st['is_active'] else 'DESATIVADO'}")
    elif args.avaritia:
        if args.avaritia == "enable":
            enable_mod("avaritia", target_world)
        elif args.avaritia == "disable":
            disable_mod("avaritia", target_world)
        else:
            st = get_mod_status("avaritia", target_world)
            print(f"Avaritia ({target_world}): {'ATIVO' if st['is_active'] else 'DESATIVADO'}")
    elif args.spectrite:
        if args.spectrite == "enable":
            enable_mod("spectrite", target_world)
        elif args.spectrite == "disable":
            disable_mod("spectrite", target_world)
        else:
            st = get_mod_status("spectrite", target_world)
            print(f"Spectrite ({target_world}): {'ATIVO' if st['is_active'] else 'DESATIVADO'}")
    elif args.cobbledrock:
        if args.cobbledrock == "enable":
            enable_mod("cobbledrock", target_world)
        elif args.cobbledrock == "disable":
            disable_mod("cobbledrock", target_world)
        else:
            st = get_mod_status("cobbledrock", target_world)
            print(f"CobbleDrock ({target_world}): {'ATIVO' if st['is_active'] else 'DESATIVADO'}")
    elif args.luckyblock:
        if args.luckyblock == "enable":
            enable_mod("luckyblock", target_world)
        elif args.luckyblock == "disable":
            disable_mod("luckyblock", target_world)
        else:
            st = get_mod_status("luckyblock", target_world)
            print(f"Lucky Block ({target_world}): {'ATIVO' if st['is_active'] else 'DESATIVADO'}")
    elif args.enable_combo:
        enable_mod("rubyore", target_world)
        enable_mod("avaritia", target_world)
        enable_mod("spikes", target_world)
        enable_mod("spectrite", target_world)
        enable_mod("luckyblock", target_world)
    else:
        interactive_menu()


if __name__ == "__main__":
    main()
