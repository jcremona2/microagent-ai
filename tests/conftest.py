"""
Test configuration and fixtures for Groq integration tests.
"""
import os
import pytest
from dotenv import load_dotenv
from typing import Dict, Any, Optional

# Load environment variables from .env file
load_dotenv()

class TestConfig:
    """Configuration for Groq API tests"""
    
    # API Configuration
    API_KEY: str = os.getenv("GROQ_API_KEY", "")
    BASE_URL: str = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
    
    # Test Models - will be tried in order until one works
    TEST_MODELS: list = [
        os.getenv("GROQ_TEST_MODEL", "openai/gpt-oss-120b"),
        "llama3-70b-8192",
        "mixtral-8x7b-32768"
    ]
    
    # Test Parameters
    TEST_TEMPERATURE: float = float(os.getenv("GROQ_TEST_TEMPERATURE", "0.7"))
    TEST_MAX_TOKENS: int = int(os.getenv("GROQ_TEST_MAX_TOKENS", "100"))
    TEST_TIMEOUT: int = int(os.getenv("GROQ_TEST_TIMEOUT", "30"))
    
    # Test Behavior
    SKIP_SLOW_TESTS: bool = os.getenv("SKIP_SLOW_TESTS", "true").lower() == "true"
    ENABLE_STREAM_TESTS: bool = os.getenv("ENABLE_STREAM_TESTS", "true").lower() == "true"
    
    @classmethod
    def get_client_kwargs(cls) -> Dict[str, Any]:
        """Get kwargs for initializing the Groq client"""
        return {
            "api_key": cls.API_KEY,
            "base_url": cls.BASE_URL,
            "timeout": cls.TEST_TIMEOUT
        }

# Pytest fixtures
@pytest.fixture(scope="session")
def test_config() -> TestConfig:
    """Provide test configuration to test functions"""
    return TestConfig

@pytest.fixture(scope="session")
def working_model(test_config) -> str:
    """Fixture that returns the first working model"""
    from groq import Groq, APIStatusError
    
    client = Groq(**test_config.get_client_kwargs())
    
    for model in test_config.TEST_MODELS:
        try:
            # Test with a minimal request
            client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=1
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
    config.addinivalue_line(
        "markers",
        "slow: mark test as slow to run"
    )
    config.addinivalue_line(
        "markers",
        "streaming: mark test as requiring streaming support"
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
