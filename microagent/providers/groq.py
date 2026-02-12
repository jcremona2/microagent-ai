from typing import Dict, List, Optional, Union, AsyncGenerator, Any
import os
from groq import Groq
from groq.types.chat import ChatCompletion, ChatCompletionChunk

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
        
        # Configure the client
        client_kwargs = {"api_key": self.api_key}
        if base_url:
            client_kwargs["base_url"] = base_url
            
        self.client = Groq(**client_kwargs)
    
    async def chat_complete(
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
        return await self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
    
    async def stream_chat_complete(
        self,
        messages: List[Dict[str, str]],
        model: str = "llama-3.3-70b-versatile",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> AsyncGenerator[ChatCompletionChunk, None]:
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
