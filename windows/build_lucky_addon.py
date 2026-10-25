"""
Construtor e Gerador do Add-on Lucky Block & OneBlock Engine para Minecraft Bedrock Dedicated Server.
Cria a estrutura de Behavior Pack e Resource Pack com texturas, blocos, scripts e receitas.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from PIL import Image, ImageDraw

WINDOWS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = WINDOWS_DIR.parent
SERVER_DIR = PROJECT_ROOT / "server"
DATA_DIR = SERVER_DIR / "data"
CUSTOM_PACKS_DIR = DATA_DIR / "custom_packs"
RUNTIME_DIR = SERVER_DIR / "runtime"

BP_UUID = "59aa09c5-0a2c-4134-8481-725801fba963"
BP_DATA_UUID = "f668f595-2688-4a50-b638-ac3264689650"
BP_SCRIPT_UUID = "c17b5aeb-5495-441e-80b8-519750ecf88e"
RP_UUID = "60910110-474e-41b4-aa72-68e06a917819"
RP_RES_UUID = "aaf4bb44-a87a-4061-801b-047f45d64282"

BP_DIR = CUSTOM_PACKS_DIR / "behavior_packs" / "LuckyBlock_BP"
RP_DIR = CUSTOM_PACKS_DIR / "resource_packs" / "LuckyBlock_RP"

DEV_BP_DIR = RUNTIME_DIR / "development_behavior_packs" / "LuckyBlock_BP"
DEV_RP_DIR = RUNTIME_DIR / "development_resource_packs" / "LuckyBlock_RP"


def generate_lucky_block_texture(out_path: Path) -> None:
    """Gera textura 16x16 dourada clássica com ponto de interrogacao para o Lucky Block."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGBA", (16, 16), (255, 204, 0, 255))
    pixels = img.load()

    # Borda dourada e sombreado 3D
    for x in range(16):
        for y in range(16):
            if x == 0 or y == 0:
                pixels[x, y] = (255, 235, 120, 255)  # Brilho superior/esquerdo
            elif x == 15 or y == 15:
                pixels[x, y] = (180, 130, 0, 255)    # Sombra inferior/direito
            elif (x + y) % 5 == 0:
                pixels[x, y] = (245, 195, 0, 255)    # Ruido sutil de textura

    # Desenho pixelado do '?' em branco com sombra
    q_coords = [
        (6, 3), (7, 3), (8, 3), (9, 3),
        (5, 4), (10, 4),
        (10, 5),
        (9, 6),
        (8, 7),
        (7, 8), (8, 8),
        (7, 9), (8, 9),
        (7, 11), (8, 11),
        (7, 12), (8, 12)
    ]
    for (x, y) in q_coords:
        pixels[x, y] = (255, 255, 255, 255)

    img.save(out_path, "PNG")


