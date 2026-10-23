"""
Testes unitarios para a integracao do mapa Cobbled Farms no Minecraft Bedrock Server.
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

import gerenciar_cobbledrock as gc
import gerenciar_mods
import instalar_cobbled_farms as icf


class TestCobbledFarmsIntegration(unittest.TestCase):
    def setUp(self):
        self.world_dir = REPO_ROOT / "server" / "data" / "worlds" / "Cobbled Farms"

    def test_cobbled_farms_directory_structure(self):
        """Valida que a pasta do Cobbled Farms possui toda a estrutura nativa Bedrock."""
        self.assertTrue(self.world_dir.is_dir(), "A pasta Cobbled Farms deve existir em server/data/worlds/")
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

        # Valida conteudo de levelname.txt
        levelname_content = (self.world_dir / "levelname.txt").read_text(encoding="utf-8").strip()
        self.assertEqual(levelname_content, "Cobbled Farms")

    def test_cobblemon_addons_integration(self):
        """Valida se os pacotes do CobbleDrock (Core e Content) estao ativos no Cobbled Farms."""
        bp_path = self.world_dir / "world_behavior_packs.json"
        rp_path = self.world_dir / "world_resource_packs.json"

        bps = gerenciar_mods.load_json_file(bp_path)
        rps = gerenciar_mods.load_json_file(rp_path)

        active_bp_ids = {entry.get("pack_id") for entry in bps if isinstance(entry, dict)}
        active_rp_ids = {entry.get("pack_id") for entry in rps if isinstance(entry, dict)}

        for bp_id in gc.COBBLEDROCK_BP_IDS:
            self.assertIn(bp_id, active_bp_ids, f"BP {bp_id} deve estar ativo no Cobbled Farms")

        for rp_id in gc.COBBLEDROCK_RP_IDS:
            self.assertIn(rp_id, active_rp_ids, f"RP {rp_id} deve estar ativo no Cobbled Farms")

        status = gerenciar_mods.get_mod_status("cobbledrock", "Cobbled Farms")
        self.assertTrue(status["is_active"], "CobbleDrock deve constar como 100% ativo")

    def test_list_available_worlds_discovers_cobbled_farms(self):
        """Verifica se list_available_worlds reconhece Cobbled Farms como mundo valido."""
        worlds = gerenciar_mods.list_available_worlds()
        self.assertIn("Cobbled Farms", worlds)
        self.assertIn("Bedrock level", worlds)
        self.assertIn("Tryzz's Parkour Spiral", worlds)

    def test_world_switching_flow(self):
        """Valida alternancia de mundos entre Cobbled Farms e outros mundos."""
        initial = gerenciar_mods.read_level_name()

        try:
            # Alterna para Cobbled Farms
            self.assertTrue(gerenciar_mods.switch_active_world("Cobbled Farms"))
            self.assertEqual(gerenciar_mods.read_level_name(), "Cobbled Farms")

            # Alterna para Bedrock level
            self.assertTrue(gerenciar_mods.switch_active_world("Bedrock level"))
            self.assertEqual(gerenciar_mods.read_level_name(), "Bedrock level")

            # Retorna para Cobbled Farms
            self.assertTrue(gerenciar_mods.switch_active_world("Cobbled Farms"))
            self.assertEqual(gerenciar_mods.read_level_name(), "Cobbled Farms")
        finally:
            gerenciar_mods.switch_active_world(initial)

    def test_chunker_cli_readiness(self):
        """Garante que a ferramenta oficial Chunker CLI esta disponivel para reconversao/atualizacao."""
        chunker_jar = icf.ensure_chunker_jar()
        self.assertTrue(chunker_jar.is_file())
        self.assertGreater(chunker_jar.stat().st_size, 10_000_000)


if __name__ == "__main__":
    unittest.main()
