"""
Testes unitarios para o utilitario windows/gerenciar_cobbledrock.py.
"""

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
WINDOWS_DIR = REPO_ROOT / "windows"
if str(WINDOWS_DIR) not in sys.path:
    sys.path.insert(0, str(WINDOWS_DIR))

import gerenciar_cobbledrock as gc


class TestCobbleDrockManager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.world_dir = self.temp_dir / "test_world"
        self.world_dir.mkdir(parents=True, exist_ok=True)

        self.bp_file = self.world_dir / "world_behavior_packs.json"
        self.rp_file = self.world_dir / "world_resource_packs.json"

        # Mock inicial com CobbleDrock e outro add-on
        initial_bps = [
            {"pack_id": "301ce48a-eef2-51b7-926d-b8a68eabcfea", "version": [1, 3, 1]},
            {"pack_id": "56a52fe3-c4d8-588d-9cce-6c6e6c381013", "version": [1, 3, 1]},
            {"pack_id": "5ad3bb44-8328-448e-8959-e7e0c64be76e", "version": [1, 7, 0]},
        ]
        initial_rps = [
            {"pack_id": "3e2975ad-9c9f-5098-8ac6-86bfb6cb6917", "version": [1, 3, 1]},
            {"pack_id": "266755bb-c9eb-5e1f-ad3e-f4e062d58c48", "version": [1, 3, 1]},
            {"pack_id": "a4a7d62a-b5ec-4f83-bc25-0f808ff74411", "version": [1, 7, 0]},
        ]
        gc.save_json_file(self.bp_file, initial_bps)
        gc.save_json_file(self.rp_file, initial_rps)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_status_detection(self):
        """Valida que o detector identifica corretamente o CobbleDrock ativo e outros add-ons."""
        bps = gc.load_json_file(self.bp_file)
        rps = gc.load_json_file(self.rp_file)

        active_bp_ids = {entry.get("pack_id") for entry in bps}
        self.assertIn("301ce48a-eef2-51b7-926d-b8a68eabcfea", active_bp_ids)
        self.assertIn("56a52fe3-c4d8-588d-9cce-6c6e6c381013", active_bp_ids)
        self.assertIn("5ad3bb44-8328-448e-8959-e7e0c64be76e", active_bp_ids)

    def test_disable_cobbledrock(self):
        """Valida a remocao cirurgica dos UUIDs do CobbleDrock mantendo outros add-ons."""
        bps = gc.load_json_file(self.bp_file)
        rps = gc.load_json_file(self.rp_file)

        filtered_bps = [b for b in bps if b.get("pack_id") not in gc.COBBLEDROCK_BP_IDS]
        filtered_rps = [r for r in rps if r.get("pack_id") not in gc.COBBLEDROCK_RP_IDS]

        gc.save_json_file(self.bp_file, filtered_bps)
        gc.save_json_file(self.rp_file, filtered_rps)

        result_bps = gc.load_json_file(self.bp_file)
        result_rps = gc.load_json_file(self.rp_file)

        self.assertEqual(len(result_bps), 1)
        self.assertEqual(result_bps[0]["pack_id"], "5ad3bb44-8328-448e-8959-e7e0c64be76e")

        self.assertEqual(len(result_rps), 1)
        self.assertEqual(result_rps[0]["pack_id"], "a4a7d62a-b5ec-4f83-bc25-0f808ff74411")

    def test_enable_cobbledrock(self):
        """Valida a reinsercao correta dos pacotes do CobbleDrock."""
        # Limpar primeiro
        gc.save_json_file(self.bp_file, [{"pack_id": "outromod", "version": [1, 0, 0]}])
        gc.save_json_file(self.rp_file, [{"pack_id": "outromod_rp", "version": [1, 0, 0]}])

        bps = gc.load_json_file(self.bp_file)
        rps = gc.load_json_file(self.rp_file)
        existing_bp_ids = {b.get("pack_id") for b in bps}
        existing_rp_ids = {r.get("pack_id") for r in rps}

        for pack in gc.COBBLEDROCK_PACKS["bp"]:
            if pack["pack_id"] not in existing_bp_ids:
                bps.insert(0, {"pack_id": pack["pack_id"], "version": pack["default_version"]})

        for pack in gc.COBBLEDROCK_PACKS["rp"]:
            if pack["pack_id"] not in existing_rp_ids:
                rps.insert(0, {"pack_id": pack["pack_id"], "version": pack["default_version"]})

        gc.save_json_file(self.bp_file, bps)
        gc.save_json_file(self.rp_file, rps)

        res_bps = gc.load_json_file(self.bp_file)
        res_rps = gc.load_json_file(self.rp_file)

        self.assertEqual(len(res_bps), 3)
        self.assertEqual(len(res_rps), 3)


if __name__ == "__main__":
    unittest.main()
