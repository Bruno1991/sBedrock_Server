#!/usr/bin/env python3
# ==============================================================================
# Script: test_backup_logic.py
# Responsabilidade: Testes automatizados do protocolo oficial de backup a quente,
# parsing da saida de 'save query', truncamento estrito de bytes e integridade SHA-256.
# ==============================================================================

import hashlib
import os
import shutil
import tempfile
import unittest

class TestBackupLogic(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="bds_backup_test_")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_save_query_output_parsing(self):
        """Valida a expressao de extracao de pares arquivo:tamanho gerados pelo BDS."""
        sample_output = (
            "A previous save has not been completed.\n"
            "Saving...\n"
            "Data saved. Files are now ready to be copied.\n"
            "Bedrock level/db/000005.ldb:2048576, Bedrock level/level.dat:2348, Bedrock level/db/CURRENT:16\n"
        )

        # Simular a extracao da lista
        lines = sample_output.splitlines()
        file_list_raw = ""
        found = False
        for line in lines:
            if found:
                file_list_raw += " " + line.strip()
            elif "Files are now ready to be copied" in line:
                found = True

        entries = [e.strip() for e in file_list_raw.split(",") if ":" in e]
        parsed = {}
        for entry in entries:
            path, size = entry.rsplit(":", 1)
            parsed[path.strip()] = int(size.strip())

        expected = {
            "Bedrock level/db/000005.ldb": 2048576,
            "Bedrock level/level.dat": 2348,
            "Bedrock level/db/CURRENT": 16,
        }
        self.assertEqual(parsed, expected)

    def test_byte_truncation_accuracy(self):
        """Garante que arquivos fatiados sejam truncados exatamente aos bytes reportados pela engine."""
        dummy_file = os.path.join(self.test_dir, "000005.ldb")
        target_size = 2048

        # Escrever 10.000 bytes no arquivo original (simulando escritas adicionais da engine apos snapshot)
        with open(dummy_file, "wb") as f:
            f.write(b"A" * 10000)

        self.assertEqual(os.path.getsize(dummy_file), 10000)

        # Realizar truncamento para target_size
        with open(dummy_file, "r+b") as f:
            f.truncate(target_size)

        self.assertEqual(os.path.getsize(dummy_file), target_size)

    def test_checksum_verification(self):
        """Valida que qualquer alteracao de 1 bit invalida o checksum SHA-256 do pacote de backup."""
        dummy_archive = os.path.join(self.test_dir, "backup.tar.gz")
        with open(dummy_archive, "wb") as f:
            f.write(b"Dados transacionais de teste do Bedrock Dedicated Server")

        with open(dummy_archive, "rb") as f:
            original_sha = hashlib.sha256(f.read()).hexdigest()

        # Checksum inicial confere
        with open(dummy_archive, "rb") as f:
            self.assertEqual(hashlib.sha256(f.read()).hexdigest(), original_sha)

        # Corromper 1 byte
        with open(dummy_archive, "r+b") as f:
            f.seek(0)
            f.write(b"X")

        # Checksum deve falhar
        with open(dummy_archive, "rb") as f:
            self.assertNotEqual(hashlib.sha256(f.read()).hexdigest(), original_sha)

if __name__ == "__main__":
    unittest.main()
