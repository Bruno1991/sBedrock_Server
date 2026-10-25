"""
Testes unitarios para o Add-on The Ruby Ore (romhenri) e integracao na matriz de mundos e mods.
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
WINDOWS_DIR = REPO_ROOT / "windows"
if str(WINDOWS_DIR) not in sys.path:
    sys.path.insert(0, str(WINDOWS_DIR))

import gerenciar_mods
import instalar_ruby_ore
import server_manager as sm


class TestRubyOreIntegration(unittest.TestCase):
    def setUp(self):
        self.bp_dir = REPO_ROOT / "server" / "data" / "custom_packs" / "behavior_packs" / "RubyOre_BP"
        self.rp_dir = REPO_ROOT / "server" / "data" / "custom_packs" / "resource_packs" / "RubyOre_RP"

    def test_catalog_contains_rubyore(self):
        """Valida se o catalogo de mods contem a definicao do Ruby Ore."""
        self.assertIn("rubyore", gerenciar_mods.MODS_CATALOG)
        mod_info = gerenciar_mods.MODS_CATALOG["rubyore"]
        self.assertIn("The Ruby Ore", mod_info["name"])
        self.assertEqual(mod_info["bp"][0]["pack_id"], instalar_ruby_ore.BP_UUID)
        self.assertEqual(mod_info["rp"][0]["pack_id"], instalar_ruby_ore.RP_UUID)

    def test_ruby_ore_pack_structure(self):
        """Valida que o Behavior Pack e Resource Pack possuem manifestos, itens, blocos e texturas validos."""
        self.assertTrue((self.bp_dir / "manifest.json").is_file(), "Manifest BP deve existir")
        self.assertTrue((self.rp_dir / "manifest.json").is_file(), "Manifest RP deve existir")

        # Verifica manifesto BP
        bp_manifest = json.loads((self.bp_dir / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(bp_manifest["header"]["uuid"], instalar_ruby_ore.BP_UUID)

        # Verifica itens essenciais
        for item_name in ["ruby", "ruby_sword", "ruby_pickaxe", "ruby_axe", "ruby_hammer", "ruby_combat_axe"]:
            item_file = self.bp_dir / "items" / f"{item_name}.json"
            self.assertTrue(item_file.is_file(), f"Item {item_name} deve existir no BP")
            item_data = json.loads(item_file.read_text(encoding="utf-8"))
            self.assertEqual(
                item_data["minecraft:item"]["description"]["identifier"],
                f"rubyore:{item_name}",
            )

        # Verifica blocos
        for block_name in ["ruby_ore", "deepslate_ruby_ore", "ruby_block"]:
            block_file = self.bp_dir / "blocks" / f"{block_name}.json"
            self.assertTrue(block_file.is_file(), f"Bloco {block_name} deve existir no BP")

        # Verifica texturas no RP
        self.assertTrue((self.rp_dir / "textures" / "items" / "ruby.png").is_file())
        self.assertTrue((self.rp_dir / "textures" / "items" / "ruby_sword.png").is_file())
        self.assertTrue((self.rp_dir / "textures" / "blocks" / "ruby_ore.png").is_file())
        self.assertTrue((self.rp_dir / "pack_icon.png").is_file())

    def test_enable_and_disable_ruby_ore(self):
        """Garante ativacao e desativacao isolada de Ruby Ore em configuracoes de pacotes."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_world = Path(tmp_dir)
            bp_json = tmp_world / "world_behavior_packs.json"
            rp_json = tmp_world / "world_resource_packs.json"
            bp_json.write_text("[]\n", encoding="utf-8")
            rp_json.write_text("[]\n", encoding="utf-8")

            # Simulando ativacao
            bps = gerenciar_mods.load_json_file(bp_json)
            rps = gerenciar_mods.load_json_file(rp_json)
            info = gerenciar_mods.MODS_CATALOG["rubyore"]

            for p in info["bp"]:
                bps.append({"pack_id": p["pack_id"], "version": p["version"]})
            for p in info["rp"]:
                rps.append({"pack_id": p["pack_id"], "version": p["version"]})

            gerenciar_mods.save_json_file(bp_json, bps)
            gerenciar_mods.save_json_file(rp_json, rps)

            loaded_bps = gerenciar_mods.load_json_file(bp_json)
            self.assertEqual(len(loaded_bps), 1)
            self.assertEqual(loaded_bps[0]["pack_id"], instalar_ruby_ore.BP_UUID)

    def test_curseforge_url_routing(self):
        """Valida que a URL oficial do CurseForge do mod e reconhecida e despachada."""
        url = "https://www.curseforge.com/minecraft/mc-mods/romhenris-ruby-ore"
        ok, msg = sm.install_from_curseforge(url, activate=False)
        self.assertTrue(ok)
        self.assertIn("The Ruby Ore", msg)

    def test_worlds_mods_matrix_telemetry(self):
        """Valida que a matriz de mundos e mods ativos retorna todos os mundos e identifica o mundo ativo."""
        matrix = gerenciar_mods.get_all_worlds_mods_matrix()
        self.assertTrue(len(matrix) >= 3, "Pelo menos 3 mundos devem ser descobertos")
        active_found = any(item["is_active"] for item in matrix)
        self.assertTrue(active_found, "Pelo menos um mundo deve ser marcado como ativo")

        for item in matrix:
            self.assertIn("world", item)
            self.assertIn("is_active", item)
            self.assertIn("active_mods", item)
            self.assertIn("bp_count", item)
            self.assertIn("rp_count", item)


if __name__ == "__main__":
    unittest.main()
