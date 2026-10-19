"""
Testes unitarios para o gerenciador de operadores windows/dar_op.py.
"""

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
WINDOWS_DIR = REPO_ROOT / "windows"
if str(WINDOWS_DIR) not in sys.path:
    sys.path.insert(0, str(WINDOWS_DIR))

import dar_op


class TestOpManager(unittest.TestCase):
    def test_paths_integrity(self):
        """Valida que dar_op aponta para os arquivos corretos de configuracao e runtime."""
        self.assertEqual(dar_op.PERMISSIONS_RUNTIME, REPO_ROOT / "server" / "runtime" / "permissions.json")
        self.assertEqual(dar_op.PERMISSIONS_DATA, REPO_ROOT / "server" / "data" / "config" / "permissions.json")
        self.assertEqual(dar_op.FRIENDS_FILE, WINDOWS_DIR / "amigos_operadores.txt")

    def test_load_permissions(self):
        """Garante que a lista de permissoes do permissions.json e carregada como lista de dicts."""
        perms = dar_op.load_permissions()
        self.assertIsInstance(perms, list)
        if perms:
            self.assertIn("permission", perms[0])
            self.assertIn("xuid", perms[0])

    def test_load_friends_list(self):
        """Valida leitura da lista de amigos configurados."""
        friends = dar_op.load_friends_list()
        self.assertIsInstance(friends, list)
        self.assertTrue(len(friends) > 0)
        self.assertIn("x12ultimatepass", [f.lower() for f in friends])

    def test_known_players_extraction(self):
        """Garante que a extracao de jogadores/xuids do log funciona sem excecoes."""
        known = dar_op.load_known_players_from_logs()
        self.assertIsInstance(known, dict)
        if known:
            for gt, xuid in known.items():
                self.assertTrue(xuid.isdigit())


if __name__ == "__main__":
    unittest.main()
