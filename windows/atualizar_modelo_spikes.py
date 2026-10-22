"""
Script para transformar o modelo dos espinhos no modelo 3D Pyramid exato do Spiky Spikes,
utilizando texturas oficiais de blocos (Carvalho, Pedra, Ferro, Ouro, Diamante, Netherite, Cobre)
e geometria piramidal ultra-detalhada de 32 niveis.
"""

from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT_DIR = Path(__file__).resolve().parent.parent
SERVER_DIR = ROOT_DIR / "server"
RP_DATA = SERVER_DIR / "data" / "custom_packs" / "resource_packs" / "MoreSpikes_RP"
RP_RUNTIME = SERVER_DIR / "runtime" / "development_resource_packs" / "MoreSpikes_RP"
BP_DATA = SERVER_DIR / "data" / "custom_packs" / "behavior_packs" / "MoreSpikes_BP"
BP_RUNTIME = SERVER_DIR / "runtime" / "development_behavior_packs" / "MoreSpikes_BP"


def generate_pyramid_geometry() -> dict:
    cubes = []
    for i in range(32):
        width = 16.0 - (i * 0.5)
        h = 0.5
        y = float(i) * 0.5
        half = width / 2.0
        x0 = -half
        z0 = -half

        u_x = 8.0 - half
        u_y = y

        face_uv = {
            "north": {"uv": [round(u_x, 2), round(u_y, 2)], "uv_size": [round(width, 2), round(h, 2)]},
            "east":  {"uv": [round(u_x, 2), round(u_y, 2)], "uv_size": [round(width, 2), round(h, 2)]},
            "south": {"uv": [round(u_x, 2), round(u_y, 2)], "uv_size": [round(width, 2), round(h, 2)]},
            "west":  {"uv": [round(u_x, 2), round(u_y, 2)], "uv_size": [round(width, 2), round(h, 2)]},
            "up":    {"uv": [round(u_x, 2), round(u_x, 2)], "uv_size": [round(width, 2), round(width, 2)]},
        }
        if i == 0:
            face_uv["down"] = {"uv": [0.0, 0.0], "uv_size": [16.0, 16.0]}
        else:
            face_uv["down"] = {"uv": [round(u_x, 2), round(u_x, 2)], "uv_size": [round(width, 2), round(width, 2)]}

        cube = {
            "origin": [round(x0, 2), round(y, 2), round(z0, 2)],
            "size": [round(width, 2), round(h, 2), round(width, 2)],
            "uv": face_uv,
        }
        cubes.append(cube)

    return {
        "format_version": "1.16.0",
        "minecraft:geometry": [
            {
                "description": {
                    "identifier": "geometry.dici",
                    "texture_width": 16,
                    "texture_height": 16,
                    "visible_bounds_width": 2,
                    "visible_bounds_height": 2.5,
                    "visible_bounds_offset": [0, 0.5, 0],
                },
                "bones": [
                    {
                        "name": "bb_main",
                        "pivot": [0, 0, 0],
                        "binding": "q.item_slot_to_bone_name(c.item_slot)",
                        "cubes": cubes,
                    }
                ],
            }
        ],
    }


def update_models():
    geo_data = generate_pyramid_geometry()
    for rp in [RP_DATA, RP_RUNTIME]:
        geo_file = rp / "models" / "blocks" / "dici.geo.json"
        geo_file.parent.mkdir(parents=True, exist_ok=True)
        geo_file.write_text(json.dumps(geo_data, indent=2), encoding="utf-8")
    print("[OK] Geometria 3D Pyramid aplicada em dici.geo.json (data e runtime)!")


def download_official_textures():
    base_url = "https://raw.githubusercontent.com/Mojang/bedrock-samples/main/resource_pack/textures/blocks/"
    texture_map = {
        "diamond_spike.png": "diamond_block.png",
        "gold_spike.png": "gold_block.png",
        "dici.png": "iron_block.png",
        "cobblestone_spike.png": "stone.png",
        "netherite_spike.png": "netherite_block.png",
        "copper_spike.png": "copper_block.png",
        "wooden_spikes/oak_spike.png": "planks_oak.png",
        "wooden_spikes/brich_spike.png": "planks_birch.png",
        "wooden_spikes/spruce_spike.png": "planks_spruce.png",
        "wooden_spikes/jungle_spike.png": "planks_jungle.png",
        "wooden_spikes/acacia_spike.png": "planks_acacia.png",
        "wooden_spikes/dark_oak_spike.png": "planks_big_oak.png",
        "wooden_spikes/mangrove_spike.png": "mangrove_planks.png",
        "wooden_spikes/cherry_spike.png": "cherry_planks.png",
        "wooden_spikes/bamboo_spike.png": "bamboo_planks.png",
        "wooden_spikes/crimson_spike.png": "huge_fungus/crimson_planks.png",
        "wooden_spikes/warped_spike.png": "huge_fungus/warped_planks.png",
    }

    for dest_rel, src_file in texture_map.items():
        url = base_url + src_file
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        try:
            with urllib.request.urlopen(req) as resp:
                data = resp.read()
                for rp in [RP_DATA, RP_RUNTIME]:
                    dest_path = rp / "textures" / "blocks" / dest_rel
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    dest_path.write_bytes(data)
                print(f"[OK] Textura oficial atualizada: {dest_rel} <- {src_file}")
        except Exception as exc:
            print(f"[!] Erro ao baixar textura {src_file}: {exc}")


def update_block_hitboxes():
    for bp in [BP_DATA, BP_RUNTIME]:
        normal_dir = bp / "blocks" / "normal"
        if not normal_dir.exists():
            continue
        for b_json in normal_dir.glob("*.json"):
            try:
                block_data = json.loads(b_json.read_text(encoding="utf-8-sig"))
                comps = block_data.get("minecraft:block", {}).get("components", {})
                comps["minecraft:selection_box"] = {
                    "origin": [-8, 0, -8],
                    "size": [16, 16, 16],
                }
                comps["minecraft:collision_box"] = {
                    "origin": [-8, 0, -8],
                    "size": [16, 15, 16],
                }
                b_json.write_text(json.dumps(block_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            except Exception as exc:
                print(f"[!] Erro ao atualizar {b_json.name}: {exc}")
    print("[OK] Hitboxes de selecao e colisao ajustadas para a altura total da piramide!")


def main():
    print("=" * 65)
    print("   ATUALIZANDO VISUAIS: MODELO E TEXTURAS SPIKY SPIKES   ")
    print("=" * 65)
    update_models()
    download_official_textures()
    update_block_hitboxes()
    print("=" * 65)
    print("Concluido com sucesso!")


if __name__ == "__main__":
    main()
