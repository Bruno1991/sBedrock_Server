"""
Script de entrega do Kit Supremo (God Gear) para os jogadores no Minecraft Bedrock.
Entrega armadura completa de Netherite com encantamentos maximos, ferramentas, armas,
arco infinito, besta, tridente, maca, elytra, totens e suprimentos.
"""

from bds_cmd import send_command, get_bds_pid
import time
import sys

def run(cmd, delay=0.04):
    return send_command(cmd, wait_ms=int(delay * 1000))

# Lista de itens a encantar via armor stand drop
GOD_ITEMS = [
    {
        "item": "netherite_helmet",
        "name": "Capacete de Netherite Supremo",
        "enchants": [("protection", 4), ("unbreaking", 3), ("mending", 1), ("respiration", 3), ("aqua_affinity", 1)]
    },
    {
        "item": "netherite_chestplate",
        "name": "Peitoral de Netherite Supremo",
        "enchants": [("protection", 4), ("unbreaking", 3), ("mending", 1), ("thorns", 3)]
    },
    {
        "item": "netherite_leggings",
        "name": "Calcas de Netherite Supremas",
        "enchants": [("protection", 4), ("unbreaking", 3), ("mending", 1), ("swift_sneak", 3)]
    },
    {
        "item": "netherite_boots",
        "name": "Botas de Netherite Supremas",
        "enchants": [("protection", 4), ("unbreaking", 3), ("mending", 1), ("feather_falling", 4), ("depth_strider", 3), ("soul_speed", 3)]
    },
    {
        "item": "netherite_sword",
        "name": "Espada de Netherite Suprema",
        "enchants": [("sharpness", 5), ("unbreaking", 3), ("mending", 1), ("looting", 3), ("fire_aspect", 2), ("knockback", 2)]
    },
    {
        "item": "netherite_pickaxe",
        "name": "Picareta de Fortuna Suprema",
        "enchants": [("efficiency", 5), ("unbreaking", 3), ("mending", 1), ("fortune", 3)]
    },
    {
        "item": "netherite_pickaxe",
        "name": "Picareta Toque Suave Suprema",
        "enchants": [("efficiency", 5), ("unbreaking", 3), ("mending", 1), ("silk_touch", 1)]
    },
    {
        "item": "netherite_axe",
        "name": "Machado de Netherite Supremo",
        "enchants": [("efficiency", 5), ("sharpness", 5), ("unbreaking", 3), ("mending", 1)]
    },
    {
        "item": "netherite_shovel",
        "name": "Pa de Netherite Suprema",
        "enchants": [("efficiency", 5), ("silk_touch", 1), ("unbreaking", 3), ("mending", 1)]
    },
    {
        "item": "netherite_hoe",
        "name": "Enxada de Netherite Suprema",
        "enchants": [("efficiency", 5), ("fortune", 3), ("unbreaking", 3), ("mending", 1)]
    },
    {
        "item": "bow",
        "name": "Arco Infinito Supremo",
        "enchants": [("power", 5), ("flame", 1), ("punch", 2), ("infinity", 1), ("unbreaking", 3)]
    },
    {
        "item": "crossbow",
        "name": "Besta Multipla Suprema",
        "enchants": [("quick_charge", 3), ("multishot", 1), ("unbreaking", 3), ("mending", 1)]
    },
    {
        "item": "trident",
        "name": "Tridente Leal Supremo",
        "enchants": [("impaling", 5), ("loyalty", 3), ("channeling", 1), ("unbreaking", 3), ("mending", 1)]
    },
    {
        "item": "mace",
        "name": "Maca de Impacto Suprema",
        "enchants": [("density", 5), ("breach", 4), ("wind_burst", 3), ("unbreaking", 3), ("mending", 1)]
    },
    {
        "item": "shield",
        "name": "Escudo Reforcado Supremo",
        "enchants": [("unbreaking", 3), ("mending", 1)]
    },
    {
        "item": "elytra",
        "name": "Asas de Elytra Supremas",
        "enchants": [("unbreaking", 3), ("mending", 1)]
    }
]

def deliver_kit_to_player(player_name):
    print(f"\n>>> Entregando Kit Supremo para: {player_name}...")
    run(f'say [BDS] Preparando e entregando o Kit Supremo para {player_name}...')

    # 1. Equipar imediatamente a armadura no corpo do jogador
    run(f'replaceitem entity {player_name} slot.armor.head 0 netherite_helmet')
    run(f'replaceitem entity {player_name} slot.armor.chest 0 netherite_chestplate')
    run(f'replaceitem entity {player_name} slot.armor.legs 0 netherite_leggings')
    run(f'replaceitem entity {player_name} slot.armor.feet 0 netherite_boots')
    run(f'replaceitem entity {player_name} slot.weapon.offhand 0 shield')

    # 2. Entregar consumiveis essenciais
    run(f'give {player_name} totem_of_undying 5')
    run(f'give {player_name} enchanted_golden_apple 64')
    run(f'give {player_name} arrow 64')
    run(f'give {player_name} firework_rocket 64')
    run(f'give {player_name} experience_bottle 64')

    # 3. Forjar e dropar cada item com encantamentos maximos nos pes do jogador
    stand_name = f"kit_{player_name}"
    for gear in GOD_ITEMS:
        item_id = gear["item"]
        name_desc = gear["name"]
        print(f"  - Forjando: {name_desc}...")

        # Invocar armor stand nos pes do jogador
        run(f'execute at {player_name} run summon armor_stand {stand_name} ~ ~ ~')
        time.sleep(0.04)

        # Colocar o item na mao do stand
        run(f'replaceitem entity @e[type=armor_stand,name={stand_name}] slot.weapon.mainhand 0 {item_id}')

        # Aplicar cada encantamento de nivel maximo
        for enc_id, enc_lvl in gear["enchants"]:
            run(f'enchant @e[type=armor_stand,name={stand_name}] {enc_id} {enc_lvl}')

        # Matar o stand para dropar o item encantado diretamente no jogador
        run(f'kill @e[type=armor_stand,name={stand_name}]')
        time.sleep(0.04)

    run(f'say [BDS] {player_name} recebeu todo o Kit Supremo!')

def main():
    pid = get_bds_pid()
    if not pid:
        print("[ERRO] BDS nao esta em execucao!")
        sys.exit(1)

    players = ["x12ultimatepass", "AerialTuba9051"]
    for p in players:
        deliver_kit_to_player(p)

    print("\n==================================================================")
    print(" [SUCESSO] Todos os itens maximos foram entregues a ambos os jogadores!")
    print("==================================================================")

if __name__ == '__main__':
    main()
