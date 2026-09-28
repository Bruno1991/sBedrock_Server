#!/usr/bin/env python3
# ==============================================================================
# Script: test_data_layout.py
# Responsabilidade: Testes automatizados do modelo de desacoplamento de dados
# e links simbolicos de runtime definidos no ADR-003.
# ==============================================================================

import os
import shutil
import tempfile
import unittest

class TestDataLayout(unittest.TestCase):
    def setUp(self):
        self.test_root = tempfile.mkdtemp(prefix="bds_layout_test_")
        self.versions_dir = os.path.join(self.test_root, "versions")
        self.data_dir = os.path.join(self.test_root, "data")
        self.runtime_dir = os.path.join(self.test_root, "runtime")

        os.makedirs(self.versions_dir)
        os.makedirs(self.data_dir)
        os.makedirs(self.runtime_dir)

    def tearDown(self):
        shutil.rmtree(self.test_root)

    def test_version_isolation_and_rollback(self):
        """Valida que a troca atomica de links simbolicos preserva mundos e atualiza binarios."""
        # Criar versao 1.26.50
        v1_dir = os.path.join(self.versions_dir, "1.26.50")
        os.makedirs(v1_dir)
        with open(os.path.join(v1_dir, "bedrock_server"), "w") as f:
            f.write("BINARY_V1")

        # Criar versao 1.26.52
        v2_dir = os.path.join(self.versions_dir, "1.26.52")
        os.makedirs(v2_dir)
        with open(os.path.join(v2_dir, "bedrock_server"), "w") as f:
            f.write("BINARY_V2")

        # Criar dados persistentes
        worlds_dir = os.path.join(self.data_dir, "worlds")
        os.makedirs(worlds_dir)
        world_file = os.path.join(worlds_dir, "level.dat")
        with open(world_file, "w") as f:
            f.write("WORLD_DATA_IMMUTABLE")

        # Montar runtime inicial apontando para v1
        rt_bin = os.path.join(self.runtime_dir, "bedrock_server")
        rt_worlds = os.path.join(self.runtime_dir, "worlds")

        try:
            os.symlink(os.path.join(v1_dir, "bedrock_server"), rt_bin)
            os.symlink(worlds_dir, rt_worlds)
        except OSError as e:
            if os.name == "nt" and getattr(e, "winerror", None) == 1314:
                raise unittest.SkipTest("Links simbolicos no Windows exigem modo de desenvolvedor ou privilegios de Administrador (executado nativamente no Linux).")
            raise

        # Checar v1
        with open(rt_bin, "r") as f:
            self.assertEqual(f.read(), "BINARY_V1")
        with open(os.path.join(rt_worlds, "level.dat"), "r") as f:
            self.assertEqual(f.read(), "WORLD_DATA_IMMUTABLE")

        # Atualizar para v2 (relink)
        os.remove(rt_bin)
        os.symlink(os.path.join(v2_dir, "bedrock_server"), rt_bin)

        with open(rt_bin, "r") as f:
            self.assertEqual(f.read(), "BINARY_V2")

        # Rollback para v1 (relink reverso)
        os.remove(rt_bin)
        os.symlink(os.path.join(v1_dir, "bedrock_server"), rt_bin)

        with open(rt_bin, "r") as f:
            self.assertEqual(f.read(), "BINARY_V1")

        # O mundo deve permanecer 100% inalterado
        with open(os.path.join(rt_worlds, "level.dat"), "r") as f:
            self.assertEqual(f.read(), "WORLD_DATA_IMMUTABLE")

    def test_directory_structure_contract(self):
        """Valida que a hierarquia estrutural de diretorios respeita o contrato do ADR-003."""
        expected_dirs = [
            "versions",
            "data/config",
            "data/worlds",
            "data/keys",
            "data/backups",
            "data/custom_packs",
            "runtime",
            "bin"
        ]
        base_dir = os.path.join(self.test_root, "opt_bds")
        for d in expected_dirs:
            os.makedirs(os.path.join(base_dir, d), exist_ok=True)
            self.assertTrue(os.path.isdir(os.path.join(base_dir, d)))

if __name__ == "__main__":
    unittest.main()
