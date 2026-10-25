"""
Testes unitarios para o modulo de gerencia inteligente (server_manager.py).
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
WINDOWS_DIR = REPO_ROOT / "windows"
if str(WINDOWS_DIR) not in sys.path:
    sys.path.insert(0, str(WINDOWS_DIR))

import server_manager as sm


class TestServerManager(unittest.TestCase):
    def test_get_server_status_structure(self):
        """Valida que get_server_status retorna todas as chaves essenciais de telemetria."""
        st = sm.get_server_status()
        self.assertIn("running", st)
        self.assertIn("pid", st)
        self.assertIn("memory_mb", st)
        self.assertIn("port_bound", st)
        self.assertIn("active_world", st)
        self.assertIn("total_worlds", st)
        self.assertIn("active_mods", st)
        self.assertIsInstance(st["total_worlds"], int)
        self.assertGreaterEqual(st["total_worlds"], 4)

    def test_list_worlds_detailed(self):
        """Valida detalhamento de mundos com tamanho, integridade e contagem de pacotes."""
        worlds = sm.list_worlds_detailed()
        names = [w["name"] for w in worlds]
        self.assertIn("Cobbled Farms", names)
        self.assertIn("Lucky OneBlock", names)
        self.assertIn("Bedrock level", names)

        for w in worlds:
            self.assertIn("size_mb", w)
            self.assertIn("is_active", w)
            self.assertIn("last_modified", w)
            self.assertIn("bp_count", w)
            self.assertIn("rp_count", w)

    def test_healthcheck_execution(self):
        """Valida execucao do healthcheck diagnosticando o ecossistema BDS."""
        hc = sm.run_healthcheck()
        self.assertIn("overall_ok", hc)
        self.assertIn("checks", hc)
        self.assertTrue(len(hc["checks"]) >= 7)

        check_names = [c["name"] for c in hc["checks"]]
        self.assertTrue(any("Binário" in n for n in check_names))
        self.assertTrue(any("server.properties" in n for n in check_names))
        self.assertTrue(any("permissions.json" in n for n in check_names))
        self.assertTrue(any("Porta de Rede" in n for n in check_names))

    def test_backup_and_list_backups(self):
        """Valida criacao de snapshot ZIP de mundo e listagem de backups."""
        ok, msg = sm.backup_world("Bedrock level")
        self.assertTrue(ok, f"Backup falhou: {msg}")

        backups = sm.list_world_backups()
        self.assertGreaterEqual(len(backups), 1)
        self.assertIn("Bedrock_level", backups[0]["name"])

    def test_curseforge_installer_routing(self):
        """Garante que URLs e slugs oficiais do CurseForge sao roteados corretamente."""
        # Teste do roteamento com URL do Lucky OneBlock
        url = "https://www.curseforge.com/minecraft/worlds/lucky-oneblock"
        ok, msg = sm.install_from_curseforge(url, activate=False)
        self.assertTrue(ok, f"Roteamento do Lucky OneBlock falhou: {msg}")

    def test_disable_all_mods(self):
        """Valida que disable_all_mods limpa todos os pacotes deixando o mundo vanilla."""
        ok, msg = sm.disable_all_mods("Lucky OneBlock")
        self.assertTrue(ok, f"disable_all_mods falhou: {msg}")
        self.assertIn("vanilla", msg)

        # Checa status
        st = sm.get_server_status()
        # Se Lucky OneBlock for o ativo, nao deve ter active_mods
        if st["active_world"] == "Lucky OneBlock":
            self.assertEqual(len(st["active_mods"]), 0)


if __name__ == "__main__":
    unittest.main()
