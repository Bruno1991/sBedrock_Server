"""
Script de Construcao da Mansao Estatua Gigante de Creeper no Minecraft Bedrock.
Escala: 3:1 (cada pixel do Creeper equivale a 3x3 blocos).
Dimensoes: 24 blocos de largura x 24 blocos de profundidade x 78 blocos de altura.
Base: Y = 76 | Topo: Y = 154.

Andares e Funcoes:
- Andar 1 (Y = 77-94): Hall de Entrada Principal, Armaria, Portal do Nether, Cofre e Mina.
- Andar 2 (Y = 95-103): Jardim Zen & Estufa Hidroponica de Azaleas e Glow Berries.
- Andar 3 (Y = 104-112): Oficina de Metalurgia & Super Fornalhas Automaticas.
- Andar 4 (Y = 113-121): Laboratorio de Alquimia & Pocao.
- Andar 5 (Y = 122-130): Grande Biblioteca & Altar de Encantamentos Nivel 30.
- Andar 6 (Y = 131-142): Grande Armazem & Centro Logistico (40+ Baus Duplos e Barris).
- Andar 7 (Y = 143-153): Suite Master Suprema no Topo (Camas King, Visao Panoramica pelos Olhos).
- Telhado (Y = 154): Terraco Mirante & Para-raios do Creeper Eletrizado.
"""

import sys
import time
import random
from bds_cmd import send_command, get_bds_pid

def cmd(command_str, delay=0.03):
    ok = send_command(command_str, wait_ms=int(delay * 1000))
    if not ok:
        print(f"[AVISO] Falha ao enviar: {command_str}")
    return ok

