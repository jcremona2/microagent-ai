"""
Test configuration and fixtures for microagent-ai tests.
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest
from dotenv import load_dotenv

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables from .env.test if it exists
dotenv_path = project_root / ".env.test"
if dotenv_path.exists():
    load_dotenv(dotenv_path=dotenv_path, override=True)


class TestConfig:
    """Configuration for microagent-ai tests"""

    # API Configuration
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "test_api_key")
    GROQ_BASE_URL: str = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
    TEST_MODEL: str = os.getenv("TEST_MODEL", "mixtral-8x7b-32768")

    # Test Behavior
    SKIP_SLOW_TESTS: bool = os.getenv("SKIP_SLOW_TESTS", "true").lower() == "true"
    ENABLE_NETWORK_TESTS: bool = (
        os.getenv("ENABLE_NETWORK_TESTS", "false").lower() == "true"
    )
    ENABLE_STREAM_TESTS: bool = (
        os.getenv("ENABLE_STREAM_TESTS", "false").lower() == "true"
    )
    TEST_TEMPERATURE: float = float(os.getenv("TEST_TEMPERATURE", "0.7"))
    TEST_TIMEOUT: int = int(os.getenv("TEST_TIMEOUT", "30"))
    TEST_MODELS: List[str] = os.getenv(
        "TEST_MODELS", "mixtral-8x7b-32768,llama2-70b-4096"
    ).split(",")

    @classmethod
    def get_groq_config(cls) -> Dict[str, Any]:
        """Get configuration for Groq client"""
        return {
            "api_key": cls.GROQ_API_KEY,
            "base_url": cls.GROQ_BASE_URL,
            "model": cls.TEST_MODEL,
        }

    @classmethod
    def get_client_kwargs(cls) -> Dict[str, Any]:
        """Get keyword arguments for initializing the Groq client"""
        return {
            "api_key": cls.GROQ_API_KEY,
            "base_url": cls.GROQ_BASE_URL,
            "timeout": cls.TEST_TIMEOUT,
        }


# Pytest fixtures
@pytest.fixture(scope="session")
def test_config() -> TestConfig:
    """Provide test configuration to test functions"""
    return TestConfig


@pytest.fixture(scope="session")
def working_model(test_config) -> str:
    """Fixture that returns the first working model"""
    from groq import APIStatusError, Groq

    client = Groq(**test_config.get_client_kwargs())

    for model in test_config.TEST_MODELS:
        try:
            # Test with a minimal request
            client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=1,
            )
            return model
        except Exception as e:
            if "model not found" in str(e).lower():
                continue
            raise

    pytest.skip("No working model found in the test configuration")


# Custom markers
def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line("markers", "slow: mark test as slow to run")
    config.addinivalue_line(
        "markers", "streaming: mark test as requiring streaming support"
    )


# Skip slow tests if configured
def pytest_collection_modifyitems(config, items):
    """Skip slow tests if SKIP_SLOW_TESTS is True"""
    if TestConfig.SKIP_SLOW_TESTS:
        skip_slow = pytest.mark.skip(reason="Skipping slow test")
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_slow)

    # Skip streaming tests if disabled
    if not TestConfig.ENABLE_STREAM_TESTS:
        skip_stream = pytest.mark.skip(reason="Streaming tests disabled")
        for item in items:
            if "streaming" in item.keywords:
                item.add_marker(skip_stream)