def generate_pack_icon(out_path: Path, title: str = "LUCKY BLOCK") -> None:
    """Gera icone 128x128 estilizado para o pacote e mundo."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    size = 128
    img = Image.new("RGB", (size, size), (25, 20, 35))
    draw = ImageDraw.Draw(img)

    # Fundo gradiente/noturno do void
    for y in range(size):
        r = int(20 + 20 * (y / size))
        g = int(15 + 25 * (y / size))
        b = int(40 + 50 * (y / size))
        draw.line([(0, y), (size, y)], fill=(r, g, b))

    # Cubo Lucky Block centralizado (isométrico ou plano estilizado)
    bx, by, bw, bh = 32, 28, 64, 64
    # Sombra
    draw.rectangle([bx + 4, by + 4, bx + bw + 4, by + bh + 4], fill=(10, 10, 15))
    # Bloco dourado
    draw.rectangle([bx, by, bx + bw, by + bh], fill=(255, 204, 0), outline=(255, 240, 140), width=3)
    draw.rectangle([bx + 2, by + bh - 6, bx + bw - 2, by + bh - 2], fill=(180, 130, 0))
    draw.rectangle([bx + bw - 6, by + 2, bx + bw - 2, by + bh - 2], fill=(180, 130, 0))

    # Letra '?' grande
    # Centro aproximado
    cx, cy = 64, 60
    # Arco do interrogacao
    draw.arc([cx - 16, cy - 22, cx + 16, cy + 2], start=180, end=0, fill=(255, 255, 255), width=6)
    draw.line([(cx + 16, cy - 10), (cx + 16, cy - 5)], fill=(255, 255, 255), width=6)
    draw.line([(cx + 16, cy - 5), (cx, cy + 5)], fill=(255, 255, 255), width=6)
    draw.line([(cx, cy + 5), (cx, cy + 12)], fill=(255, 255, 255), width=6)
    # Ponto do '?'
    draw.rectangle([cx - 3, cy + 18, cx + 3, cy + 24], fill=(255, 255, 255))

    # Banner inferior
    draw.rectangle([0, 102, size, 128], fill=(200, 150, 0))
    draw.rectangle([0, 100, size, 102], fill=(255, 220, 100))
    # Texto representativo
    draw.text((12, 108), title, fill=(20, 20, 20))

    if out_path.suffix.lower() in [".jpg", ".jpeg"]:
        img.save(out_path, "JPEG", quality=95)
    else:
        img.save(out_path, "PNG")


def build_lucky_behavior_pack() -> None:
    """Cria a estrutura completa de arquivos do LuckyBlock_BP."""
    BP_DIR.mkdir(parents=True, exist_ok=True)
    (BP_DIR / "blocks").mkdir(parents=True, exist_ok=True)
    (BP_DIR / "recipes").mkdir(parents=True, exist_ok=True)
    (BP_DIR / "scripts").mkdir(parents=True, exist_ok=True)
    (BP_DIR / "texts").mkdir(parents=True, exist_ok=True)

    # 1. manifest.json
    manifest = {
        "format_version": 2,
        "header": {
            "name": "Lucky Block BP v1.0.0",
            "description": "Lucky Block & OneBlock Engine Behavior Pack for Bedrock Dedicated Server",
            "uuid": BP_UUID,
            "version": [1, 0, 0],
            "min_engine_version": [1, 26, 50],
        },
        "modules": [
            {
                "description": "Lucky Block Data",
                "type": "data",
                "uuid": BP_DATA_UUID,
                "version": [1, 0, 0],
            },
            {
                "description": "Lucky OneBlock Script Engine",
                "type": "script",
                "uuid": BP_SCRIPT_UUID,
                "version": [1, 0, 0],
                "entry": "scripts/main.js",
            },
        ],
        "dependencies": [
            {
                "uuid": RP_UUID,
                "version": [1, 0, 0],
            },
            {
                "module_name": "@minecraft/server",
                "version": "2.10.0",
            },
        ],
    }
    (BP_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    # 2. blocks/lucky_block.json
    block_json = {
        "format_version": "1.21.20",
        "minecraft:block": {
            "description": {
                "identifier": "lucky:lucky_block"
            },
            "components": {
                "minecraft:destructible_by_mining": {
                    "seconds_to_destroy": 0.5
                },
                "minecraft:destructible_by_explosion": {
                    "explosion_resistance": 1.0
                },
                "minecraft:friction": 0.6,
                "minecraft:map_color": "#ffcc00",
                "minecraft:light_emission": 6,
                "minecraft:display_name": "tile.lucky:lucky_block.name"
            }
        }
    }
    (BP_DIR / "blocks" / "lucky_block.json").write_text(json.dumps(block_json, indent=2), encoding="utf-8")

    # 3. recipes/lucky_block.json
    recipe_json = {
        "format_version": "1.20.10",
        "minecraft:recipe_shaped": {
            "description": {
                "identifier": "lucky:lucky_block_recipe"
            },
            "tags": ["crafting_table"],
            "pattern": [
                "GGG",
                "GCG",
                "GGG"
            ],
            "key": {
                "G": {
                    "item": "minecraft:gold_ingot"
                },
                "C": {
                    "item": "minecraft:dropper"
                }
            },
            "result": {
                "item": "lucky:lucky_block",
                "count": 1
            }
        }
    }
    (BP_DIR / "recipes" / "lucky_block.json").write_text(json.dumps(recipe_json, indent=2), encoding="utf-8")

    # 4. texts
    (BP_DIR / "texts" / "languages.json").write_text(json.dumps(["en_US", "pt_BR"]), encoding="utf-8")
    (BP_DIR / "texts" / "en_US.lang").write_text("tile.lucky:lucky_block.name=Lucky Block\npack.name=Lucky Block BP\npack.description=Lucky Block and OneBlock Engine\n", encoding="utf-8")
    (BP_DIR / "texts" / "pt_BR.lang").write_text("tile.lucky:lucky_block.name=Bloco da Sorte\npack.name=Lucky Block BP\npack.description=Bloco da Sorte e Motor OneBlock\n", encoding="utf-8")

    # 5. scripts/main.js
    script_js = """// ==============================================================================
