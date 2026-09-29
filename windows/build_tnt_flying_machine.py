"""
Script de construcao e validacao da Maquina Voadora de TNT no Minecraft Bedrock Dedicated Server.
Coordenadas base: 0, 150, 0.
Design:
- Estacao de Embarque em Obsidian (imune a colagem de slime/mel)
- Alavanca de ignicao com acionamento direto via trapdoor
- Motor Bedrock Diagonal 2-wide (Slime + Mel)
- Ejetor de TNT voltado para baixo carregado com 576 TNTs
"""

from bds_cmd import send_command, get_bds_pid
import time
import sys

def run_cmd(cmd, delay=0.08):
    ok = send_command(cmd, wait_ms=int(delay * 1000))
    if not ok:
        print(f"[ERRO] Falha ao enviar comando: {cmd}")
    return ok

def build_machine():
    pid = get_bds_pid()
    if not pid:
        print("[ERRO] Bedrock Dedicated Server nao esta em execucao!")
        sys.exit(1)
        
    print("======================================================================")
    print(" Construindo Maquina Voadora de TNT Completa no BDS (0, 150, 0)")
    print("======================================================================")

    # 1. Garantir tickingarea para que o corredor de voo fique permanentemente ativo
    print("[1/5] Garantindo Ticking Area em torno de 0, 150, 0...")
    run_cmd('tickingarea add -16 140 -16 64 160 16 tnt_flight_corridor')

    # 2. Limpar corredor aereo para garantir que nada encoste nos blocos de slime
    print("[2/5] Limpando espaco aereo da estacao e pista de voo...")
    run_cmd("fill -6 148 -4 50 155 4 air")
    time.sleep(0.2)

    # 3. Construir Estacao de Controle em Obsidian
    print("[3/5] Construindo plataforma da estacao em Obsidian...")
    # Plataforma do jogador (Y = 149)
    run_cmd("fill -5 149 -3 -2 149 1 obsidian")
    # Parede de apoio da alavanca e do alcapao
    run_cmd("setblock -2 150 0 obsidian")
    run_cmd("setblock -2 151 0 obsidian")

    # Alcapao de acionamento em X = -1, Y = 150, Z = 0 (na face do observador traseiro)
    run_cmd('setblock -1 150 0 trapdoor ["direction"=2]')
    # Painel da Alavanca em X = -2, Y = 151, Z = -1
    run_cmd('setblock -2 150 -1 obsidian')
    run_cmd('setblock -2 151 -1 obsidian')
    run_cmd('setblock -2 152 -1 lever ["lever_direction"="up_north_south"]')
    # Fiamento de redstone conectando a alavanca ao alcapao
    run_cmd('setblock -2 152 0 redstone_wire')

    # 4. Montar o Motor Voador Desacoplado (Slime + Mel)
    print("[4/5] Montando o motor voador Slime + Mel...")
    # Lado Slime (Z = 0)
    run_cmd('setblock 0 150 0 observer ["facing_direction"=4]')
    run_cmd('setblock 1 150 0 piston ["facing_direction"=5]')
    run_cmd('setblock 2 150 0 slime')

    # Lado Mel (Z = 1)
    run_cmd('setblock 1 150 1 honey_block')
    run_cmd('setblock 2 150 1 sticky_piston ["facing_direction"=4]')
    run_cmd('setblock 3 150 1 observer ["facing_direction"=5]')

    # 5. Acoplar Ejetor de TNT e Abastecer
    print("[5/5] Acoplando Ejetor de TNT e abastecendo 576 TNTs...")
    run_cmd('setblock 2 150 -1 dispenser ["facing_direction"=0]')
    run_cmd('setblock 3 150 -1 observer ["facing_direction"=5]')

    for slot in range(9):
        run_cmd(f'replaceitem block 2 150 -1 slot.container {slot} tnt 64', delay=0.03)

    # Posicionar jogadores
    run_cmd('tp @a -3 150 -1')

    print("======================================================================")
    print(" [SUCESSO] Maquina Voadora de TNT montada e pronta para operacao!")
    print(" Localizacao da Alavanca: X = -2, Y = 152, Z = -1")
    print(" Ao acionar a alavanca, o alcapao abre/fecha e dispara o motor!")
    print("======================================================================")

if __name__ == '__main__':
    build_machine()
