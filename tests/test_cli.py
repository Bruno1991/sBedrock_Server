"""
Testes unitarios para a interface CLI unificada (windows/cli.py).
"""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
WINDOWS_DIR = REPO_ROOT / "windows"
CLI_PY = WINDOWS_DIR / "cli.py"


class TestUnifiedCLI(unittest.TestCase):
    def test_cli_help(self):
        """Valida que cli.py --help executa com sucesso e lista opcoes essenciais."""
        result = subprocess.run([sys.executable, str(CLI_PY), "--help"], capture_output=True, text=True, cwd=str(WINDOWS_DIR))
        self.assertEqual(result.returncode, 0)
        self.assertIn("--start", result.stdout)
        self.assertIn("--mods", result.stdout)
        self.assertIn("--worlds", result.stdout)
        self.assertIn("--cobbled-farms", result.stdout)
        self.assertIn("--list-worlds", result.stdout)

    def test_cli_status(self):
        """Valida execucao de cli.py --status exibindo BDS e mundo ativo."""
        result = subprocess.run([sys.executable, str(CLI_PY), "--status"], capture_output=True, text=True, cwd=str(WINDOWS_DIR))
        self.assertEqual(result.returncode, 0)
        self.assertIn("Status do Servidor BDS", result.stdout)
        self.assertIn("Mundo Ativo no BDS", result.stdout)

    def test_cli_list_worlds(self):
        """Valida execucao de cli.py --list-worlds listando mundos instalados."""
        result = subprocess.run([sys.executable, str(CLI_PY), "--list-worlds"], capture_output=True, text=True, cwd=str(WINDOWS_DIR))
        self.assertEqual(result.returncode, 0)
        self.assertIn("Mundos instalados no BDS:", result.stdout)
        self.assertIn("Cobbled Farms", result.stdout)
        self.assertIn("Bedrock level", result.stdout)

    def test_cli_cobbled_farms_shortcut(self):
        """Valida que o atalho --cobbled-farms ativa o mundo e integra o CobbleDrock."""
        result = subprocess.run([sys.executable, str(CLI_PY), "--cobbled-farms"], capture_output=True, text=True, cwd=str(WINDOWS_DIR))
        self.assertEqual(result.returncode, 0)
        self.assertIn("Cobbled Farms ativado", result.stdout)


if __name__ == "__main__":
    unittest.main()