// Lucky Block & OneBlock Engine - Bedrock Dedicated Server 1.26.50+
// Suporte nativo ao mundo Lucky OneBlock e blocos lucky:lucky_block
// ==============================================================================
import { system, world, ItemStack } from "@minecraft/server";

const ONEBLOCK_POS = { x: 0, y: 64, z: 0 };
const LUCKY_BLOCK_ID = "lucky:lucky_block";

// Catalogo rico de eventos Lucky
const LUCKY_OUTCOMES = [
    // 1. Super Lucky: Diamantes e Joias
    {
        name: "§b✦ Diamantes da Sorte! ✦",
        run(dimension, pos) {
            dimension.spawnItem(new ItemStack("minecraft:diamond", Math.floor(Math.random() * 4) + 2), pos);
            dimension.spawnItem(new ItemStack("minecraft:emerald", Math.floor(Math.random() * 3) + 1), pos);
        }
    },
    // 2. Ouro e Recursos Nobres
    {
        name: "§6✦ Pepitas e Barras de Ouro! ✦",
        run(dimension, pos) {
            dimension.spawnItem(new ItemStack("minecraft:gold_ingot", Math.floor(Math.random() * 6) + 3), pos);
            dimension.spawnItem(new ItemStack("minecraft:iron_ingot", Math.floor(Math.random() * 6) + 3), pos);
        }
    },
    // 3. Suprimento de Construcao (Essencial p/ OneBlock)
    {
        name: "§a⛏ Kit de Construção Inicial ⛏",
        run(dimension, pos) {
            dimension.spawnItem(new ItemStack("minecraft:oak_log", 16), pos);
            dimension.spawnItem(new ItemStack("minecraft:cobblestone", 32), pos);
            dimension.spawnItem(new ItemStack("minecraft:glass", 16), pos);
        }
    },
    // 4. Kit Agro & Sobrevivência
    {
        name: "§2✿ Banquete da Sorte! ✿",
        run(dimension, pos) {
            dimension.spawnItem(new ItemStack("minecraft:cooked_beef", 8), pos);
            dimension.spawnItem(new ItemStack("minecraft:golden_carrot", 4), pos);
            dimension.spawnItem(new ItemStack("minecraft:wheat_seeds", 6), pos);
            dimension.spawnItem(new ItemStack("minecraft:bone_meal", 8), pos);
        }
    },
    // 5. Maça Dourada Encantada
    {
        name: "§6★ MAÇÃ DOURADA ENCANTADA! ★",
        run(dimension, pos) {
            dimension.spawnItem(new ItemStack("minecraft:enchanted_golden_apple", 1), pos);
            dimension.spawnItem(new ItemStack("minecraft:experience_bottle", 8), pos);
        }
    },
    // 6. Kit de Ferramentas Reforçadas
    {
        name: "§9⚔ Picareta e Espada de Ferro ⚔",
        run(dimension, pos) {
            dimension.spawnItem(new ItemStack("minecraft:iron_pickaxe", 1), pos);
            dimension.spawnItem(new ItemStack("minecraft:iron_sword", 1), pos);
            dimension.spawnItem(new ItemStack("minecraft:torch", 16), pos);
        }
    },
    // 7. Baldes de Água e Lava (Gerador de Cobblestone!)
    {
        name: "§3💧 Elementos: Água e Lava! 🔥",
        run(dimension, pos) {
            dimension.spawnItem(new ItemStack("minecraft:water_bucket", 1), pos);
            dimension.spawnItem(new ItemStack("minecraft:lava_bucket", 1), pos);
        }
    },
    // 8. Netherite Scrap Relíquia
    {
        name: "§8✦ Sucata de Netherite! ✦",
        run(dimension, pos) {
            dimension.spawnItem(new ItemStack("minecraft:netherite_scrap", 1), pos);
            dimension.spawnItem(new ItemStack("minecraft:obsidian", 4), pos);
        }
    },
    // 9. Animal Amigável
    {
        name: "§d❤ Um Amigo Animal Surgiu! ❤",
        run(dimension, pos) {
            const animals = ["minecraft:sheep", "minecraft:cow", "minecraft:pig", "minecraft:chicken"];
            const chosen = animals[Math.floor(Math.random() * animals.length)];
            dimension.spawnEntity(chosen, { x: pos.x + 0.5, y: pos.y + 1, z: pos.z + 0.5 });
        }
    },
    // 10. Totem da Imortalidade
    {
        name: "§e⚡ TOTEM DA IMORTALIDADE! ⚡",
        run(dimension, pos) {
            dimension.spawnItem(new ItemStack("minecraft:totem_of_undying", 1), pos);
        }
    },
    // 11. Surpresa Misteriosa: Mob Hostil Cômico
    {
        name: "§c☠ CUIDADO: Zumbi da Sorte! ☠",
        run(dimension, pos) {
            const zombie = dimension.spawnEntity("minecraft:zombie", { x: pos.x + 0.5, y: pos.y + 1, z: pos.z + 0.5 });
            dimension.spawnItem(new ItemStack("minecraft:golden_helmet", 1), pos);
        }
    },
    // 12. Livros Encantados e Experiência
    {
        name: "§5✨ Frascos de Experiência e Lápis-Lazúli ✨",
        run(dimension, pos) {
            dimension.spawnItem(new ItemStack("minecraft:experience_bottle", 12), pos);
            dimension.spawnItem(new ItemStack("minecraft:lapis_lazuli", 16), pos);
            dimension.spawnItem(new ItemStack("minecraft:book", 3), pos);
        }
    }
];

