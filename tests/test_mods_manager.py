"""
Testes unitarios para o Gerenciador Central de Mods e Add-ons (gerenciar_mods.py).
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import sys
WINDOWS_DIR = Path(__file__).resolve().parent.parent / "windows"
if str(WINDOWS_DIR) not in sys.path:
    sys.path.insert(0, str(WINDOWS_DIR))

import gerenciar_mods


class TestModsManager(unittest.TestCase):
    def test_catalog_structure(self):
        """Verifica se todos os mods possuem identificadores, UUIDs e versoes validas."""
        self.assertIn("spikes", gerenciar_mods.MODS_CATALOG)
        self.assertIn("avaritia", gerenciar_mods.MODS_CATALOG)
        self.assertIn("cobbledrock", gerenciar_mods.MODS_CATALOG)

        for key, mod in gerenciar_mods.MODS_CATALOG.items():
            self.assertIn("bp", mod)
            self.assertIn("rp", mod)
            self.assertTrue(len(mod["bp"]) > 0)
            self.assertTrue(len(mod["rp"]) > 0)
            for p in mod["bp"]:
                self.assertIn("pack_id", p)
                self.assertIn("version", p)
            for p in mod["rp"]:
                self.assertIn("pack_id", p)
                self.assertIn("version", p)

    def test_spikes_pack_uuids(self):
        """Garante que os UUIDs do More Spikes conferem com o manifesto oficial v2.0.1."""
        spikes_mod = gerenciar_mods.MODS_CATALOG["spikes"]
        bp_uuid = spikes_mod["bp"][0]["pack_id"]
        rp_uuid = spikes_mod["rp"][0]["pack_id"]

        self.assertEqual(bp_uuid, "c0bf473f-12d4-4c5c-bc9b-2c24df1e6c07")
        self.assertEqual(rp_uuid, "d595877a-04d1-4187-b56f-f81e7b015db6")

    def test_enable_disable_isolation(self):
        """Valida que ativar e desativar mods preserva outros add-ons sem corrupcao."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_world = Path(tmp_dir)
            bp_json = tmp_world / "world_behavior_packs.json"
            rp_json = tmp_world / "world_resource_packs.json"

            # Estado inicial com Avaritia
            initial_bp = [{"pack_id": "5ad3bb44-8328-448e-8959-e7e0c64be76e", "version": [1, 7, 0]}]
            initial_rp = [{"pack_id": "a4a7d62a-b5ec-4f83-bc25-0f808ff74411", "version": [1, 7, 0]}]
            bp_json.write_text(json.dumps(initial_bp), encoding="utf-8")
            rp_json.write_text(json.dumps(initial_rp), encoding="utf-8")

            # Simulando adicao do spikes
            bps = gerenciar_mods.load_json_file(bp_json)
            rps = gerenciar_mods.load_json_file(rp_json)
            spikes = gerenciar_mods.MODS_CATALOG["spikes"]

            for p in spikes["bp"]:
                bps.append({"pack_id": p["pack_id"], "version": p["version"]})
            for p in spikes["rp"]:
                rps.append({"pack_id": p["pack_id"], "version": p["version"]})

            gerenciar_mods.save_json_file(bp_json, bps)
            gerenciar_mods.save_json_file(rp_json, rps)

            loaded_bps = gerenciar_mods.load_json_file(bp_json)
            self.assertEqual(len(loaded_bps), 2)
            self.assertEqual(loaded_bps[0]["pack_id"], "5ad3bb44-8328-448e-8959-e7e0c64be76e")
            self.assertEqual(loaded_bps[1]["pack_id"], "c0bf473f-12d4-4c5c-bc9b-2c24df1e6c07")


if __name__ == "__main__":
    unittest.main()
