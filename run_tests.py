#!/usr/bin/env python3

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

try:
    from tests import test_tools, test_groq_integration
except ImportError as e:
    print(f"Error importing test modules: {e}")
    sys.exit(1)

loader = unittest.TestLoader()
suite = unittest.TestSuite()

try:
    suite.addTests(loader.loadTestsFromModule(test_tools))
    suite.addTests(loader.loadTestsFromModule(test_groq_integration))
except Exception as e:
    print(f"Error loading test cases: {e}")
    sys.exit(1)

print("Running tests...")
runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)

sys.exit(not result.wasSuccessful())
