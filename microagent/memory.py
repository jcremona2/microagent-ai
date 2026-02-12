"""Memory system for the microagent framework."""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from .llm import Message


class BaseMemory(ABC):
    """Abstract base class for memory implementations."""

    @abstractmethod
    def add(
        self,
        role: str,
        content: Optional[str],
        *,
        tool_calls: Optional[List[Dict[str, Any]]] = None,
        tool_call_id: Optional[str] = None,
    ) -> None:
        """Add a message to the memory.

        Args:
            role: The role of the message sender (e.g., 'user', 'assistant', 'tool')
            content: The content of the message, if any
            tool_calls: Optional list of tool calls (for assistant messages)
            tool_call_id: Optional ID of the tool call (for tool messages)
        """
        raise NotImplementedError

    @abstractmethod
    def get_messages(self, limit: Optional[int] = None) -> List[Message]:
        """Get messages from memory.

        Args:
            limit: Maximum number of messages to return. If None, return all messages.

        Returns:
            List of message dictionaries compatible with the LLM `Message` format.
        """
        raise NotImplementedError

    @abstractmethod
    def clear(self) -> None:
        """Clear all messages from memory."""
        raise NotImplementedError


class InMemoryMemory(BaseMemory):
    """In-memory implementation of the memory system."""

    def __init__(self, max_messages: Optional[int] = None):
        """Initialize the in-memory memory store.

        Args:
            max_messages: Maximum number of messages to store. If None, no limit.
        """
        self._messages: List[Message] = []
        self.max_messages = max_messages

    def add(
        self,
        role: str,
        content: Optional[str],
        *,
        tool_calls: Optional[List[Dict[str, Any]]] = None,
        tool_call_id: Optional[str] = None,
    ) -> None:
        """Add a message to memory."""
        message: Message = {
            "role": role,
            "content": content,
            "tool_calls": tool_calls,
            "tool_call_id": tool_call_id,
        }
        self._messages.append(message)

        # Enforce max messages limit if set
        if self.max_messages is not None:
            while len(self._messages) > self.max_messages:
                self._messages.pop(0)

    def get_messages(self, limit: Optional[int] = None) -> List[Message]:
        """Get messages from memory."""
        messages = self._messages if limit is None else self._messages[-limit:]

        # Return a shallow copy of each message so external mutation
        # cannot affect internal state.
        return [msg.copy() for msg in messages]

    def clear(self) -> None:
        """Clear all messages from memory."""
        self._messages.clear()