function isOneBlockPos(pos) {
    return pos.x === ONEBLOCK_POS.x && pos.y === ONEBLOCK_POS.y && pos.z === ONEBLOCK_POS.z;
}

function ensureOneBlock() {
    try {
        const dimension = world.getDimension("overworld");
        const block = dimension.getBlock(ONEBLOCK_POS);
        if (block && (block.isAir || block.typeId !== LUCKY_BLOCK_ID)) {
            block.setType(LUCKY_BLOCK_ID);
        }
    } catch (e) {
        // Pode ocorrer se o chunk ainda nao estiver carregado
    }
}

// Inicializacao do OneBlock
world.afterEvents.worldInitialize.subscribe(() => {
    system.runTimeout(() => {
        ensureOneBlock();
    }, 20);
});

// Mensagem de boas-vindas aos jogadores
world.afterEvents.playerSpawn.subscribe((event) => {
    const player = event.player;
    if (event.initialSpawn) {
        player.onScreenDisplay.setTitle("§6§lLUCKY ONEBLOCK§r", {
            subtitle: "§eQuebre o Lucky Block no centro para começar!",
            fadeInDuration: 20,
            stayDuration: 60,
            fadeOutDuration: 20
        });
        player.sendMessage("§6==================================================");
        player.sendMessage("§e★ Bem-vindo ao §lLucky OneBlock§r §e(BDS Edition)!");
        player.sendMessage("§7- O bloco central respawna infinitamente a cada quebra.");
        player.sendMessage("§7- Protecao contra queda no void ativa na area inicial.");
        player.sendMessage("§6==================================================");
    }
});

// Evento ao quebrar bloco: Executa evento Lucky e restaura OneBlock
world.afterEvents.playerBreakBlock.subscribe((event) => {
    const { block, brokenBlockPermutation, dimension, player } = event;
    const pos = { x: block.location.x, y: block.location.y, z: block.location.z };

    const isLucky = brokenBlockPermutation.type.id === LUCKY_BLOCK_ID || isOneBlockPos(pos);
    if (!isLucky) return;

    // Sorteia um evento
    const outcome = LUCKY_OUTCOMES[Math.floor(Math.random() * LUCKY_OUTCOMES.length)];
    try {
        outcome.run(dimension, { x: pos.x + 0.5, y: pos.y + 0.5, z: pos.z + 0.5 });
        if (player) {
            player.onScreenDisplay.setActionBar(outcome.name);
            player.playSound("random.levelup", { location: pos, volume: 1.0, pitch: 1.2 });
        }
    } catch (err) {
        console.warn(`[LuckyBlock] Erro ao disparar outcome: ${err}`);
    }

    // Se foi na posicao OneBlock, respawna o bloco apos 8 ticks
    if (isOneBlockPos(pos)) {
        system.runTimeout(() => {
            try {
                const b = dimension.getBlock(ONEBLOCK_POS);
                if (b) {
                    b.setType(LUCKY_BLOCK_ID);
                    dimension.playSound("random.orb", { location: ONEBLOCK_POS, volume: 0.8, pitch: 1.5 });
                }
            } catch (err) {
                console.warn(`[LuckyBlock] Erro ao respawnar OneBlock: ${err}`);
            }
        }, 8);
    }
});

