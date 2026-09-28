#!/usr/bin/env python3
# ==============================================================================
# Script: test_config_generator.py
# Responsabilidade: Testes unitarios automatizados para geracao e validacao
# das propriedades de configuracao do BDS a partir de templates.
# ==============================================================================

import os
import re
import subprocess
import tempfile
import unittest

class TestConfigGenerator(unittest.TestCase):
    def setUp(self):
        self.repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.template_path = os.path.join(self.repo_root, "templates", "server.properties.template")
        self.script_path = os.path.join(self.repo_root, "scripts", "bds-config.sh")

    def test_template_syntax_and_variables(self):
        """Verifica se todas as variaveis no template server.properties seguem o padrao oficial ${BDS_...}."""
        self.assertTrue(os.path.exists(self.template_path), "Template server.properties.template nao encontrado")
        with open(self.template_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Encontra todas as variaveis ${VAR} ou ${VAR:-DEFAULT}
        vars_found = re.findall(r"\$\{([A-Z0-9_]+)(:-([^}]*))?\}", content)
        self.assertGreater(len(vars_found), 5, "Poucas variaveis de template detectadas")
        for var_name, _, _ in vars_found:
            self.assertTrue(var_name.startswith("BDS_"), f"Variavel nao segue o prefixo BDS_: {var_name}")

    def test_python_template_substitution(self):
        """Simula a substituicao de variaveis no template e garante ausencia de marcadores orfaos."""
        env_vars = {
            "BDS_SERVER_NAME": "Meu Servidor Proxmox",
            "BDS_MAX_PLAYERS": "15",
            "BDS_GAMEMODE": "creative",
            "BDS_DIFFICULTY": "hard",
            "BDS_VIEW_DISTANCE": "24",
            "BDS_TICK_DISTANCE": "6",
        }

        with open(self.template_path, "r", encoding="utf-8") as f:
            template_content = f.read()

        def replacer(match):
            name = match.group(1)
            default = match.group(3) if match.group(3) is not None else ""
            return env_vars.get(name, default)

        rendered = re.sub(r"\$\{([A-Z0-9_]+)(:-([^}]*))?\}", replacer, template_content)

        # Verificar se as variaveis foram injetadas
        self.assertIn("server-name=Meu Servidor Proxmox", rendered)
        self.assertIn("max-players=15", rendered)
        self.assertIn("gamemode=creative", rendered)
        self.assertIn("difficulty=hard", rendered)
        self.assertIn("view-distance=24", rendered)
        self.assertIn("tick-distance=6", rendered)

        # Garantir que nao sobraram tags ${BDS_...}
        remaining = re.findall(r"\$\{BDS_[A-Z0-9_]+(:?-[^}]*)?\}", rendered)
        self.assertEqual(len(remaining), 0, f"Variaveis de template nao substituidas: {remaining}")

    def test_json_templates_validity(self):
        """Valida se todos os templates JSON sao documentos sintaticamente validos."""
        import json
        templates = ["allowlist.json.template", "permissions.json.template", "packetlimitconfig.json.template"]
        for tmpl in templates:
            tmpl_path = os.path.join(self.repo_root, "templates", tmpl)
            self.assertTrue(os.path.exists(tmpl_path), f"Arquivo ausente: {tmpl}")
            with open(tmpl_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.assertIsNotNone(data, f"JSON invalido em {tmpl}")

if __name__ == "__main__":
    unittest.main()
