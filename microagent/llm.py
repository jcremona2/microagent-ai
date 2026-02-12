"""LLM abstraction layer for the microagent framework."""

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional, TypedDict, Union

from .exceptions import LLMError


class ToolCall(TypedDict):
    """Represents a function/tool call from the LLM."""

    id: str
    type: Literal["function"]
    function: Dict[str, Any]  # name, arguments (JSON string)


class Message(TypedDict):
    """Message format for LLM communication."""

    role: Literal["system", "user", "assistant", "tool"]
    content: Optional[str]
    tool_calls: Optional[List[ToolCall]]
    tool_call_id: Optional[str]


class LLMResponse(TypedDict):
    """Structured response from the LLM."""

    content: Optional[str]
    tool_calls: List[ToolCall]
    raw_response: Any


class BaseLLM(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def complete(
        self, messages: List[Message], tools: Optional[List[Any]] = None, **kwargs: Any
    ) -> LLMResponse:
        """Generate a completion from the LLM.

        Args:
            messages: List of messages in the conversation
            tools: List of tools available to the LLM
            **kwargs: Additional model-specific parameters

        Returns:
            LLMResponse containing the generated content and tool calls
        """
        pass


class OpenAIModel(BaseLLM):
    """OpenAI-compatible LLM implementation."""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs,
    ):
        """Initialize the OpenAI model.

        Args:
            api_key: OpenAI API key
            model: Model name to use
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum number of tokens to generate
            **kwargs: Additional model parameters
        """
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError(
                "The 'openai' package is required for OpenAIModel. "
                "Install it with: pip install openai"
            )

        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.kwargs = kwargs

    def complete(
        self, messages: List[Message], tools: Optional[List[Any]] = None, **kwargs
    ) -> LLMResponse:
        """Generate a completion using the OpenAI API.

        Args:
            messages: List of messages in the conversation
            tools: List of tools available to the LLM
            **kwargs: Additional parameters to override defaults

        Returns:
            LLMResponse with content, tool_calls, and raw response
        """
        try:
            # Prepare tools for the API if provided
            tools_list = None
            if tools:
                tools_list = [
                    {
                        "type": "function",
                        "function": {
                            "name": tool.name,
                            "description": tool.description,
                            "parameters": tool.parameters,
                        },
                    }
                    for tool in tools
                ]

            # Merge default and provided kwargs
            params = {
                "model": self.model,
                "messages": messages,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                **self.kwargs,
                **kwargs,
            }

            if tools_list:
                params["tools"] = tools_list
                params["tool_choice"] = "auto"

            # Make the API call
            response = self.client.chat.completions.create(**params)

            # Extract the response
            choice = response.choices[0]
            message = choice.message

            # Handle tool calls if present
            tool_calls = []
            if hasattr(message, "tool_calls") and message.tool_calls:
                tool_calls = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in message.tool_calls
                ]

            return {
                "content": message.content,
                "tool_calls": tool_calls,
                "raw_response": response,
            }

        except Exception as e:
            raise LLMError(f"Error calling OpenAI API: {str(e)}") from e
