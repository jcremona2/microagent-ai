from typing import Dict, List, Optional, Union, AsyncGenerator
import os
from groq import Groq as GroqClient, AsyncGroq
from groq.types.chat.chat_completion import ChatCompletion

class GroqProvider:
    """Provider for Groq API."""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """Initialize the Groq provider.
        
        Args:
            api_key: Groq API key. If not provided, will try to get from GROQ_API_KEY environment variable.
            base_url: Base URL for the Groq API. Defaults to the official Groq API endpoint.
        """
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        if not self.api_key:
            raise ValueError(
                "Groq API key not provided. Either pass it as an argument or set the GROQ_API_KEY environment variable."
            )
        
        # Remove the /openai/v1 suffix as it's already included in the client
        self.base_url = base_url or "https://api.groq.com"
        self.client = GroqClient(api_key=self.api_key, base_url=self.base_url)
        self.async_client = AsyncGroq(api_key=self.api_key, base_url=self.base_url)
    
    def chat_complete(
        self,
        messages: List[Dict[str, str]],
        model: str = "llama-3.3-70b-versatile",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> ChatCompletion:
        """Generate a chat completion using Groq's API.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'.
            model: The model to use for completion.
            temperature: Controls randomness (0-2).
            max_tokens: Maximum number of tokens to generate.
            **kwargs: Additional arguments to pass to the Groq API.
            
        Returns:
            ChatCompletion object containing the generated response.
        """
        return self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
    
    async def achat_complete(
        self,
        messages: List[Dict[str, str]],
        model: str = "llama-3.3-70b-versatile",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> ChatCompletion:
        """Asynchronously generate a chat completion using Groq's API.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'.
            model: The model to use for completion.
            temperature: Controls randomness (0-2).
            max_tokens: Maximum number of tokens to generate.
            **kwargs: Additional arguments to pass to the Groq API.
            
        Returns:
            ChatCompletion object containing the generated response.
        """
        return await self.async_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
    
    def stream_chat_complete(
        self,
        messages: List[Dict[str, str]],
        model: str = "llama-3.3-70b-versatile",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> AsyncGenerator[ChatCompletion, None]:
        """Stream chat completions from the Groq API.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'.
            model: The model to use for completion.
            temperature: Controls randomness (0-2).
            max_tokens: Maximum number of tokens to generate.
            **kwargs: Additional arguments to pass to the Groq API.
            
        Yields:
            Chunks of the ChatCompletion response as they're generated.
        """
        stream = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            **kwargs
        )
        
        for chunk in stream:
            yield chunk
