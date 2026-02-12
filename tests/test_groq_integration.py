"""
Integration tests for Groq API client
"""
import time
import pytest
import asyncio
from unittest.mock import patch, MagicMock
from groq import Groq, APIConnectionError, APIStatusError

# Test configuration from conftest
TEST_PROMPT = "What is the capital of France?"

class TestGroqIntegration:
    """Test suite for Groq API integration"""
    
    @pytest.fixture(autouse=True)
    def setup(self, test_config, working_model):
        """Setup test fixtures"""
        self.config = test_config
        self.working_model = working_model
        self.client = Groq(**test_config.get_client_kwargs())
        
    def test_connection(self):
        """Test basic API connection"""
        assert self.client is not None
        
    @pytest.mark.slow
    def test_chat_completion_with_different_models(self):
        """Test chat completion with different models"""
        for model in self.config.TEST_MODELS:
            try:
                completion = self.client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": TEST_PROMPT}],
                    temperature=self.config.TEST_TEMPERATURE,
                    max_tokens=50
                )
                assert completion.choices[0].message.content is not None
                assert len(completion.choices[0].message.content) > 0
                
                # If we get here, the model works
                print(f"✅ Model {model} is working")
                return
                
            except Exception as e:
                if "model not found" in str(e).lower():
                    print(f"⚠️  Model {model} not available")
                    continue
                raise
        
        pytest.skip("No working model found in the test configuration")
    
    @pytest.mark.streaming
    def test_streaming_response(self):
        """Test streaming response"""
        completion = self.client.chat.completions.create(
            model=self.working_model,
            messages=[{"role": "user", "content": TEST_PROMPT}],
            temperature=self.config.TEST_TEMPERATURE,
            max_tokens=50,
            stream=True
        )
        
        content = ""
        for chunk in completion:
            content += chunk.choices[0].delta.content or ""
            
        assert len(content) > 0
        assert "Paris" in content
    
    @pytest.mark.slow
    def test_temperature_effect(self):
        """Test that temperature affects output randomness"""
        responses = set()
        
        for _ in range(3):
            completion = self.client.chat.completions.create(
                model=self.working_model,
                messages=[{"role": "user", "content": "Say a random number"}],
                temperature=0.9,  # High temperature for more randomness
                max_tokens=10
            )
            response = completion.choices[0].message.content.strip()
            responses.add(response)
            
            # Small delay to avoid rate limiting
            time.sleep(1)
            
        assert len(responses) > 1, "Temperature not affecting output diversity"
    
    @pytest.mark.parametrize("max_tokens", [5, 10, 20])
    def test_max_tokens(self, max_tokens):
        """Test max_tokens parameter"""
        completion = self.client.chat.completions.create(
            model=self.working_model,
            messages=[{"role": "user", "content": "Count from 1 to 10"}],
            max_tokens=max_tokens,
            temperature=0  # Deterministic output
        )
        
        content = completion.choices[0].message.content
        # Allow for some variance in tokenization
        assert len(content.split()) <= max_tokens + 3, \
            f"Response too long: {len(content.split())} > {max_tokens + 3} (max_tokens + 3)"
    
    @pytest.mark.asyncio
    async def test_async_completion(self):
        """Test async completion"""
        from groq import AsyncGroq
        
        async with AsyncGroq(**self.config.get_client_kwargs()) as async_client:
            completion = await async_client.chat.completions.create(
                model=self.working_model,
                messages=[{"role": "user", "content": TEST_PROMPT}],
                temperature=self.config.TEST_TEMPERATURE,
                max_tokens=50
            )
            
            assert completion.choices[0].message.content is not None
    
    def test_error_handling(self):
        """Test error handling for invalid requests"""
        with pytest.raises(APIStatusError) as excinfo:
            self.client.chat.completions.create(
                model="nonexistent-model-123",
                messages=[{"role": "user", "content": TEST_PROMPT}],
                max_tokens=5
            )
        
        assert excinfo.value.status_code == 400
        assert "model not found" in str(excinfo.value).lower()
        
    def test_custom_base_url(self):
        """Test that custom base URLs are used"""
        custom_url = "https://custom-api.groq.com/v1"
        with patch('groq._client.SyncGroq') as mock_client:
            Groq(api_key="test-key", base_url=custom_url)
            _, kwargs = mock_client.call_args
            assert kwargs["base_url"] == custom_url

class TestGroqClientConfiguration:
    """Test Groq client configuration"""
    
    def test_custom_timeout(self, test_config):
        """Test custom timeout configuration"""
        with patch('groq._client.SyncGroq') as mock_client:
            Groq(api_key="test-key", timeout=test_config.TEST_TIMEOUT)
            mock_client.assert_called_once()
            _, kwargs = mock_client.call_args
            assert kwargs["timeout"] == test_config.TEST_TIMEOUT
    
    def test_default_headers(self):
        """Test default headers include user agent"""
        with patch('groq._client.SyncGroq') as mock_client:
            Groq(api_key="test-key")
            _, kwargs = mock_client.call_args
            headers = kwargs["default_headers"]
            assert "User-Agent" in headers
            assert "groq-python" in headers["User-Agent"]
    
    def test_environment_variables_override(self, monkeypatch):
        """Test that environment variables override defaults"""
        monkeypatch.setenv("GROQ_BASE_URL", "https://custom-api.example.com")
        monkeypatch.setenv("GROQ_TEST_MODEL", "custom-model")
        
        # Reload the config to pick up the new env vars
        from tests.conftest import TestConfig
        reloaded_config = type('TestConfig', (), {})()
        
        assert reloaded_config.BASE_URL == "https://custom-api.example.com"
        assert reloaded_config.TEST_MODELS[0] == "custom-model"

# Example usage documentation
docstring = """
Groq API Client Usage Examples
=============================

1. Basic Usage:
```python
from groq import Groq

client = Groq(api_key="your-api-key")

response = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[{"role": "user", "content": "Hello!"}],
    temperature=0.7,
    max_tokens=100
)
print(response.choices[0].message.content)
```

2. Streaming Response:
```python
completion = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[{"role": "user", "content": "Tell me a story"}],
    stream=True
)

for chunk in completion:
    print(chunk.choices[0].delta.content or "", end="", flush=True)
```

3. Async Client:
```python
import asyncio
from groq import AsyncGroq

async def main():
    async with AsyncGroq(api_key="your-api-key") as client:
        response = await client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": "Hello!"}]
        )
        print(response.choices[0].message.content)

asyncio.run(main())
```

4. Error Handling:
```python
try:
    response = client.chat.completions.create(
        model="nonexistent-model",
        messages=[{"role": "user", "content": "Hello!"}]
    )
except Exception as e:
    print(f"Error: {e}")
```

Environment Variables:
- `GROQ_API_KEY`: Your Groq API key
- `GROQ_MODEL`: Default model to use
- `GROQ_TEMPERATURE`: Default temperature (0.0-1.0)
- `GROQ_MAX_TOKENS`: Default max tokens per request
"""
