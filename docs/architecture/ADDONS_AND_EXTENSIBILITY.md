<!--
Responsabilidade: Especificação da arquitetura de extensibilidade para Add-ons, Resource Packs,
Behavior Packs e Scripts da Bedrock Scripting API, garantindo isolamento do núcleo vanilla do BDS.
-->

# Extensibilidade: Add-ons, Pacotes de Recursos e Scripts

## 1. Princípios de Extensibilidade sem Modificação do Núcleo

O Bedrock Dedicated Server é distribuído como um binário compilado fechado sem suporte a loaders Java tradicionais (como Spigot, Paper ou Forge). No entanto, o motor Bedrock oferece mecanismos nativos avançados para modificação do jogo através de:
- **Resource Packs (Pacotes de Recursos)**: Modificam texturas, modelos geométricos, sons, interface e partículas.
- **Behavior Packs (Pacotes de Comportamento)**: Definem componentes de entidades, tabelas de saques (loot tables), receitas e geradores.
- **Bedrock Scripting API (JavaScript/TypeScript)**: Execução de lógica de jogo no servidor via módulo oficial `@minecraft/server`.

**Regra de Ouro**: Nenhum add-on, script ou textura personalizada deve ser injetado diretamente nas pastas vanilla de versão (`/opt/bds/versions/<versao>/`). Todo o conteúdo customizado deve residir em `/opt/bds/data/custom_packs/` e ser vinculado via manifesto ao mundo ou aos diretórios de sistema.

---

## 2. Mecanismos Oficiais de Ativação de Pacotes

*Fonte: `bedrock_server_how_to.html` e Microsoft Creator Portal ([https://learn.microsoft.com/minecraft/creator](https://learn.microsoft.com/minecraft/creator))*

### 2.1. Pacotes por Mundo (`world_behavior_packs.json` e `world_resource_packs.json`)
Para ativar pacotes em um mundo específico:
1. Os arquivos do pacote descompactados são posicionados em:
   - `/opt/bds/runtime/development_behavior_packs/` ou `behavior_packs/`
   - `/opt/bds/runtime/development_resource_packs/` ou `resource_packs/`
2. No diretório do mundo ativo (`/opt/bds/data/worlds/<level-name>/`), cria-se o arquivo `world_behavior_packs.json` e/ou `world_resource_packs.json` contendo o `pack_id` (UUID) e a `version` definidos no `manifest.json` do add-on:

```json
[
  {
    "pack_id": "00000000-0000-0000-0000-000000000001",
    "version": [1, 0, 0]
  }
]
```

### 2.2. Pacotes Globais Administrativos (`system_behavior_packs` e `system_resource_packs`)
A documentação oficial do BDS v1.26.52.3 introduz e detalha os diretórios `system_behavior_packs` e `system_resource_packs`:
- **Finalidade**: Armazenar pacotes de administração do servidor aplicados automaticamente em todos os mundos carregados pelo BDS.
- **Proteção de UUID**: Os UUIDs definidos nesses pacotes são protegidos pelo motor do servidor; caso um pacote de usuário tente registrar módulos com o mesmo identificador, o carregamento do pacote de usuário é rejeitado, prevenindo sobrescrita de regras administrativas.

---

## 3. Gestão e Configuração da Scripting API

A Bedrock Scripting API permite automações orientadas a eventos (ex.: detecção de jogadores, sistemas de economia local, moderação de chat).

No `server.properties` oficial (v1.26.52.3), existem parâmetros dedicados para governança de scripts:

| Propriedade Oficial | Valor Padrão | Recomendação de Produção | Descrição |
| :--- | :--- | :--- | :--- |
| `allow-inbound-script-debugging` | `false` | `false` | Impede depuração de scripts via conexões externas. |
| `allow-outbound-script-debugging` | `false` | `false` | Impede conexão do servidor a depuradores remotos. |
| `script-watchdog-enable` | `true` | `true` | Ativa o watchdog de proteção contra travamento de scripts. |
| `script-watchdog-hang-threshold` | `10000` | `10000` (ms) | Tempo limite de 10s para tick congelado antes de disparar exceção. |
| `script-watchdog-memory-warning` | `100` | `150` (MB) | Limite de uso de memória de scripts para emitir alerta no log. |
| `script-watchdog-memory-limit` | `250` | `300` (MB) | Limite máximo de memória de script antes de salvar e encerrar o mundo. |

---

## 4. Isolamento e Persistência através de Atualizações

Para garantir que a atualização de binários do BDS nunca apague pacotes instalados:

1. Diretório dedicado `/opt/bds/data/custom_packs/`:
   ```
   /opt/bds/data/custom_packs/
   ├── behavior_packs/
   │   └── meu_addon_customizado/
   │       ├── manifest.json
   │       └── scripts/
   └── resource_packs/
       └── minhas_texturas/
           └── manifest.json
   ```
2. Links simbólicos no diretório `/opt/bds/runtime/`:
   O script de montagem de runtime cria links apontando cada pasta de `/opt/bds/data/custom_packs/` para o diretório de execução correspondente.
3. Ao atualizar a versão do BDS, o novo pacote vanilla é descompactado sem interferir nas pastas de dados do operador.