def build_creeper_mansion():
    pid = get_bds_pid()
    if not pid:
        print("[ERRO] Bedrock Dedicated Server nao esta rodando!")
        sys.exit(1)

    print("==================================================================")
    print(" INICIANDO CONSTRUCAO DA MANSAO ESTATUA GIGANTE DE CREEPER")
    print("==================================================================")

    cmd("say [BDS] Iniciando construcao da Mansao Gigante de Creeper...")

    # Ativar ticking area temporaria para garantir carregamento perfeito
    cmd("tickingarea add -20 70 -80 20 160 -45 creeper_mansion_area")

    # =========================================================================
    # 1. FUNDACAO & LIMPEZA DO TERRENO
    # =========================================================================
    print("1/8 - Preparando fundacao e nivelando terreno...")
    # Limpar espaco aereo da mansao
    cmd("fill -15 77 -77 14 158 -48 air")
    # Base solida de pedra e deepslate sob as patas
    cmd("fill -14 70 -76 13 76 -49 smooth_stone")
    # Praca externa pavimentada com tijolos de pedra musgosa
    cmd("fill -15 76 -77 14 76 -48 stone_brick_stairs 0 keep")
    cmd("fill -14 76 -76 13 76 -49 mossy_stone_bricks")
    cmd("fill -12 76 -74 11 76 -51 polished_blackstone")

    # =========================================================================
    # 2. ESTRUTURA EXTERIOR DAS 4 PATAS (Y = 77 ate 94, 18 blocos de altura)
    # =========================================================================
    print("2/8 - Erguer estrutura das 4 patas do Creeper...")
    # Pata Dianteira Esquerda: X [-12, -1], Z [-62, -51]
    cmd("fill -12 77 -62 -1 94 -51 green_concrete")
    cmd("fill -11 77 -61 -2 94 -52 air")

    # Pata Dianteira Direita: X [0, 11], Z [-62, -51]
    cmd("fill 0 77 -62 11 94 -51 green_concrete")
    cmd("fill 1 77 -61 10 94 -52 air")

    # Pata Traseira Esquerda: X [-12, -1], Z [-74, -63]
    cmd("fill -12 77 -74 -1 94 -63 green_concrete")
    cmd("fill -11 77 -73 -2 94 -64 air")

    # Pata Traseira Direita: X [0, 11], Z [-74, -63]
    cmd("fill 0 77 -74 11 94 -63 green_concrete")
    cmd("fill 1 77 -73 10 94 -64 air")

    # Aberturas de conexao entre o hall central e as 4 patas
    cmd("fill -2 77 -64 -1 82 -61 air")
    cmd("fill 0 77 -64 1 82 -61 air")
    cmd("fill -5 77 -63 -2 82 -63 air")
    cmd("fill 1 77 -63 4 82 -63 air")

    # =========================================================================
    # 3. TRONCO / CORPO (Y = 95 ate 130, 36 blocos de altura)
    # =========================================================================
    print("3/8 - Construindo o tronco macico do Creeper...")
    # Tronco: X [-12, 11], Z [-68, -57] (profundidade 12 blocos, largura 24 blocos)
    cmd("fill -12 95 -68 11 130 -57 green_concrete")
    cmd("fill -11 95 -67 10 130 -58 air")

    # Terracos ajardinados no topo das patas dianteiras e traseiras que sobram fora do tronco
    # Topo das patas dianteiras: Z [-56, -51]
    cmd("fill -12 94 -56 11 94 -51 moss_block")
    cmd("fill -12 95 -51 11 95 -51 oak_fence")
    cmd("fill -12 95 -56 -12 95 -52 oak_fence")
    cmd("fill 11 95 -56 11 95 -52 oak_fence")

    # Topo das patas traseiras: Z [-74, -69]
    cmd("fill -12 94 -74 11 94 -69 moss_block")
    cmd("fill -12 95 -74 11 95 -74 oak_fence")
    cmd("fill -12 95 -73 -12 95 -69 oak_fence")
    cmd("fill 11 95 -73 11 95 -69 oak_fence")

    # =========================================================================
    # 4. CABECA DO CREEPER (Y = 131 ate 154, 24 blocos de altura)
    # =========================================================================
    print("4/8 - Esculpindo a cabeca monumental e o rosto iconico...")
    # Cabeca exterior: X [-12, 11], Z [-74, -51] (24x24x24 blocos!)
    cmd("fill -12 131 -74 11 154 -51 green_concrete")
    cmd("fill -11 131 -73 10 153 -52 air")

    # ROSTO DO CREEPER NA FACE SUL (Z = -51):
    # Olho Esquerdo (do observador olhando pro Creeper = X [-9, -4], Y [146, 151])
    cmd("fill -9 146 -51 -4 151 -51 black_stained_glass")
    # Olho Direito (X [3, 8], Y [146, 151])
    cmd("fill 3 146 -51 8 151 -51 black_stained_glass")

    # Nariz Central (X [-3, 2], Y [143, 145])
    cmd("fill -3 143 -51 2 145 -51 black_concrete")

    # Boca Superior (X [-9, 8], Y [137, 142])
    cmd("fill -9 137 -51 8 142 -51 black_concrete")
    # Janela panoramica central na boca para o armazem ter vista
    cmd("fill -3 138 -51 2 141 -51 tinted_glass")

    # Dentes / Bigode do Creeper (Y [134, 136])
    # Recortes verdes nas laterais internas do bigode
    cmd("fill -6 134 -51 -4 136 -51 green_concrete")
    cmd("fill 3 134 -51 5 136 -51 green_concrete")

    # Cantos inferiores da boca / queixo (Y [131, 133])
    cmd("fill -9 131 -51 -7 133 -51 black_concrete")
    cmd("fill 6 131 -51 8 133 -51 black_concrete")

    # =========================================================================
    # 5. TEXTURA CAMUFLADA MOSAICO (LIME, MOSS, TERRACOTTA)
    # =========================================================================
    print("5/8 - Aplicando textura camuflada oficial de alta definicao...")
    # Adicionar variacao procedural de blocos na fachada e laterais
    camo_blocks = ["lime_concrete", "moss_block", "lime_terracotta", "green_terracotta"]
    
    # Patches no tronco
    cmd("fill -10 98 -57 -6 103 -57 lime_concrete")
    cmd("fill 5 97 -57 9 104 -57 moss_block")
    cmd("fill -8 112 -57 -3 118 -57 lime_terracotta")
    cmd("fill 2 110 -57 7 117 -57 lime_concrete")
    cmd("fill -11 120 -57 -7 127 -57 moss_block")
    cmd("fill 4 121 -57 8 128 -57 lime_concrete")

    # Patches nas patas dianteiras
    cmd("fill -10 80 -51 -4 86 -51 lime_concrete")
    cmd("fill 3 81 -51 8 87 -51 moss_block")
    cmd("fill -9 88 -51 -5 92 -51 lime_terracotta")
    cmd("fill 4 89 -51 9 93 -51 lime_concrete")

    # Patches na cabeca
    cmd("fill -11 133 -51 -10 144 -51 lime_concrete")
    cmd("fill 9 133 -51 10 144 -51 moss_block")
    cmd("fill -11 152 -51 10 154 -51 lime_concrete")
    cmd("fill -2 147 -51 1 151 -51 moss_block")

    # =========================================================================
    # 6. ELEVADORES DE AGUA & ESCADA CENTRAL (Y = 77 ate 154)
    # =========================================================================
    print("6/8 - Instalando sistema de elevadores duplos de bolhas e escada...")
    # Tubo do Elevador Subida (Soul Sand): X = -1, Z = -63
    cmd("fill -2 77 -63 0 153 -63 glass")
    cmd("fill -1 77 -64 -1 153 -62 glass")
    # Coluna de agua
    cmd("fill -1 77 -63 -1 153 -63 water")
    cmd("setblock -1 76 -63 soul_sand")

    # Tubo do Elevador Descida (Magma Block): X = 1, Z = -63
    cmd("fill 0 77 -63 2 153 -63 glass")
    cmd("fill 1 77 -64 1 153 -62 glass")
    cmd("fill 1 77 -63 1 153 -63 water")
    cmd("setblock 1 76 -63 magma_block")

    # Eixo central de andaimes para acesso manual entre andares: X = 0, Z = -62
    cmd("fill 0 77 -62 0 154 -62 scaffolding")

    # =========================================================================
    # 7. ANDARES, PISOS, ILUMINACAO E DECORACOES TEMATICAS
    # =========================================================================
    print("7/8 - Mobiliando e decorando todos os andares funcionais...")

    # -------------------------------------------------------------------------
    # ANDAR 1: GRAND ENTRANCE HALL & AS 4 PATAS (Y = 77 - 94)
    # -------------------------------------------------------------------------
    # Piso do Hall Principal
    cmd("fill -11 76 -73 10 76 -52 polished_deepslate")
    cmd("fill -6 76 -68 5 76 -57 smooth_quartz")
    
    # Portal de Entrada na face Sul (entre as patas dianteiras)
    cmd("fill -2 77 -51 1 81 -51 air")
    cmd("fill -2 77 -51 -2 81 -51 dark_oak_log")
    cmd("fill 1 77 -51 1 81 -51 dark_oak_log")
    cmd("fill -1 81 -51 0 81 -51 dark_oak_log")
    cmd("setblock -1 77 -51 dark_oak_door 0")
    cmd("setblock 0 77 -51 dark_oak_door 8")
    cmd("setblock -1 76 -52 polished_blackstone_pressure_plate")
    cmd("setblock 0 76 -52 polished_blackstone_pressure_plate")
    cmd("setblock -1 76 -50 polished_blackstone_pressure_plate")
    cmd("setblock 0 76 -50 polished_blackstone_pressure_plate")

    # Iluminacao do Hall
    cmd("setblock -5 85 -55 sea_lantern")
    cmd("setblock 4 85 -55 sea_lantern")
    cmd("setblock -5 85 -70 sea_lantern")
    cmd("setblock 4 85 -70 sea_lantern")

    # Pata Dianteira Direita: SANTUARIO DO PORTAL DO NETHER
    cmd("fill 4 77 -59 8 82 -59 obsidian")
    cmd("fill 5 78 -59 7 81 -59 portal")
    cmd("setblock 3 77 -58 chest 2")
    cmd("setblock 9 77 -58 chest 2")
    cmd("setblock 6 82 -58 crying_obsidian")

    # Pata Dianteira Esquerda: ARMARIA & ESTANDES DE TREINO
    cmd("fill -9 77 -59 -5 77 -59 polished_andesite")
    cmd("setblock -9 78 -59 armor_stand")
    cmd("setblock -7 78 -59 armor_stand")
    cmd("setblock -5 78 -59 armor_stand")
    cmd("setblock -10 77 -55 target")
    cmd("setblock -10 78 -55 target")

    # Pata Traseira Esquerda: COFRE REFORCADO & ENDER CHESTS
    cmd("fill -10 77 -72 -4 77 -72 gold_block")
    cmd("fill -9 78 -72 -5 78 -72 diamond_block")
    cmd("setblock -7 77 -70 ender_chest 2")
    cmd("setblock -6 77 -70 ender_chest 2")

    # Pata Traseira Direita: POCO INFINITO & ENTRADA PARA A MINA
    cmd("fill 5 77 -71 7 77 -69 smooth_stone_slab")
    cmd("setblock 6 77 -70 water")
    cmd("setblock 4 77 -66 crafting_table")
    cmd("setblock 8 77 -66 barrel 2")

    # Saidas do elevador no Andar 1
    cmd("setblock -1 77 -62 air")
    cmd("setblock 1 77 -62 air")

    # -------------------------------------------------------------------------
    # ANDAR 2: JARDIM ZEN & ESTUFA HIDROPONICA (Y = 95 - 103)
    # -------------------------------------------------------------------------
    # Piso do Andar 2
    cmd("fill -11 94 -67 10 94 -58 dark_oak_planks")
    cmd("fill -8 94 -65 7 94 -60 moss_block")
    cmd("fill -2 94 -64 1 94 -61 polished_deepslate") # area elevador

    # Lago central com vitoria-regia
    cmd("fill -3 94 -63 -2 94 -62 water")
    cmd("fill 2 94 -63 3 94 -62 water")
    cmd("setblock -3 95 -63 waterlily")
    cmd("setblock 2 95 -63 waterlily")

    # Vegetacao exuberante de Azalea e Glow Berries no teto
    cmd("setblock -7 95 -65 flowering_azalea")
    cmd("setblock 6 95 -65 flowering_azalea")
    cmd("setblock -7 95 -60 moss_carpet")
    cmd("setblock 6 95 -60 moss_carpet")
    cmd("fill -9 103 -66 8 103 -59 sea_lantern 0 replace air")
    cmd("fill -8 103 -65 7 103 -60 dark_oak_trapdoor 13") # persianas de luz

    # Bancos de descanso (stairs)
    cmd("setblock -9 95 -63 spruce_stairs 0")
    cmd("setblock -9 95 -62 spruce_stairs 0")
    cmd("setblock 8 95 -63 spruce_stairs 1")
    cmd("setblock 8 95 -62 spruce_stairs 1")

    # Aberturas elevador no Andar 2
    cmd("setblock -1 95 -62 air")
    cmd("setblock 1 95 -62 air")

    # -------------------------------------------------------------------------
    # ANDAR 3: OFICINA DE METALURGIA & SUPER FORNALHAS (Y = 104 - 112)
    # -------------------------------------------------------------------------
    # Piso
    cmd("fill -11 103 -67 10 103 -58 polished_deepslate_tiles")
    cmd("fill -2 103 -64 1 103 -61 polished_blackstone")

    # Parede Norte: Bateria de Alto-Fornos e Defumadores Automaticos
    cmd("fill -10 104 -67 -4 104 -67 blast_furnace 3")
    cmd("fill 3 104 -67 9 104 -67 smoker 3")
    cmd("fill -10 105 -67 -4 105 -67 hopper 0")
    cmd("fill 3 105 -67 9 105 -67 hopper 0")
    cmd("fill -10 106 -67 -4 106 -67 chest 3")
    cmd("fill 3 106 -67 9 106 -67 chest 3")

    # Bancadas de Trabalho especializadas
    cmd("setblock -10 104 -60 crafting_table")
    cmd("setblock -9 104 -60 smithing_table")
    cmd("setblock -8 104 -60 stonecutter")
    cmd("setblock -7 104 -60 grindstone")
    cmd("setblock -6 104 -60 anvil")
    cmd("setblock 5 104 -60 cartography_table")
    cmd("setblock 6 104 -60 fletching_table")
    cmd("setblock 7 104 -60 loom")
    cmd("setblock 8 104 -60 ender_chest 2")
    cmd("setblock 9 104 -60 crafting_table")

    # Iluminacao
    cmd("setblock -6 110 -63 sea_lantern")
    cmd("setblock 5 110 -63 sea_lantern")

    # Aberturas elevador no Andar 3
    cmd("setblock -1 104 -62 air")
    cmd("setblock 1 104 -62 air")

    # -------------------------------------------------------------------------
    # ANDAR 4: LABORATORIO DE ALQUIMIA & POCOES (Y = 113 - 121)
    # -------------------------------------------------------------------------
    # Piso xadrez de purpur e blackstone
    cmd("fill -11 112 -67 10 112 -58 purpur_block")
    cmd("fill -8 112 -65 7 112 -60 polished_blackstone")
    cmd("fill -2 112 -64 1 112 -61 polished_deepslate")

    # Bancada Alquimica Central
    cmd("fill -7 113 -65 -4 113 -65 polished_diorite")
    cmd("setblock -7 114 -65 brewing_stand 0")
    cmd("setblock -6 114 -65 brewing_stand 0")
    cmd("setblock -5 114 -65 brewing_stand 0")
    cmd("setblock -4 113 -65 cauldron 3") # Caldeirao cheio d'agua

    cmd("fill 3 113 -65 6 113 -65 polished_diorite")
    cmd("setblock 3 114 -65 brewing_stand 0")
    cmd("setblock 4 114 -65 brewing_stand 0")
    cmd("setblock 5 114 -65 brewing_stand 0")
    cmd("setblock 6 113 -65 cauldron 3")

    # Barricas de reagentes e ingredientes alquimicos
    cmd("fill -10 113 -60 -5 114 -60 barrel 2")
    cmd("fill 4 113 -60 9 114 -60 barrel 2")

    # Iluminacao mistica
    cmd("setblock -6 118 -63 soul_lantern")
    cmd("setblock 5 118 -63 soul_lantern")

    # Aberturas elevador no Andar 4
    cmd("setblock -1 113 -62 air")
    cmd("setblock 1 113 -62 air")

    # -------------------------------------------------------------------------
    # ANDAR 5: GRANDE BIBLIOTECA & ALTAR DE ENCANTAMENTOS (Y = 122 - 130)
    # -------------------------------------------------------------------------
    # Piso nobre de madeira de pinheiro (spruce) com tapete vermelho
    cmd("fill -11 121 -67 10 121 -58 spruce_planks")
    cmd("fill -7 121 -65 6 121 -60 red_carpet")
    cmd("fill -2 121 -64 1 121 -61 polished_deepslate")

    # ALTAR DE ENCANTAMENTOS NIVEL 30 (Alinhamento perfeito de estantes)
    # Mesa central em X = -5, Z = -63
    cmd("setblock -5 122 -63 enchanting_table")
    # Estantes ao redor da mesa (garantindo nivel 30)
    cmd("fill -7 122 -65 -7 123 -61 bookshelf")
    cmd("fill -7 122 -65 -3 123 -65 bookshelf")
    cmd("fill -7 122 -61 -3 123 -61 bookshelf")
    cmd("fill -3 122 -65 -3 123 -61 chiseled_bookshelf")
    cmd("setblock -3 122 -63 air") # espaco de acesso a mesa
    cmd("setblock -4 122 -62 chest 3") # Bau com Lapis Lazuli e Livros

    # Segunda Ala da Biblioteca: Leitura & Estudos (Lado Leste)
    cmd("fill 4 122 -66 8 124 -66 bookshelf")
    cmd("fill 4 122 -59 8 124 -59 chiseled_bookshelf")
    cmd("setblock 5 122 -63 lectern 2")
    cmd("setblock 7 122 -63 lectern 2")
    cmd("setblock 6 122 -61 ender_chest 2")

    # Iluminacao acolhedora
    cmd("setblock -5 126 -63 sea_lantern")
    cmd("setblock 6 126 -63 sea_lantern")

    # Aberturas elevador no Andar 5
    cmd("setblock -1 122 -62 air")
    cmd("setblock 1 122 -62 air")

    # -------------------------------------------------------------------------
    # ANDAR 6: GRANDE ARMAZEM & CENTRO LOGISTICO (Y = 131 - 142)
    # (Dentro da cabeca do Creeper - Espaco gigante de 22x22!)
    # -------------------------------------------------------------------------
    # Piso
    cmd("fill -11 130 -73 10 130 -52 polished_andesite")
    cmd("fill -8 130 -70 7 130 -55 oak_planks")
    cmd("fill -2 130 -64 1 130 -61 polished_deepslate")

    # 4 Corredores de Baus Duplos e Barris Organizadores
    # Corredor 1 (Norte): Minerios e Metais Raros
    cmd("fill -10 131 -71 -4 133 -71 chest 3")
    cmd("fill 3 131 -71 9 133 -71 chest 3")

    # Corredor 2: Equipamentos, Armas e Ferramentas
    cmd("fill -10 131 -66 -4 133 -66 chest 3")
    cmd("fill 3 131 -66 9 133 -66 chest 3")

    # Corredor 3: Blocos de Construcao
    cmd("fill -10 131 -59 -4 133 -59 chest 2")
    cmd("fill 3 131 -59 9 133 -59 chest 2")

    # Corredor 4 (Sul): Alimentos, Pocao, Polvora e Drops de Mobs
    cmd("fill -10 131 -54 -4 133 -54 barrel 2")
    cmd("fill 3 131 -54 9 133 -54 barrel 2")

    # Mesa de triagem central e bigornas
    cmd("setblock -5 131 -62 anvil")
    cmd("setblock -4 131 -62 smithing_table")
    cmd("setblock 3 131 -62 grindstone")
    cmd("setblock 4 131 -62 ender_chest 2")
    cmd("setblock 5 131 -62 crafting_table")

    # Iluminacao
    cmd("fill -8 136 -68 7 136 -57 sea_lantern 0 replace air")

    # Aberturas elevador no Andar 6
    cmd("setblock -1 131 -62 air")
    cmd("setblock 1 131 -62 air")

    # -------------------------------------------------------------------------
    # ANDAR 7: SUITE MASTER SUPREMA NO TOPO (Y = 143 - 153)
    # (Com vista panoramica espetacular pelos OLHOS do Creeper!)
    # -------------------------------------------------------------------------
    # Piso de luxo em quartzo e carpete tematico Verde/Lima
    cmd("fill -11 142 -73 10 142 -52 smooth_quartz")
    cmd("fill -8 142 -70 7 142 -55 lime_carpet")
    cmd("fill -2 142 -64 1 142 -61 polished_deepslate")

    # CAMA KING-SIZE 1 (Para x12ultimatepass - Lado Esquerdo)
    # Cama dupla Lima com pilares de quartzo e abobada
    cmd("fill -8 143 -68 -7 143 -68 smooth_quartz")
    cmd("setblock -8 143 -67 lime_bed 0")
    cmd("setblock -7 143 -67 lime_bed 0")
    cmd("setblock -9 143 -67 smooth_quartz_stairs 0")
    cmd("setblock -6 143 -67 smooth_quartz_stairs 1")
    cmd("setblock -8 143 -69 flower_pot")
    cmd("setblock -7 143 -69 soul_lantern")

    # CAMA KING-SIZE 2 (Para AerialTuba9051 - Lado Direito)
    # Cama dupla Verde com dossel
    cmd("fill 6 143 -68 7 143 -68 smooth_quartz")
    cmd("setblock 6 143 -67 green_bed 0")
    cmd("setblock 7 143 -67 green_bed 0")
    cmd("setblock 5 143 -67 smooth_quartz_stairs 0")
    cmd("setblock 8 143 -67 smooth_quartz_stairs 1")
    cmd("setblock 6 143 -69 flower_pot")
    cmd("setblock 7 143 -69 soul_lantern")

    # Area de Estar & Lounge
    cmd("setblock -1 143 -69 jukebox")
    cmd("setblock 0 143 -69 ender_chest 2")
    cmd("setblock -2 143 -69 chest 2")
    cmd("setblock 1 143 -69 chest 2")

    # Armaduras em exposicao no quarto
    cmd("setblock -10 143 -60 armor_stand")
    cmd("setblock 9 143 -60 armor_stand")

    # Varanda / Mirante diante dos OLHOS do Creeper (Z = -52)
    # Plataformas dianteiras de vidro para contemplar o mundo
    cmd("fill -9 143 -53 -4 143 -53 polished_blackstone")
    cmd("fill 3 143 -53 8 143 -53 polished_blackstone")

    # Iluminacao no teto do quarto
    cmd("fill -7 151 -68 6 151 -57 sea_lantern 0 replace air")

    # Aberturas elevador no Andar 7
    cmd("setblock -1 143 -62 air")
    cmd("setblock 1 143 -62 air")

    # -------------------------------------------------------------------------
    # TELHADO: TERRACO MIRANTE & CREEPER CHARGED LIGHTNING ROD (Y = 154)
    # -------------------------------------------------------------------------
    # Piso do telhado
    cmd("fill -11 154 -73 10 154 -52 mossy_stone_bricks")
    cmd("fill -12 155 -74 11 155 -51 mossy_stone_brick_stairs 0 keep")
    cmd("fill -12 155 -74 11 155 -51 stone_brick_wall")
    cmd("fill -11 155 -73 10 155 -52 air")

    # Claraboia central de vidro no telhado
    cmd("fill -4 154 -65 3 154 -60 tinted_glass")

    # Monumento ao Creeper Eletrizado: Para-raios central sobre pedestal de cobre
    cmd("setblock 0 155 -63 copper_block")
    cmd("setblock 0 156 -63 lightning_rod")
    cmd("setblock -1 155 -63 soul_lantern")
    cmd("setblock 1 155 -63 soul_lantern")

    # Alcapao de acesso ao telhado
    cmd("setblock 0 154 -62 dark_oak_trapdoor 0")

    # =========================================================================
    # 8. CONEXAO AEREA / SKYBRIDGE PARA A ESTACAO DOS JOGADORES (Y = 150)
    # =========================================================================
    print("8/8 - Criando passarela aerea iluminada ate a estacao...")
    # Estacao dos jogadores esta em torno de (10, 150, 18) e a maquina em (0, 150, 0)
    # Conectar o mirante da cabeca (Z = -51) com um mirante sul
    cmd("fill -2 150 -51 1 150 -46 smooth_quartz")
    cmd("fill -2 151 -51 -2 151 -46 glass")
    cmd("fill 1 151 -51 1 151 -46 glass")
    cmd("fill -1 150 -46 0 150 -46 lantern")

    # Remover ticking area temporaria
    cmd("tickingarea remove creeper_mansion_area")

    print("\n==================================================================")
    print(" [SUCESSO] MANSAO ESTATUA GIGANTE DE CREEPER CONCLUIDA COM EXCELENCIA!")
    print(" Coordenadas: X [-12 a 11], Y [76 a 155], Z [-74 a -51]")
    print(" Altura Total: 78 blocos | 7 Andares Completos e Funcionais")
    print("==================================================================")

    cmd("say [BDS] Mansao Estatua Gigante de Creeper concluida com sucesso!")
    cmd("say [BDS] 7 Andares funcionais: Quarto no Topo, Armazem, Biblioteca Nivel 30, Alquimia, Fornalhas, Jardim Zen, Hall e Elevadores!")

if __name__ == '__main__':
    build_creeper_mansion()
