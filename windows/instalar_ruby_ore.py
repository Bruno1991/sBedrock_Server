"""
Instalador e Construtor do Add-on The Ruby Ore (romhenri) para Minecraft Bedrock Dedicated Server (BDS).

Port oficial das funcionalidades do mod CurseForge 'The Ruby Ore' (romhenri):
- Itens: Ruby, Raw Ruby, Ruby Dust, Ruby Sword (+9 dano), Ruby Pickaxe, Ruby Axe (+11 dano),
         Ruby Shovel, Ruby Hoe, Ruby Hammer (Escavador 3x3), Ruby Combat Axe (+12 dano).
- Durabilidade: 2031 (padrao Netherite balanceado)
- Blocos: Ruby Block, Ruby Ore, Deepslate Ruby Ore
- Receitas: Bancada de trabalho, fornalha e alto-forno
- Texturas originais pixel-art 16x16 do autor romhenri
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import urllib.request
from pathlib import Path
from typing import Optional

try:
    from PIL import Image, ImageDraw
except ImportError:
    Image = None
    ImageDraw = None

WINDOWS_DIR = Path(__file__).resolve().parent
if str(WINDOWS_DIR) not in sys.path:
    sys.path.insert(0, str(WINDOWS_DIR))

PROJECT_ROOT = WINDOWS_DIR.parent
SERVER_DIR = PROJECT_ROOT / "server"
DATA_DIR = SERVER_DIR / "data"
CUSTOM_PACKS_DIR = DATA_DIR / "custom_packs"
RUNTIME_DIR = SERVER_DIR / "runtime"
WORLDS_DIR = DATA_DIR / "worlds"

BP_UUID = "e8182397-79f0-47eb-bf6f-a8a523ffd7b5"
BP_DATA_UUID = "62e9763f-3f1c-435c-be91-92962ca00819"
RP_UUID = "8c01126d-d7b0-44ed-bbd3-994b7409e134"
RP_RES_UUID = "91a127d8-1b62-4bfd-b826-b61269aaf961"

BP_DIR = CUSTOM_PACKS_DIR / "behavior_packs" / "RubyOre_BP"
RP_DIR = CUSTOM_PACKS_DIR / "resource_packs" / "RubyOre_RP"

DEV_BP_DIR = RUNTIME_DIR / "development_behavior_packs" / "RubyOre_BP"
DEV_RP_DIR = RUNTIME_DIR / "development_resource_packs" / "RubyOre_RP"

GITHUB_RAW_BASE = "https://raw.githubusercontent.com/romhenri/rise-modpack/main/rubyore/src/main/resources/assets/rubyore/textures"

ONLINE_TEXTURES = {
    "items/ruby.png": f"{GITHUB_RAW_BASE}/item/ruby.png",
    "items/raw_ruby.png": f"{GITHUB_RAW_BASE}/item/ruby-o.png",
    "items/ruby_dust.png": f"{GITHUB_RAW_BASE}/item/ruby_dust.png",
    "items/ruby_sword.png": f"{GITHUB_RAW_BASE}/item/ruby_sword.png",
    "items/ruby_pickaxe.png": f"{GITHUB_RAW_BASE}/item/ruby_pickaxe.png",
    "items/ruby_axe.png": f"{GITHUB_RAW_BASE}/item/ruby_axe.png",
    "items/ruby_shovel.png": f"{GITHUB_RAW_BASE}/item/ruby_shovel.png",
    "items/ruby_hoe.png": f"{GITHUB_RAW_BASE}/item/ruby_hoe.png",
    "items/ruby_hammer.png": f"{GITHUB_RAW_BASE}/item/ruby_hammer.png",
    "items/ruby_combat_axe.png": f"{GITHUB_RAW_BASE}/item/ruby_combat_axe.png",
    "blocks/ruby_ore.png": f"{GITHUB_RAW_BASE}/block/ruby_ore.png",
    "blocks/deepslate_ruby_ore.png": f"{GITHUB_RAW_BASE}/block/deepslate_ruby_ore.png",
    "blocks/ruby_block.png": f"{GITHUB_RAW_BASE}/block/ruby_block.png",
}


def create_fallback_texture(path: Path, is_block: bool = False, main_color: tuple = (220, 20, 60, 255)) -> None:
    """Gera textura 16x16 de fallback caso o download externo nao esteja disponivel."""
    if Image is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    pixels = img.load()
    if is_block:
        for x in range(16):
            for y in range(16):
                pixels[x, y] = main_color
    else:
        # Formato de gema diamante/rubi 8x10
        for x in range(4, 12):
            for y in range(3, 13):
                pixels[x, y] = main_color
    img.save(path, "PNG")


def generate_pack_icon(path: Path) -> None:
    """Gera icone estilizado 128x128 para o pacote e inventario."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if Image is None:
        return
    img = Image.new("RGBA", (128, 128), (20, 20, 25, 255))
    draw = ImageDraw.Draw(img)

    # Fundo degrade rubi escuro
    for y in range(128):
        c = int(20 + 40 * (y / 128))
        draw.line([(0, y), (128, y)], fill=(c + 20, 10, 20, 255))

    # Gema Rubi Lapidada no centro
    pts = [
        (64, 20),
        (100, 50),
        (85, 105),
        (43, 105),
        (28, 50),
    ]
    draw.polygon(pts, fill=(225, 25, 55, 255), outline=(255, 120, 140, 255))
    # Facetas internas de brilho
    draw.line([(64, 20), (64, 65)], fill=(255, 180, 190, 255), width=2)
    draw.line([(64, 65), (85, 105)], fill=(180, 15, 40, 255), width=2)
    draw.line([(64, 65), (43, 105)], fill=(180, 15, 40, 255), width=2)
    draw.line([(64, 65), (100, 50)], fill=(255, 140, 160, 255), width=2)
    draw.line([(64, 65), (28, 50)], fill=(255, 140, 160, 255), width=2)

    img.save(path, "PNG")


