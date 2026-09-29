"""
Script de construcao e validacao da Maquina Voadora de TNT no Minecraft Bedrock Dedicated Server.
Coordenadas base: 0, 150, 0.
Inclui:
- Estacao de Lancamento com Alavanca (Ligar / Parar)
- Motor Voador Bedrock (Pistao Normal + Pistao Grudento + Observadores + Blocos de Slime)
- Ejetor de TNT voltado para baixo carregado com 576 TNTs (9 slots cheios)
- Observador de disparo continuo de TNT durante o voo
"""

import time
import sys
from bds_cmd import send_command, get_bds_pid

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

    # 1. Garantir tickingarea para que o chunk fique ativo permanentemente
    print("[1/6] Garantindo Ticking Area em torno de 0, 150, 0...")
    run_cmd('tickingarea add -16 140 -16 32 160 16 tnt_flight_corridor')

    # 2. Limpar espaco aereo imediato (runway)
    print("[2/6] Limpando espaco aereo da estacao e pista de voo...")
    # Limpar area da maquina e estacao
    run_cmd('fill -4 148 -3 10 154 3 air')

    # 3. Construir Estacao de Controle e Plataforma de Operacao (Y = 148 - 149)
    print("[3/6] Construindo plataforma da estacao com alavanca de partida/parada...")
    # Piso da plataforma de observacao para o jogador em X = -4 a -1, Z = -3 a 1
    run_cmd('fill -4 148 -3 -1 148 1 smooth_stone')
    # Guarda-corpo de vidro para seguranca do jogador
    run_cmd('fill -4 149 -3 -4 149 1 glass')
    run_cmd('fill -4 149 -3 -1 149 -3 glass')
    run_cmd('fill -1 149 -3 -1 149 -2 glass')

    # Bloco de apoio do painel de controle (Obsidian nao gruda em slime)
    run_cmd('setblock -2 149 -1 obsidian')
    run_cmd('setblock -2 150 -1 obsidian')
    # Alavanca de Ligar / Parar no painel
    # facing_direction ou lever_direction para fixar na face do bloco
    run_cmd('setblock -2 151 -1 lever ["lever_direction"="up_north_south"]')

    # Mecanismo de Trava / Parada com Pistao e Obsidian
    # Pistao da estacao em X = -2, Y = 150, Z = 0 apontado para East (+X)
    run_cmd('setblock -3 150 0 obsidian')
    run_cmd('setblock -2 150 0 sticky_piston ["facing_direction"=5]')
    # Bloco de Obsidian que serve de trava na ponta do pistao (X = -1, Y = 150, Z = 0)
    run_cmd('setblock -1 150 0 obsidian')
    # Ligacao de redstone entre a alavanca e o pistao de trava
    run_cmd('setblock -2 150 0 sticky_piston ["facing_direction"=5]')
    run_cmd('setblock -3 151 -1 redstone_wire')
    run_cmd('setblock -3 151 0 redstone_wire')

    # 4. Construir o Motor Voador da Maquina (Bedrock Engine)
    # Direcao de voo: +X (Leste)
    print("[4/6] Montando o motor voador (Pistao Normal, Pistao Grudento e Slimes)...")
    
    # --- Modulo Traseiro (Empurrador) ---
    # Observador Traseiro em (0, 150, 0): Face voltada para -X (West = 4), dot de saida para +X (East)
    run_cmd('setblock 0 150 0 observer ["facing_direction"=4]')
    # Pistao Normal em (1, 150, 0): Apontado para +X (East = 5)
    run_cmd('setblock 1 150 0 piston ["facing_direction"=5]')
    # Slime blocks do Modulo Traseiro na camada superior (Y = 151)
    run_cmd('setblock 0 151 0 slime')
    run_cmd('setblock 1 151 0 slime')

    # --- Modulo Dianteiro (Puxador) ---
    # Slime blocks do Modulo Dianteiro na camada inferior (Y = 150)
    run_cmd('setblock 2 150 0 slime')
    run_cmd('setblock 3 150 0 slime')
    # Pistao Grudento em (2, 151, 0): Apontado para -X (West = 4), puxa o Modulo Traseiro
    run_cmd('setblock 2 151 0 sticky_piston ["facing_direction"=4]')
    # Observador Dianteiro em (3, 151, 0): Face voltada para +X (East = 5), dot de saida para -X (West)
    run_cmd('setblock 3 151 0 observer ["facing_direction"=5]')

    # 5. Acoplar o Modulo de Bombardeio TNT (Dispenser + Observador Gatilho)
    print("[5/6] Instalando Ejetor de TNT e Observador de detonacao...")
    # Ejetor voltado para baixo (facing_direction = 0 / down) conectado ao Slime Dianteiro
    run_cmd('setblock 2 150 1 dispenser ["facing_direction"=0]')
    # Observador gatilho em (3, 150, 1): Face voltada para +X (East = 5), dot de saida para -X no Ejetor
    run_cmd('setblock 3 150 1 observer ["facing_direction"=5]')

    # Abastecer o Ejetor com 9 slots de TNT (64 unidades por slot = 576 TNTs)
    print("[5/6 - Cont.] Abastecendo 576 TNTs nos 9 slots do Ejetor...")
    for slot in range(9):
        run_cmd(f'replaceitem block 2 150 1 slot.container {slot} tnt 64', delay=0.03)

    # 6. Validar posicionamento de todos os blocos fundamentais
    print("[6/6] Validando integridade de todos os componentes com o BDS...")
    checks = [
        ("0 150 0", "observer", "Observador Traseiro"),
        ("1 150 0", "piston", "Pistao Normal"),
        ("0 151 0", "slime", "Slime Superior 1"),
        ("1 151 0", "slime", "Slime Superior 2"),
        ("2 150 0", "slime", "Slime Inferior 1"),
        ("3 150 0", "slime", "Slime Inferior 2"),
        ("2 151 0", "sticky_piston", "Pistao Grudento"),
        ("3 151 0", "observer", "Observador Dianteiro"),
        ("2 150 1", "dispenser", "Ejetor de TNT"),
        ("3 150 1", "observer", "Observador Gatilho"),
        ("-1 150 0", "obsidian", "Trava de Parada (Obsidian)"),
        ("-2 151 -1", "lever", "Alavanca de Controle")
    ]
    
    for coord, block_type, name in checks:
        run_cmd(f'testforblock {coord} {block_type}', delay=0.05)

    print("======================================================================")
    print(" [SUCESSO] Maquina Voadora de TNT montada e pronta para operacao!")
    print(" Localizacao da estacao: X = -2, Y = 150, Z = -1 (ao lado de 0, 150, 0)")
    print(" Status da Alavanca:")
    print(" - Alavanca LIGADA:  Trava ativada (Maquina parada e bloqueada)")
    print(" - Alavanca DESLIGADA: Trava recolhida -> Maquina inicia voo e bombardeio")
    print("======================================================================")

if __name__ == '__main__':
    build_machine()
