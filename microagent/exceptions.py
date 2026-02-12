"""Custom exceptions for the microagent framework."""

class AgentError(Exception):
    """Base exception for all agent-related errors."""
    pass

class ToolExecutionError(AgentError):
    """Raised when a tool fails during execution."""
    pass

class InvalidToolArguments(AgentError):
    """Raised when invalid arguments are passed to a tool."""
    pass

class MaxStepsExceeded(AgentError):
    """Raised when the agent exceeds the maximum number of steps."""
    pass

class LLMError(AgentError):
    """Raised when there's an error with the LLM provider."""
    pass
