# Máquina Voadora de TNT no Minecraft Bedrock Dedicated Server

Documentação técnica e manual de operação da **Máquina Voadora de TNT (TNT Bomber)** com estação de controle e alavanca de partida/parada, construída nas coordenadas `(0, 150, 0)`.

---

## 1. Visão Geral e Localização

* **Coordenadas Centrais da Máquina:** `X = 0, Y = 150, Z = 0`
* **Direção de Voo:** `+X` (Leste / East)
* **Estação de Controle (Plataforma):** `X = -4` até `X = -1`, `Y = 148` a `151`, `Z = -3` até `1`
* **Localização da Alavanca (Start / Stop):** `X = -2, Y = 151, Z = -1`
* **Carga de TNT Inicial:** 576 blocos de TNT (9 slots de 64 no Ejetor)
* **Ticking Area Ativa:** `tnt_flight_corridor` (assegura processamento contínuo dos chunks mesmo sem jogadores próximos)

---

## 2. Princípios de Engenharia no Bedrock Edition

1. **Inexistência de TNT Duplication:**
   No Minecraft Bedrock Edition, bugs de duplicação de TNT da versão Java (com coral morto e carrinho) não existem. A única forma legítima e oficial de lançar TNTs em voo é utilizando um **Ejetor (Dispenser)** apontado para baixo (`facing_direction = 0`), abastecido com blocos de TNT.
2. **Motor Deslocado em Camadas (Diagonal Slime Isolation):**
   Para evitar que os blocos de slime das duas metades do motor grudem entre si (o que travaria os pistões), o motor utiliza a clássica geometria de camadas alternadas:
   * **Módulo Traseiro (Empurrador):** Pistão Normal e Observador na camada inferior (`Y = 150`), Slimes na camada superior (`Y = 151`).
   * **Módulo Dianteiro (Puxador):** Slimes na camada inferior (`Y = 150`), Pistão Grudento e Observador na camada superior (`Y = 151`).
   * Como os blocos de slime se tocam apenas em quinas diagonais, eles não compartilham faces e movem-se livremente sem colar.
3. **Limite de Empuxo (Push Limit):**
   Cada pistão move no máximo 6 blocos por ciclo, bem abaixo do limite de 12 blocos da engine.

---

## 3. Diagrama Esquemático dos Blocos

### Camada Y = 150 (Camada Inferior de Voo)
```
  Z \ X   -2           -1           0            1            2            3
 -------+------------+------------+------------+------------+------------+------------
    1   |    Ar      |    Ar      |    Ar      |    Ar      | Dispenser↓ | Observador→|
    0   | Pistão-G→  | Obsidian   | Observador←| Pistão-N→  | Slime      | Slime      |
   -1   | Obsidian   |    Ar      |    Ar      |    Ar      |    Ar      |    Ar      |
```

### Camada Y = 151 (Camada Superior de Voo)
```
  Z \ X   -2           -1           0            1            2            3
 -------+------------+------------+------------+------------+------------+------------
    1   |    Ar      |    Ar      |    Ar      |    Ar      |    Ar      |    Ar      |
    0   | Redstone   |    Ar      | Slime      | Slime      | Pistão-G←  | Observador→|
   -1   | Alavanca   |    Ar      |    Ar      |    Ar      |    Ar      |    Ar      |
```

---

## 4. Como Operar a Máquina

### Iniciar o Voo (Start):
1. Vá até a plataforma de controle nas coordenadas `(-2, 149, -1)` (voando em modo criativo ou subindo pela escada).
2. Localize a **Alavanca** no painel de obsidian em `(-2, 151, -1)`.
3. Alterne a alavanca para **DESLIGADA**:
   * O pistão da estação recolhe a trava de obsidian.
   * O observador traseiro detecta a mudança de bloco e dá o pulso inicial.
   * A máquina começa a voar em direção a `+X`, soltando TNTs continuamente que caem e detonam no solo.

### Parar a Máquina (Stop):
* Para parar a máquina no ponto de partida, mantenha a alavanca **LIGADA** (trava de obsidian estendida).
* Se a máquina já estiver em voo livre pelo mapa e você quiser fazê-la parar em uma base remota, posicione um bloco de **Obsidian** no caminho do módulo dianteiro (camada `Y = 150` ou `Y = 151`). Como obsidian é imovível, o motor para imediatamente.

### Reabastecer ou Reconstruir:
Para reconstruir a máquina instantaneamente ou recarregar todos os 576 TNTs, execute no terminal:
```powershell
python .\windows\build_tnt_flying_machine.py
```
Ou envie comandos manuais via console IPC:
```powershell
.\windows\bds-cmd.ps1 "replaceitem block 2 150 1 slot.container 0 tnt 64"
```
