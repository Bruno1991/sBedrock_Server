"""
Testes unitarios para a integracao do mapa e add-on Lucky OneBlock no Minecraft Bedrock Server.
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
WINDOWS_DIR = REPO_ROOT / "windows"
if str(WINDOWS_DIR) not in sys.path:
    sys.path.insert(0, str(WINDOWS_DIR))

import build_lucky_addon as bla
import gerenciar_mods
import instalar_lucky_oneblock as ilo
import server_manager as sm


class TestLuckyOneBlockIntegration(unittest.TestCase):
    def setUp(self):
        self.world_dir = REPO_ROOT / "server" / "data" / "worlds" / "Lucky OneBlock"
        self.bp_dir = REPO_ROOT / "server" / "data" / "custom_packs" / "behavior_packs" / "LuckyBlock_BP"
        self.rp_dir = REPO_ROOT / "server" / "data" / "custom_packs" / "resource_packs" / "LuckyBlock_RP"

    def test_lucky_oneblock_directory_structure(self):
        """Valida que a pasta do Lucky OneBlock possui toda a estrutura nativa Bedrock."""
        self.assertTrue(self.world_dir.is_dir(), "A pasta Lucky OneBlock deve existir em server/data/worlds/")
        self.assertTrue((self.world_dir / "level.dat").is_file(), "level.dat deve existir")
        self.assertTrue((self.world_dir / "db").is_dir(), "A pasta de banco LevelDB db/ deve existir")
        self.assertTrue((self.world_dir / "levelname.txt").is_file(), "levelname.txt deve existir")
        self.assertTrue((self.world_dir / "world_icon.jpeg").is_file(), "world_icon.jpeg deve existir")
        self.assertTrue(
            (self.world_dir / "world_behavior_packs.json").is_file(),
            "world_behavior_packs.json deve existir",
        )
        self.assertTrue(
            (self.world_dir / "world_resource_packs.json").is_file(),
            "world_resource_packs.json deve existir",
        )

        levelname_content = (self.world_dir / "levelname.txt").read_text(encoding="utf-8").strip()
        self.assertTrue(levelname_content.startswith("Lucky OneBlock"), f"Esperado prefixo 'Lucky OneBlock', obtido: '{levelname_content}'")

    def test_lucky_block_addon_structure(self):
        """Valida que o Behavior Pack e Resource Pack do Lucky Block possuem manifestos e componentes validos."""
        self.assertTrue((self.bp_dir / "manifest.json").is_file(), "Manifest BP deve existir")
        self.assertTrue((self.rp_dir / "manifest.json").is_file(), "Manifest RP deve existir")
        self.assertTrue((self.bp_dir / "blocks" / "lucky_block.json").is_file(), "Definicao do bloco deve existir")
        self.assertTrue((self.bp_dir / "scripts" / "main.js").is_file(), "Scripting OneBlock deve existir")
        self.assertTrue(
            (self.rp_dir / "textures" / "blocks" / "lucky_block.png").is_file(),
            "Textura do bloco deve existir",
        )

        # Checa UUIDs
        bp_manifest = json.loads((self.bp_dir / "manifest.json").read_text(encoding="utf-8"))
        rp_manifest = json.loads((self.rp_dir / "manifest.json").read_text(encoding="utf-8"))

        self.assertEqual(bp_manifest["header"]["uuid"], bla.BP_UUID)
        self.assertEqual(rp_manifest["header"]["uuid"], bla.RP_UUID)

    def test_lucky_block_default_disabled_and_activation_flow(self):
        """Garante que por padrao os mods estao desativados e que a ativacao/desativacao e manual."""
        # Estado padrao: desativado
        gerenciar_mods.disable_all_mods("Lucky OneBlock")
        status_before = gerenciar_mods.get_mod_status("luckyblock", "Lucky OneBlock")
        self.assertFalse(status_before["is_active"], "Por padrao Lucky Block deve iniciar DESATIVADO")

        # Ativa manualmente
        self.assertTrue(gerenciar_mods.enable_mod("luckyblock", "Lucky OneBlock"))
        status_active = gerenciar_mods.get_mod_status("luckyblock", "Lucky OneBlock")
        self.assertTrue(status_active["is_active"], "Lucky Block deve constar como ATIVADO apos enable_mod")

        # Retorna ao padrao desativado
        self.assertTrue(gerenciar_mods.disable_all_mods("Lucky OneBlock"))
        status_after = gerenciar_mods.get_mod_status("luckyblock", "Lucky OneBlock")
        self.assertFalse(status_after["is_active"], "Deve retornar a 100% DESATIVADO apos disable_all_mods")

    def test_catalog_contains_luckyblock(self):
        """Garante que MODS_CATALOG contem a definicao do Lucky Block."""
        self.assertIn("luckyblock", gerenciar_mods.MODS_CATALOG)
        mod = gerenciar_mods.MODS_CATALOG["luckyblock"]
        self.assertEqual(mod["bp"][0]["pack_id"], bla.BP_UUID)
        self.assertEqual(mod["rp"][0]["pack_id"], bla.RP_UUID)

    def test_world_discovery(self):
        """Garante que list_available_worlds descobre Lucky OneBlock."""
        worlds = gerenciar_mods.list_available_worlds()
        self.assertIn("Lucky OneBlock", worlds)

    def test_world_switch_to_lucky_oneblock(self):
        """Garante alternancia limpa para o Lucky OneBlock."""
        initial = gerenciar_mods.read_level_name()
        try:
            self.assertTrue(gerenciar_mods.switch_active_world("Lucky OneBlock"))
            self.assertEqual(gerenciar_mods.read_level_name(), "Lucky OneBlock")
        finally:
            gerenciar_mods.switch_active_world(initial)


if __name__ == "__main__":
    unittest.main()
