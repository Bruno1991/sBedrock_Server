"""
Testes unitarios para o utilitario windows/reset_test_map.py.
"""

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
WINDOWS_DIR = REPO_ROOT / "windows"
if str(WINDOWS_DIR) not in sys.path:
    sys.path.insert(0, str(WINDOWS_DIR))

import reset_test_map


class TestResetMapPaths(unittest.TestCase):
    def test_paths_match_adr003_layout(self):
        """Valida que reset_test_map aponta para server/runtime e server/data e nao windows/."""
        self.assertEqual(reset_test_map.BDS_EXE, REPO_ROOT / "server" / "runtime" / "bedrock_server.exe")
        self.assertEqual(reset_test_map.SERVER_PROPERTIES, REPO_ROOT / "server" / "runtime" / "server.properties")
        self.assertEqual(reset_test_map.WORLDS_DIR, REPO_ROOT / "server" / "data" / "worlds")
        self.assertEqual(reset_test_map.BACKUPS_DIR, REPO_ROOT / "server" / "data" / "backups")

    def test_read_level_name_from_runtime(self):
        """Valida que o level-name e extraido corretamente de server.properties."""
        level_name = reset_test_map.read_level_name()
        self.assertTrue(len(level_name) > 0)
        self.assertIn(level_name, ["Bedrock level", "Cobbled Farms", "Tryzz's Parkour Spiral"])

    def test_binary_existence_in_runtime(self):
        """Garante que bedrock_server.exe esta presente no caminho resolvido."""
        self.assertTrue(reset_test_map.BDS_EXE.exists(), f"Executavel nao encontrado em {reset_test_map.BDS_EXE}")


if __name__ == "__main__":
    unittest.main()
