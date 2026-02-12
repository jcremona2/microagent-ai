#!/usr/bin/env python3
"""Run tests for microagent-ai."""

import unittest
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

# Import test modules
try:
    from tests import test_tools, test_groq_integration
except ImportError as e:
    print(f"Error importing test modules: {e}")
    sys.exit(1)

# Create a test suite
loader = unittest.TestLoader()
suite = unittest.TestSuite()

# Add test cases to the suite
try:
    suite.addTests(loader.loadTestsFromModule(test_tools))
    suite.addTests(loader.loadTestsFromModule(test_groq_integration))
except Exception as e:
    print(f"Error loading test cases: {e}")
    sys.exit(1)

# Run the test suite
print("Running tests...")
runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)

# Exit with non-zero code if any tests failed
sys.exit(not result.wasSuccessful())
