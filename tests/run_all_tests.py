#!/usr/bin/env python3
# ==============================================================================
# Script: run_all_tests.py
# Responsabilidade: Executor centralizado de toda a suite de testes unitarios
# e validacoes automatizadas do projeto s_Bedrock_Server.
# ==============================================================================

import os
import sys
import unittest

def main():
    test_dir = os.path.dirname(os.path.abspath(__file__))
    suite = unittest.defaultTestLoader.discover(test_dir, pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)

if __name__ == "__main__":
    main()
