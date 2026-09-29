# Mansao Estatua Gigante de Creeper - Manual Tecnico e Guia Estrutural

## 1. Visao Geral
A **Mansao Estatua Gigante de Creeper** e uma megaestrutura residencial e logistica construida no mundo do Bedrock Dedicated Server seguindo com fidelidade a proporcao oficial **3:1** da geometria do mob Creeper do Minecraft (1 pixel original = 3x3x3 blocos).

- **Coordenadas Centrais:** `X = 0`, `Z = -63`
- **Volume Delimitador (Bounding Box):**
  - **Eixo X (Largura):** `-12` a `11` (24 blocos de largura total)
  - **Eixo Y (Altura):** `76` a `155` (78 blocos de altura total)
  - **Eixo Z (Profundidade):** `-74` a `-51` (24 blocos de profundidade total)
- **Orientacao:** Face frontal do Creeper voltada para o **Sul** (`Z = -51`), encarando diretamente a estacao aerea dos jogadores e o horizonte.

```
       [ Y = 155 ] -- Terraco Mirante & Para-raios Creeper Eletrizado
    +---------------+
    |   [OO] [OO]   | [ Y = 143 - 153 ] -- Andar 7: Suite Master no Topo (Olhos Panoramicos)
    |     [---]     | [ Y = 131 - 142 ] -- Andar 6: Grande Armazem Logistico (Boca/Janela)
    +---------------+
        |       |     [ Y = 122 - 130 ] -- Andar 5: Biblioteca & Altar de Encantamentos Nv. 30
        | Tronco|     [ Y = 113 - 121 ] -- Andar 4: Laboratorio de Alquimia & Pocao
        |       |     [ Y = 104 - 112 ] -- Andar 3: Oficina de Metalurgia & Super Fornalhas
        |       |     [ Y = 95 - 103  ] -- Andar 2: Jardim Zen & Estufa Hidroponica
    +---------------+
    | Pata |  Pata  | [ Y = 77 - 94   ] -- Andar 1: Hall de Entrada Principal & 4 Patas
    +---------------+
```

---

## 2. Guia de Andares e Funcoes Internas

### Andar 1: Grand Entrance Hall & Complexo das 4 Patas (`Y = 77 - 94`)
- **Acesso Principal:** Portal monumental de madeira escura com placas de pressao na face Sul (`Z = -51`).
- **Pata Dianteira Direita:** Santuario do Portal do Nether completo e aceso em moldura de Obsidian e Crying Obsidian com baus de expedicao.
- **Pata Dianteira Esquerda:** Armaria de treinamento com estandes de armadura e alvos de tiro com arco.
- **Pata Traseira Esquerda:** Cofre-forte reforcado com blocos de Ouro, Diamante e Ender Chests.
- **Pata Traseira Direita:** Pocos de agua infinita e acesso direto a mina profunda.

### Andar 2: Jardim Zen & Estufa Hidroponica (`Y = 95 - 103`)
- **Decoracao:** Grama e blocos de musgo, arbustos floridos de Azalea, vitorias-regias em pequenos lagos interiores e iluminacao suave embutida com persianas de madeira escura.
- **Terracos das Patas:** Saida externa para os terracos ajardinados nas copas das patas dianteiras e traseiras.

### Andar 3: Oficina de Metalurgia & Super Fornalhas (`Y = 104 - 112`)
- **Automacao de Fundicao:** Baterias sincronizadas de Alto-Fornos (*Blast Furnaces*) e Defumadores (*Smokers*) com funis (*hoppers*) e baus duplos superiores e inferiores de alimentacao.
- **Bancadas Completas:** Mesas de Trabalho (*Crafting Tables*), Cortador de Pedras (*Stonecutter*), Forja (*Smithing Table*), Rebolo (*Grindstone*), Bigorna (*Anvil*), Mesa de Cartografia e Tear (*Loom*).

### Andar 4: Laboratorio de Alquimia & Pocao (`Y = 113 - 121`)
- **Bancadas de Pocao:** Bateria de Suportes de Pocao (*Brewing Stands*) e caldeiroes com agua infinita.
- **Armazenamento de Reagentes:** Barris organizados para po de blaze, fungo do nether, lagrimas de ghast, membranas de phantom, bafo de dragao e olhos de aranha.

### Andar 5: Grande Biblioteca Arcana & Altar de Encantamentos (`Y = 122 - 130`)
- **Mesa de Encantamentos Nivel 30:** Posicionamento central com mais de 15 estantes de livros (*Bookshelves* e *Chiseled Bookshelves*) a 1 bloco de distancia, garantindo potencia maxima para encantamentos de nivel 30.
- **Area de Leitura & Lapis:** Baus dedicados a Lapis Lazuli e livros encantados, atracoes (*Lecterns*) para anotações e cristais de ametista iluminados por lanternas das almas.

### Andar 6: Grande Armazem Logistico (`Y = 131 - 142`)
- **Espaco Gigante (22x22 blocos):** Localizado na parte inferior da cabeca do Creeper.
- **4 Corredores Tematicos:** Mais de 40 Baus Duplos e Barris categorizados por:
  1. *Minerios e Metais Raros* (Netherite, Diamante, Ouro, Ferro, Redstone);
  2. *Armas, Armaduras e Ferramentas*;
  3. *Blocos de Construcao e Madeiras*;
  4. *Agricultura, Alimentos e Drops de Mobs* (Polvora, TNT, Perolas do End).
- **Janela Panoramica:** Abertura frontal em vidro fumê (*tinted glass*) posicionada exatamente no centro do recorte da boca do Creeper.

### Andar 7: Suite Master Suprema no Topo (`Y = 143 - 153`)
- **Camas Duplas King-Size com Dossel:**
  - Cama Lima Real para `x12ultimatepass`.
  - Cama Verde Esmeralda Real para `AerialTuba9051`.
- **Visao Panoramica pelos Olhos do Creeper:** Os olhos da estatua sao compostos por vidro escurecido (*black stained glass* e *tinted glass*). De fora mantem a assinatura preta do Creeper; de dentro funciona como mirante panoramico.
- **Lounge:** Jukebox com discos de musica, Ender Chest, criados-mudos com lanternas das almas e vasos de flores.

### Telhado: Terraco Mirante & Para-raios do Creeper Eletrizado (`Y = 154 - 155`)
- Mirante de observacao a ceu aberto com parapeito e claraboia central de vidro.
- Para-raios central sobre pedestal de cobre (*Charged Creeper Tribute*).

---

## 3. Sistema de Circulacao Vertical
1. **Elevador de Bolhas para Subida (Soul Sand):**
   - Coordenadas: `X = -1`, `Z = -63`.
   - Propulsa o jogador do Andar 1 ao Andar 7 em menos de 3 segundos atraves de coluna de agua sobre Soul Sand.
2. **Elevador de Bolhas para Descida (Magma Block):**
   - Coordenadas: `X = 1`, `Z = -63`.
   - Permite descida suave e veloz ate a base.
3. **Eixo Central de Andaimes (*Scaffolding*):**
   - Coordenadas: `X = 0`, `Z = -62`.
   - Permite subir e descer parando livremente em qualquer um dos 7 andares.