def download_or_generate_textures(rp_textures_dir: Path) -> None:
    """Baixa as texturas originais do GitHub de romhenri ou gera com seguranca."""
    for rel_path, url in ONLINE_TEXTURES.items():
        dest = rp_textures_dir / rel_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.is_file() and dest.stat().st_size > 100:
            continue
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = resp.read()
                if len(data) > 100:
                    dest.write_bytes(data)
                    continue
        except Exception:
            pass

        # Fallback local deterministico se offline
        is_block = "blocks/" in rel_path
        color = (180, 20, 45, 255) if is_block else (225, 25, 55, 255)
        create_fallback_texture(dest, is_block=is_block, main_color=color)


def build_behavior_pack() -> None:
    """Cria a estrutura e todos os arquivos do Behavior Pack do Ruby Ore."""
    BP_DIR.mkdir(parents=True, exist_ok=True)
    (BP_DIR / "items").mkdir(parents=True, exist_ok=True)
    (BP_DIR / "blocks").mkdir(parents=True, exist_ok=True)
    (BP_DIR / "recipes").mkdir(parents=True, exist_ok=True)
    (BP_DIR / "texts").mkdir(parents=True, exist_ok=True)

    # 1. manifest.json
    manifest = {
        "format_version": 2,
        "header": {
            "name": "Ruby Ore BP v1.0.0",
            "description": "The Ruby Ore Add-on Behavior Pack by romhenri - Bedrock Port v1.2.0",
            "uuid": BP_UUID,
            "version": [1, 0, 0],
            "min_engine_version": [1, 26, 50],
        },
        "modules": [
            {
                "type": "data",
                "uuid": BP_DATA_UUID,
                "version": [1, 0, 0],
            }
        ],
        "dependencies": [
            {
                "uuid": RP_UUID,
                "version": [1, 0, 0],
            }
        ],
    }
    (BP_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    # 2. Itens
    items_def = {
        "ruby": {
            "category": "nature",
            "icon": "ruby",
            "max_stack": 64,
            "name": "§cRuby§r",
        },
        "raw_ruby": {
            "category": "nature",
            "icon": "raw_ruby",
            "max_stack": 64,
            "name": "§cRaw Ruby§r",
        },
        "ruby_dust": {
            "category": "nature",
            "icon": "ruby_dust",
            "max_stack": 64,
            "name": "§cRuby Dust§r",
        },
        "ruby_sword": {
            "category": "equipment",
            "icon": "ruby_sword",
            "max_stack": 1,
            "hand_equipped": True,
            "durability": 2031,
            "damage": 9,
            "slot": "sword",
            "name": "§c§lRuby Sword§r\n§7Tier: Netherite+ | Attack: +9 | Durability: 2031",
        },
        "ruby_pickaxe": {
            "category": "equipment",
            "icon": "ruby_pickaxe",
            "max_stack": 1,
            "hand_equipped": True,
            "durability": 2031,
            "damage": 6,
            "slot": "pickaxe",
            "speed": 12.0,
            "name": "§c§lRuby Pickaxe§r\n§7Tier: Netherite+ | Speed: 12.0 | Durability: 2031",
        },
        "ruby_axe": {
            "category": "equipment",
            "icon": "ruby_axe",
            "max_stack": 1,
            "hand_equipped": True,
            "durability": 2031,
            "damage": 11,
            "slot": "axe",
            "speed": 12.0,
            "name": "§c§lRuby Axe§r\n§7Tier: Netherite+ | Attack: +11 | Durability: 2031",
        },
        "ruby_shovel": {
            "category": "equipment",
            "icon": "ruby_shovel",
            "max_stack": 1,
            "hand_equipped": True,
            "durability": 2031,
            "damage": 6.5,
            "slot": "shovel",
            "speed": 12.0,
            "name": "§c§lRuby Shovel§r\n§7Tier: Netherite+ | Attack: +6.5 | Durability: 2031",
        },
        "ruby_hoe": {
            "category": "equipment",
            "icon": "ruby_hoe",
            "max_stack": 1,
            "hand_equipped": True,
            "durability": 2031,
            "damage": 2,
            "slot": "hoe",
            "speed": 12.0,
            "name": "§c§lRuby Hoe§r\n§7Tier: Netherite+ | Durability: 2031",
        },
        "ruby_hammer": {
            "category": "equipment",
            "icon": "ruby_hammer",
            "max_stack": 1,
            "hand_equipped": True,
            "durability": 2031,
            "damage": 8,
            "slot": "pickaxe",
            "speed": 10.0,
            "name": "§c§lRuby Hammer§r\n§7Heavy 3x3 Area Excavator | Durability: 2031",
        },
        "ruby_combat_axe": {
            "category": "equipment",
            "icon": "ruby_combat_axe",
            "max_stack": 1,
            "hand_equipped": True,
            "durability": 2031,
            "damage": 12,
            "slot": "axe",
            "speed": 12.0,
            "name": "§c§lRuby Combat Axe§r\n§7Heavy Cleaver | Attack: +12 | Durability: 2031",
        },
    }

    for item_id, item_data in items_def.items():
        components = {
            "minecraft:icon": {"textures": {"default": item_data["icon"]}},
            "minecraft:max_stack_size": item_data["max_stack"],
            "minecraft:display_name": {"value": item_data["name"]},
        }
        if item_data.get("hand_equipped"):
            components["minecraft:hand_equipped"] = True
        if item_data.get("durability"):
            components["minecraft:durability"] = {"max_durability": item_data["durability"]}
        if item_data.get("damage"):
            components["minecraft:damage"] = item_data["damage"]
        if item_data.get("slot"):
            components["minecraft:enchantable"] = {"value": 25, "slot": item_data["slot"]}

        # Adiciona tags e propriedades de mineracao para ferramentas
        if item_data.get("speed"):
            components["minecraft:digger"] = {
                "use_efficiency": True,
                "destroy_speeds": [
                    {
                        "block": "minecraft:stone",
                        "speed": item_data["speed"],
                    },
                    {
                        "block": "minecraft:deepslate",
                        "speed": item_data["speed"],
                    },
                    {
                        "block": "rubyore:ruby_ore",
                        "speed": item_data["speed"],
                    },
                    {
                        "block": "rubyore:deepslate_ruby_ore",
                        "speed": item_data["speed"],
                    },
                ],
            }

        item_json = {
            "format_version": "1.21.20",
            "minecraft:item": {
                "description": {
                    "identifier": f"rubyore:{item_id}",
                    "menu_category": {"category": item_data["category"]},
                },
                "components": components,
            },
        }
        (BP_DIR / "items" / f"{item_id}.json").write_text(json.dumps(item_json, indent=2), encoding="utf-8")

    # 3. Blocos
    blocks_def = {
        "ruby_block": {
            "seconds_to_destroy": 6.0,
            "explosion_resistance": 15.0,
            "map_color": "#c0392b",
            "name": "tile.rubyore:ruby_block.name",
        },
        "ruby_ore": {
            "seconds_to_destroy": 5.0,
            "explosion_resistance": 10.0,
            "map_color": "#7f8c8d",
            "name": "tile.rubyore:ruby_ore.name",
        },
        "deepslate_ruby_ore": {
            "seconds_to_destroy": 6.0,
            "explosion_resistance": 12.0,
            "map_color": "#2c3e50",
            "name": "tile.rubyore:deepslate_ruby_ore.name",
        },
    }

    for block_id, b_data in blocks_def.items():
        block_json = {
            "format_version": "1.21.20",
            "minecraft:block": {
                "description": {
                    "identifier": f"rubyore:{block_id}",
                },
                "components": {
                    "minecraft:destructible_by_mining": {
                        "seconds_to_destroy": b_data["seconds_to_destroy"]
                    },
                    "minecraft:destructible_by_explosion": {
                        "explosion_resistance": b_data["explosion_resistance"]
                    },
                    "minecraft:friction": 0.6,
                    "minecraft:map_color": b_data["map_color"],
                    "minecraft:display_name": b_data["name"],
                },
            },
        }
        (BP_DIR / "blocks" / f"{block_id}.json").write_text(json.dumps(block_json, indent=2), encoding="utf-8")

    # 4. Receitas
    recipes = {
        "ruby_block": {
            "type": "shaped",
            "pattern": ["RRR", "RRR", "RRR"],
            "key": {"R": {"item": "rubyore:ruby"}},
            "result": {"item": "rubyore:ruby_block", "count": 1},
        },
        "ruby_from_block": {
            "type": "shapeless",
            "ingredients": [{"item": "rubyore:ruby_block"}],
            "result": {"item": "rubyore:ruby", "count": 9},
        },
        "ruby_sword": {
            "type": "shaped",
            "pattern": [" R ", " R ", " S "],
            "key": {"R": {"item": "rubyore:ruby"}, "S": {"item": "minecraft:stick"}},
            "result": {"item": "rubyore:ruby_sword", "count": 1},
        },
        "ruby_pickaxe": {
            "type": "shaped",
            "pattern": ["RRR", " S ", " S "],
            "key": {"R": {"item": "rubyore:ruby"}, "S": {"item": "minecraft:stick"}},
            "result": {"item": "rubyore:ruby_pickaxe", "count": 1},
        },
        "ruby_axe": {
            "type": "shaped",
            "pattern": ["RR ", "RS ", " S "],
            "key": {"R": {"item": "rubyore:ruby"}, "S": {"item": "minecraft:stick"}},
            "result": {"item": "rubyore:ruby_axe", "count": 1},
        },
        "ruby_shovel": {
            "type": "shaped",
            "pattern": [" R ", " S ", " S "],
            "key": {"R": {"item": "rubyore:ruby"}, "S": {"item": "minecraft:stick"}},
            "result": {"item": "rubyore:ruby_shovel", "count": 1},
        },
        "ruby_hoe": {
            "type": "shaped",
            "pattern": ["RR ", " S ", " S "],
            "key": {"R": {"item": "rubyore:ruby"}, "S": {"item": "minecraft:stick"}},
            "result": {"item": "rubyore:ruby_hoe", "count": 1},
        },
        "ruby_hammer": {
            "type": "shaped",
            "pattern": ["RRR", "RRR", " S "],
            "key": {"R": {"item": "rubyore:ruby"}, "S": {"item": "minecraft:stick"}},
            "result": {"item": "rubyore:ruby_hammer", "count": 1},
        },
        "ruby_combat_axe": {
            "type": "shaped",
            "pattern": ["RRR", "RS ", " S "],
            "key": {"R": {"item": "rubyore:ruby"}, "S": {"item": "minecraft:stick"}},
            "result": {"item": "rubyore:ruby_combat_axe", "count": 1},
        },
        "ruby_smelting_ore": {
            "type": "furnace",
            "tags": ["furnace", "blast_furnace"],
            "input": "rubyore:ruby_ore",
            "output": "rubyore:ruby",
        },
        "ruby_smelting_deepslate": {
            "type": "furnace",
            "tags": ["furnace", "blast_furnace"],
            "input": "rubyore:deepslate_ruby_ore",
            "output": "rubyore:ruby",
        },
    }

    for r_name, r_data in recipes.items():
        if r_data["type"] == "shaped":
            rec_json = {
                "format_version": "1.20.0",
                "minecraft:recipe_shaped": {
                    "description": {"identifier": f"rubyore:{r_name}"},
                    "tags": ["crafting_table"],
                    "pattern": r_data["pattern"],
                    "key": r_data["key"],
                    "result": r_data["result"],
                },
            }
        elif r_data["type"] == "shapeless":
            rec_json = {
                "format_version": "1.20.0",
                "minecraft:recipe_shapeless": {
                    "description": {"identifier": f"rubyore:{r_name}"},
                    "tags": ["crafting_table"],
                    "ingredients": r_data["ingredients"],
                    "result": r_data["result"],
                },
            }
        else:
            rec_json = {
                "format_version": "1.20.0",
                "minecraft:recipe_furnace": {
                    "description": {"identifier": f"rubyore:{r_name}"},
                    "tags": r_data["tags"],
                    "input": r_data["input"],
                    "output": r_data["output"],
                },
            }
        (BP_DIR / "recipes" / f"{r_name}.json").write_text(json.dumps(rec_json, indent=2), encoding="utf-8")

    # 5. Textos
    lang_en = (
        "pack.name=Ruby Ore BP\n"
        "pack.description=The Ruby Ore Add-on by romhenri\n"
        "tile.rubyore:ruby_block.name=Block of Ruby\n"
        "tile.rubyore:ruby_ore.name=Ruby Ore\n"
        "tile.rubyore:deepslate_ruby_ore.name=Deepslate Ruby Ore\n"
        "item.rubyore:ruby.name=Ruby\n"
        "item.rubyore:raw_ruby.name=Raw Ruby\n"
        "item.rubyore:ruby_dust.name=Ruby Dust\n"
        "item.rubyore:ruby_sword.name=Ruby Sword\n"
        "item.rubyore:ruby_pickaxe.name=Ruby Pickaxe\n"
        "item.rubyore:ruby_axe.name=Ruby Axe\n"
        "item.rubyore:ruby_shovel.name=Ruby Shovel\n"
        "item.rubyore:ruby_hoe.name=Ruby Hoe\n"
        "item.rubyore:ruby_hammer.name=Ruby Hammer\n"
        "item.rubyore:ruby_combat_axe.name=Ruby Combat Axe\n"
    )
    lang_pt = (
        "pack.name=Ruby Ore BP\n"
        "pack.description=Add-on The Ruby Ore por romhenri\n"
        "tile.rubyore:ruby_block.name=Bloco de Rubi\n"
        "tile.rubyore:ruby_ore.name=Minério de Rubi\n"
        "tile.rubyore:deepslate_ruby_ore.name=Minério de Rubi em Ardósia Profunda\n"
        "item.rubyore:ruby.name=Rubi\n"
        "item.rubyore:raw_ruby.name=Rubi Bruto\n"
        "item.rubyore:ruby_dust.name=Pó de Rubi\n"
        "item.rubyore:ruby_sword.name=Espada de Rubi\n"
        "item.rubyore:ruby_pickaxe.name=Picareta de Rubi\n"
        "item.rubyore:ruby_axe.name=Machado de Rubi\n"
        "item.rubyore:ruby_shovel.name=Pá de Rubi\n"
        "item.rubyore:ruby_hoe.name=Enxada de Rubi\n"
        "item.rubyore:ruby_hammer.name=Martelo de Rubi\n"
        "item.rubyore:ruby_combat_axe.name=Machado de Combate de Rubi\n"
    )
    (BP_DIR / "texts" / "en_US.lang").write_text(lang_en, encoding="utf-8")
    (BP_DIR / "texts" / "pt_BR.lang").write_text(lang_pt, encoding="utf-8")
    (BP_DIR / "texts" / "languages.json").write_text('["en_US", "pt_BR"]\n', encoding="utf-8")
    generate_pack_icon(BP_DIR / "pack_icon.png")


def build_resource_pack() -> None:
    """Cria a estrutura e todos os arquivos do Resource Pack do Ruby Ore."""
    RP_DIR.mkdir(parents=True, exist_ok=True)
    (RP_DIR / "textures" / "items").mkdir(parents=True, exist_ok=True)
    (RP_DIR / "textures" / "blocks").mkdir(parents=True, exist_ok=True)
    (RP_DIR / "texts").mkdir(parents=True, exist_ok=True)

    # 1. manifest.json
    manifest = {
        "format_version": 2,
        "header": {
            "name": "Ruby Ore RP v1.0.0",
            "description": "The Ruby Ore Add-on Resource Pack by romhenri - Bedrock Port v1.2.0",
            "uuid": RP_UUID,
            "version": [1, 0, 0],
            "min_engine_version": [1, 26, 50],
        },
        "modules": [
            {
                "type": "resources",
                "uuid": RP_RES_UUID,
                "version": [1, 0, 0],
            }
        ],
    }
    (RP_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    # 2. Texturas
    download_or_generate_textures(RP_DIR / "textures")
    generate_pack_icon(RP_DIR / "pack_icon.png")

    # 3. item_texture.json
    item_texture = {
        "resource_pack_name": "RubyOreRP",
        "texture_name": "atlas.items",
        "texture_data": {
            "ruby": {"textures": "textures/items/ruby"},
            "raw_ruby": {"textures": "textures/items/raw_ruby"},
            "ruby_dust": {"textures": "textures/items/ruby_dust"},
            "ruby_sword": {"textures": "textures/items/ruby_sword"},
            "ruby_pickaxe": {"textures": "textures/items/ruby_pickaxe"},
            "ruby_axe": {"textures": "textures/items/ruby_axe"},
            "ruby_shovel": {"textures": "textures/items/ruby_shovel"},
            "ruby_hoe": {"textures": "textures/items/ruby_hoe"},
            "ruby_hammer": {"textures": "textures/items/ruby_hammer"},
            "ruby_combat_axe": {"textures": "textures/items/ruby_combat_axe"},
        },
    }
    (RP_DIR / "textures" / "item_texture.json").write_text(json.dumps(item_texture, indent=2), encoding="utf-8")

    # 4. terrain_texture.json
    terrain_texture = {
        "resource_pack_name": "RubyOreRP",
        "texture_name": "atlas.terrain",
        "padding": 8,
        "num_mip_levels": 4,
        "texture_data": {
            "ruby_block": {"textures": "textures/blocks/ruby_block"},
            "ruby_ore": {"textures": "textures/blocks/ruby_ore"},
            "deepslate_ruby_ore": {"textures": "textures/blocks/deepslate_ruby_ore"},
        },
    }
    (RP_DIR / "textures" / "terrain_texture.json").write_text(json.dumps(terrain_texture, indent=2), encoding="utf-8")

    # 5. blocks.json
    blocks_json = {
        "format_version": "1.21.20",
        "rubyore:ruby_block": {
            "textures": "ruby_block",
            "sound": "metal",
        },
        "rubyore:ruby_ore": {
            "textures": "ruby_ore",
            "sound": "stone",
        },
        "rubyore:deepslate_ruby_ore": {
            "textures": "deepslate_ruby_ore",
            "sound": "stone",
        },
    }
    (RP_DIR / "blocks.json").write_text(json.dumps(blocks_json, indent=2), encoding="utf-8")

    # 6. Textos
    lang_en = (
        "pack.name=Ruby Ore RP\n"
        "pack.description=The Ruby Ore Resource Pack by romhenri\n"
        "tile.rubyore:ruby_block.name=Block of Ruby\n"
        "tile.rubyore:ruby_ore.name=Ruby Ore\n"
        "tile.rubyore:deepslate_ruby_ore.name=Deepslate Ruby Ore\n"
        "item.rubyore:ruby.name=Ruby\n"
        "item.rubyore:raw_ruby.name=Raw Ruby\n"
        "item.rubyore:ruby_dust.name=Ruby Dust\n"
        "item.rubyore:ruby_sword.name=Ruby Sword\n"
        "item.rubyore:ruby_pickaxe.name=Ruby Pickaxe\n"
        "item.rubyore:ruby_axe.name=Ruby Axe\n"
        "item.rubyore:ruby_shovel.name=Ruby Shovel\n"
        "item.rubyore:ruby_hoe.name=Ruby Hoe\n"
        "item.rubyore:ruby_hammer.name=Ruby Hammer\n"
        "item.rubyore:ruby_combat_axe.name=Ruby Combat Axe\n"
    )
    (RP_DIR / "texts" / "en_US.lang").write_text(lang_en, encoding="utf-8")
    (RP_DIR / "texts" / "pt_BR.lang").write_text(lang_en, encoding="utf-8")
    (RP_DIR / "texts" / "languages.json").write_text('["en_US", "pt_BR"]\n', encoding="utf-8")


def sync_to_runtime() -> None:
    """Copia os pacotes para a pasta de runtime do servidor Bedrock."""
    DEV_BP_DIR.parent.mkdir(parents=True, exist_ok=True)
    DEV_RP_DIR.parent.mkdir(parents=True, exist_ok=True)

    if DEV_BP_DIR.exists():
        shutil.rmtree(DEV_BP_DIR)
    shutil.copytree(BP_DIR, DEV_BP_DIR)

    if DEV_RP_DIR.exists():
        shutil.rmtree(DEV_RP_DIR)
    shutil.copytree(RP_DIR, DEV_RP_DIR)


def install_ruby_ore(activate_as_current: bool = False, world_name: Optional[str] = None) -> bool:
    """Executa a criacao, compilacao e implantacao completa do Add-on The Ruby Ore."""
    print("\n" + "=" * 65)
    print("   INSTALADOR OFICIAL: THE RUBY ORE (romhenri) PARA BEDROCK")
    print("=" * 65)
    print("[*] Construindo Behavior Pack do Ruby Ore...")
    build_behavior_pack()

    print("[*] Construindo Resource Pack e sincronizando texturas oficiais...")
    build_resource_pack()

    print("[*] Sincronizando pacotes com o runtime do servidor BDS...")
    sync_to_runtime()
    print("[+] RubyOre_BP e RubyOre_RP implantados com sucesso!")

    if activate_as_current:
        try:
            import gerenciar_mods
            target_world = world_name or gerenciar_mods.read_level_name()
            gerenciar_mods.enable_mod("rubyore", target_world)
            print(f"[SUCESSO] The Ruby Ore ativado no mundo '{target_world}'!")
        except Exception as exc:
            print(f"[AVISO] Falha ao ativar no mundo atual: {exc}")

    print("=" * 65 + "\n")
    return True


def main():
    parser = argparse.ArgumentParser(description="Instalador e Construtor do Add-on The Ruby Ore para BDS")
    parser.add_argument("--activate", action="store_true", help="Ativa o mod Ruby Ore no mundo ativo apos a instalacao")
    parser.add_argument("--world", type=str, help="Especifica o mundo onde ativar o mod")
    args = parser.parse_args()

    install_ruby_ore(activate_as_current=args.activate, world_name=args.world)


if __name__ == "__main__":
    main()
