"""
Test script for multiple LLM providers
"""

import os
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional, Type

from dotenv import load_dotenv
from openai import OpenAI


class ProviderType(str, Enum):
    OPENAI = "openai"
    OPENROUTER = "openrouter"
    GROQ = "groq"
    CLOUDFLARE = "cloudflare"
    HUGGINGFACE = "huggingface"
    GOOGLE = "google"
    LOCAL = "local"


@dataclass
class ProviderConfig:
    base_url: str
    api_key_env: str
    default_model: str
    headers: Optional[Dict[str, str]] = None


# Provider configurations
PROVIDERS: Dict[ProviderType, ProviderConfig] = {
    ProviderType.OPENAI: ProviderConfig(
        base_url="https://api.openai.com/v1",
        api_key_env="OPENAI_API_KEY",
        default_model="gpt-3.5-turbo",
    ),
    ProviderType.OPENROUTER: ProviderConfig(
        base_url="https://openrouter.ai/api/v1",
        api_key_env="OPENROUTER_API_KEY",
        default_model="meta-llama/llama-3.1-8b:free",
        headers={"HTTP-Referer": "https://github.com/yourusername/microagent"},
    ),
    ProviderType.GROQ: ProviderConfig(
        base_url="https://api.groq.com/openai/v1",
        api_key_env="GROQ_API_KEY",
        default_model="llama3-8b-8192",
    ),
    ProviderType.CLOUDFLARE: ProviderConfig(
        base_url="https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run",
        api_key_env="CLOUDFLARE_API_KEY",
        default_model="@cf/meta/llama-3.1-8b-instruct",
    ),
    ProviderType.LOCAL: ProviderConfig(
        base_url="http://localhost:8080/v1",
        api_key_env="LOCAL_AI_KEY",
        default_model="local-model",
    ),
}


class LLMClient:
    """Unified client for different LLM providers"""

    def __init__(self, provider: ProviderType, model: Optional[str] = None):
        self.provider = provider
        self.config = PROVIDERS[provider]
        self.api_key = os.getenv(self.config.api_key_env)

        if not self.api_key and provider != ProviderType.LOCAL:
            raise ValueError(
                f"API key not found in environment variable: {self.config.api_key_env}"
            )

        self.model = model or self.config.default_model
        self.client = self._create_client()

    def _create_client(self):
        """Create a client for the specified provider"""
        client_kwargs = {"api_key": self.api_key, "base_url": self._process_base_url()}

        # Add provider-specific headers if they exist
        if self.config.headers:
            client_kwargs["default_headers"] = self.config.headers

        return OpenAI(**client_kwargs)

    def _process_base_url(self) -> str:
        """Process base URL with any required substitutions"""
        if self.provider == ProviderType.CLOUDFLARE:
            account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID")
            if not account_id:
                raise ValueError(
                    "CLOUDFLARE_ACCOUNT_ID environment variable is required"
                )
            return self.config.base_url.format(account_id=account_id)
        return self.config.base_url

    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from the LLM"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                **kwargs,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating text: {str(e)}"


def test_provider(provider: ProviderType, prompt: str = "Hello, how are you?") -> str:
    """Test a specific provider"""
    try:
        print(f"\n🔍 Testing {provider.value.upper()}...")
        client = LLMClient(provider)
        response = client.client.chat.completions.create(
            model=client.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50,
        )

        result = response.choices[0].message.content
        print(f"✅ {provider.value.upper()} Success!")
        print(f"Model: {client.model}")
        print(
            f"Response: {result[:200]}..."
            if len(result) > 200
            else f"Response: {result}"
        )
        return result

    except Exception as e:
        error_msg = f"❌ {provider.value.upper()} Error: {str(e)}"
        print(error_msg)
        return error_msg


def main():
    """Main function to test all configured providers"""
    load_dotenv()

    print("🤖 LLM Provider Test Script")
    print("=" * 50)

    # Test prompt
    test_prompt = "Tell me a short joke about artificial intelligence in one sentence."

    # Test each provider
    for provider in ProviderType:
        if provider in PROVIDERS:
            test_provider(provider, test_prompt)

    print("\n✅ Testing complete!")
    print("\n💡 To use a specific provider in your code:")
    print("""
from examples.test_multiple_providers import LLMClient, ProviderType
import asyncio

async def main():
    # Example: Using OpenRouter
    client = LLMClient(ProviderType.OPENROUTER, model="meta-llama/llama-3.1-8b:free")
    response = await client.generate("Your prompt here")
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
    """)


if __name__ == "__main__":
    main()