// Protecao Anti-Void para a plataforma inicial
system.runInterval(() => {
    try {
        const dimension = world.getDimension("overworld");
        const players = world.getAllPlayers();
        for (const player of players) {
            const loc = player.location;
            if (loc.y < 55 && Math.abs(loc.x) <= 25 && Math.abs(loc.z) <= 25) {
                player.teleport({ x: 0.5, y: 65.5, z: 0.5 }, { dimension, rotation: { x: 0, y: 0 } });
                player.sendMessage("§e[Lucky OneBlock] §aVocê foi resgatado do void com segurança!");
                player.playSound("beacon.activate", { location: player.location, volume: 1.0, pitch: 1.0 });
                ensureOneBlock();
            }
        }
    } catch (e) {
        // Ignora erros periodicos
    }
}, 10);
"""
    (BP_DIR / "scripts" / "main.js").write_text(script_js, encoding="utf-8")

    # 6. pack_icon.png
    generate_pack_icon(BP_DIR / "pack_icon.png", "LUCKY BLOCK BP")


def build_lucky_resource_pack() -> None:
    """Cria a estrutura completa de arquivos do LuckyBlock_RP."""
    RP_DIR.mkdir(parents=True, exist_ok=True)
    (RP_DIR / "textures" / "blocks").mkdir(parents=True, exist_ok=True)
    (RP_DIR / "texts").mkdir(parents=True, exist_ok=True)

    # 1. manifest.json
    manifest = {
        "format_version": 2,
        "header": {
            "name": "Lucky Block RP v1.0.0",
            "description": "Lucky Block Resource Pack for Bedrock Dedicated Server",
            "uuid": RP_UUID,
            "version": [1, 0, 0],
            "min_engine_version": [1, 26, 50],
        },
        "modules": [
            {
                "description": "Lucky Block Resources",
                "type": "resources",
                "uuid": RP_RES_UUID,
                "version": [1, 0, 0],
            }
        ],
    }
    (RP_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    # 2. blocks.json
    blocks_json = {
        "format_version": "1.21.20",
        "lucky:lucky_block": {
            "textures": "lucky_block",
            "sound": "wood"
        }
    }
    (RP_DIR / "blocks.json").write_text(json.dumps(blocks_json, indent=2), encoding="utf-8")

    # 3. textures/terrain_texture.json
    terrain_json = {
        "resource_pack_name": "lucky_block_rp",
        "texture_name": "atlas.terrain",
        "texture_data": {
            "lucky_block": {
                "textures": "textures/blocks/lucky_block"
            }
        }
    }
    (RP_DIR / "textures" / "terrain_texture.json").write_text(json.dumps(terrain_json, indent=2), encoding="utf-8")

    # 4. textures/blocks/lucky_block.png
    generate_lucky_block_texture(RP_DIR / "textures" / "blocks" / "lucky_block.png")

    # 5. texts
    (RP_DIR / "texts" / "languages.json").write_text(json.dumps(["en_US", "pt_BR"]), encoding="utf-8")
    (RP_DIR / "texts" / "en_US.lang").write_text("tile.lucky:lucky_block.name=Lucky Block\n", encoding="utf-8")
    (RP_DIR / "texts" / "pt_BR.lang").write_text("tile.lucky:lucky_block.name=Bloco da Sorte\n", encoding="utf-8")

    # 6. pack_icon.png
    generate_pack_icon(RP_DIR / "pack_icon.png", "LUCKY BLOCK RP")


def deploy_to_runtime() -> None:
    """Espelha os pacotes para as pastas de desenvolvimento no runtime do BDS."""
    DEV_BP_DIR.parent.mkdir(parents=True, exist_ok=True)
    DEV_RP_DIR.parent.mkdir(parents=True, exist_ok=True)

    if DEV_BP_DIR.exists():
        shutil.rmtree(DEV_BP_DIR)
    if DEV_RP_DIR.exists():
        shutil.rmtree(DEV_RP_DIR)

    shutil.copytree(BP_DIR, DEV_BP_DIR)
    shutil.copytree(RP_DIR, DEV_RP_DIR)
    print(f"[+] LuckyBlock_BP implantado em: {DEV_BP_DIR}")
    print(f"[+] LuckyBlock_RP implantado em: {DEV_RP_DIR}")


def build_all() -> None:
    print("[*] Construindo Behavior Pack do Lucky Block...")
    build_lucky_behavior_pack()
    print("[*] Construindo Resource Pack do Lucky Block...")
    build_lucky_resource_pack()
    print("[*] Implantando pacotes no runtime do servidor...")
    deploy_to_runtime()
    print("[SUCESSO] Add-on Lucky Block compilado e implantado com exito!")


if __name__ == "__main__":
    build_all()
