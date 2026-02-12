"""
Example: Using Multiple LLM Providers with an Agent
--------------------------------------------------
This example shows how to integrate different LLM providers with your agent.
"""
import os
import asyncio
from typing import List, Dict, Any, Optional, Callable, TypeVar
from dataclasses import dataclass
from enum import Enum
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# --- LLM Provider Setup (from test_multiple_providers.py) ---
class ProviderType(str, Enum):
    OPENAI = "openai"
    OPENROUTER = "openrouter"
    GROQ = "groq"
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
        default_model="gpt-3.5-turbo"
    ),
    ProviderType.OPENROUTER: ProviderConfig(
        base_url="https://openrouter.ai/api/v1",
        api_key_env="OPENROUTER_API_KEY",
        default_model="meta-llama/llama-3.1-8b:free",
        headers={"HTTP-Referer": "https://github.com/yourusername/microagent"}
    ),
    ProviderType.GROQ: ProviderConfig(
        base_url="https://api.groq.com/openai/v1",
        api_key_env="GROQ_API_KEY",
        default_model="llama3-8b-8192"
    ),
    ProviderType.LOCAL: ProviderConfig(
        base_url="http://localhost:8080/v1",
        api_key_env="LOCAL_AI_KEY",
        default_model="local-model"
    )
}

class LLMClient:
    """Unified client for different LLM providers"""
    
    def __init__(self, provider: ProviderType, model: Optional[str] = None):
        self.provider = provider
        self.config = PROVIDERS[provider]
        self.api_key = os.getenv(self.config.api_key_env)
        
        if not self.api_key and provider != ProviderType.LOCAL:
            raise ValueError(f"API key not found in environment variable: {self.config.api_key_env}")
        
        self.model = model or self.config.default_model
        self.client = self._create_client()
    
    def _create_client(self):
        """Create a client for the specified provider"""
        client_kwargs = {
            "api_key": self.api_key,
            "base_url": self.config.base_url
        }
        
        if self.config.headers:
            client_kwargs["default_headers"] = self.config.headers
        
        return OpenAI(**client_kwargs)
    
    async def generate(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate a response from the LLM"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating text: {str(e)}"

# --- Agent Implementation ---

class Agent:
    """A simple agent that can use tools and maintain conversation context"""
    
    def __init__(self, llm_client: LLMClient, tools: Optional[List[Callable]] = None):
        self.llm = llm_client
        self.tools = {tool.__name__: tool for tool in (tools or [])}
        self.memory = []
    
    async def run(self, user_input: str) -> str:
        """Process user input and return a response"""
        # Add user message to memory
        self.memory.append({"role": "user", "content": user_input})
        
        try:
            # Get response from LLM
            response = await self.llm.generate(
                messages=self.memory,
                max_tokens=500,
                temperature=0.7
            )
            
            # Add assistant's response to memory
            self.memory.append({"role": "assistant", "content": response})
            return response
            
        except Exception as e:
            return f"Error: {str(e)}"

# --- Example Tools ---

async def get_weather(location: str) -> str:
    """Get the current weather for a location"""
    # In a real implementation, this would call a weather API
    return f"The weather in {location} is sunny and 72°F."

async def calculate(expression: str) -> str:
    """Evaluate a mathematical expression"""
    try:
        result = eval(expression)  # Note: Using eval is not safe for production
        return f"The result of {expression} is {result}"
    except Exception as e:
        return f"Error calculating expression: {str(e)}"

# --- Example Usage ---

async def main():
    print("🤖 Agent with Multiple LLM Providers")
    print("=" * 50)
    
    # Initialize the LLM client with your preferred provider
    provider = ProviderType.OPENROUTER  # Change to your preferred provider
    llm_client = LLMClient(provider=provider)
    
    # Create an agent with tools
    agent = Agent(
        llm_client=llm_client,
        tools=[get_weather, calculate]
    )
    
    # Example conversation
    queries = [
        "What's the weather like in San Francisco?",
        "Now calculate 25 * 4 + 10"
    ]
    
    for query in queries:
        print(f"\nYou: {query}")
        response = await agent.run(query)
        print(f"Agent: {response}")
    
    print("\n🔍 Conversation History:")
    for msg in agent.memory:
        print(f"{msg['role'].capitalize()}: {msg['content']}")

if __name__ == "__main__":
    asyncio.run(main())
