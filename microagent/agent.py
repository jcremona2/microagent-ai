"""Core Agent implementation with strict mode, tracing, and improved error handling."""

import json
import logging
from typing import Any, Dict, List, Optional, Union, cast

from .exceptions import (
    AgentError,
    InvalidToolArguments,
    LLMError,
    MaxStepsExceeded,
    ToolExecutionError,
)
from .llm import BaseLLM, LLMResponse, Message
from .memory import BaseMemory, InMemoryMemory
from .tools import Tool
from .tracing import StepType, Tracer

logger = logging.getLogger(__name__)


class Agent:
    """Main Agent class with strict mode and execution tracing."""

    def __init__(
        self,
        llm: BaseLLM,
        tools: Optional[List[Union[Tool, Any]]] = None,
        memory: Optional[BaseMemory] = None,
        max_steps: int = 10,
        strict: bool = False,
        debug: bool = False,
        enable_tracing: bool = True,
    ):
        """Initialize the Agent with configuration.

        Args:
            llm: The LLM instance to use for generating responses
            tools: List of tools (functions decorated with @tool) or Tool instances
            memory: Memory implementation to use (defaults to InMemoryMemory)
            max_steps: Maximum number of steps before raising MaxStepsExceeded
            strict: If True, enables strict validation and fails fast on errors
            debug: If True, enables debug logging
            enable_tracing: If True, enables execution tracing
        """
        self.llm = llm
        self.max_steps = max_steps
        self.strict = strict
        self.debug = debug

        # Set up memory and tools
        self.memory = memory or InMemoryMemory()
        self.tools: Dict[str, Tool] = {}
        self._register_tools(tools or [])

        # Set up tracing
        self.tracer = Tracer(enabled=enable_tracing)

        # Set up logging
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Configure logging based on debug mode."""
        level = logging.DEBUG if self.debug else logging.INFO
        logging.basicConfig(
            level=level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    def _register_tools(self, tools: List[Union[Tool, Any]]) -> None:
        """Register tools with the agent."""
        for tool in tools:
            # If it's a function with a _tool attribute, use that
            if hasattr(tool, "_tool"):
                tool_instance = tool._tool
            # If it's already a Tool instance
            elif isinstance(tool, Tool):
                tool_instance = tool
            else:
                if self.strict:
                    raise ValueError(
                        f"Invalid tool type: {tool}. Must be a function decorated with @tool or a Tool instance."
                    )
                continue

            if tool_instance.name in self.tools:
                if self.strict:
                    raise ValueError(
                        f"Tool with name '{tool_instance.name}' already registered"
                    )
                logger.warning(
                    f"Tool with name '{tool_instance.name}' already registered, skipping"
                )
                continue

            # Enable strict mode on tools if agent is in strict mode
            if self.strict:
                tool_instance.strict = True

            self.tools[tool_instance.name] = tool_instance
            logger.debug(f"Registered tool: {tool_instance.name}")

    def _execute_tool(self, tool_call: Dict[str, Any]) -> str:
        """Execute a tool call with validation and tracing."""
        try:
            tool_name = tool_call["function"]["name"]

            if tool_name not in self.tools:
                error_msg = f"Tool '{tool_name}' not found"
                if self.strict:
                    raise ToolExecutionError(error_msg)
                return error_msg

            tool = self.tools[tool_name]
            arguments = json.loads(tool_call["function"]["arguments"])

            # Log the tool call
            self.tracer.log_tool_call(tool_name, arguments)

            try:
                # Execute the tool
                result = tool(**arguments)

                # Log successful result
                self.tracer.log_tool_result(tool_name, result)
                return str(result)

            except Exception as e:
                error = ToolExecutionError(
                    f"Error executing tool '{tool_name}': {str(e)}"
                )
                self.tracer.log_tool_result(tool_name, None, error)
                if self.strict:
                    raise error
                return str(error)

        except json.JSONDecodeError as e:
            error = InvalidToolArguments(f"Invalid JSON in tool arguments: {e}")
            self.tracer.log_tool_result("unknown", None, error)
            if self.strict:
                raise error
            return str(error)
        except Exception as e:
            error = ToolExecutionError(f"Tool execution failed: {str(e)}")
            self.tracer.log_tool_result(tool_name, None, error)
            if self.strict:
                raise error
            return str(error)

    def run(self, message: str, **kwargs) -> str:
        """Run the agent with the given message and return the final response.

        Args:
            message: The user's message
            **kwargs: Additional parameters to pass to the LLM

        Returns:
            The agent's final response

        Raises:
            AgentError: For agent-related errors
            MaxStepsExceeded: If max_steps is reached
        """
        # Start a new trace
        self.tracer.start_run(message)

        try:
            # Add user message to memory
            self.memory.add("user", message)

            # Run the agent loop
            return self._run_loop(**kwargs)

        except Exception as e:
            # Log the error and re-raise with appropriate type
            logger.error(f"Agent error: {str(e)}", exc_info=self.debug)

            # End the trace with error
            self.tracer.end_run(error=e)

            if isinstance(e, (AgentError, MaxStepsExceeded)):
                raise
            raise AgentError(f"Agent failed: {str(e)}") from e

    def _run_loop(self, **kwargs) -> str:
        """Run the agent's main loop."""
        for step in range(self.max_steps):
            # Get conversation history
            messages = self.memory.get_messages()

            try:
                # Get LLM response
                self.tracer.log_llm_call(
                    messages=messages,
                    tools=list(self.tools.values()),
                    **{k: v for k, v in kwargs.items() if k != "api_key"},
                )

                response = self.llm.complete(
                    messages=messages, tools=list(self.tools.values()), **kwargs
                )

                # Handle tool calls
                if response.get("tool_calls"):
                    for tool_call in response["tool_calls"]:
                        # Add assistant message with tool call
                        self.memory.add("assistant", None, tool_calls=[tool_call])

                        # Execute tool and add result to memory
                        tool_result = self._execute_tool(tool_call)
                        self.memory.add(
                            "tool", tool_result, tool_call_id=tool_call.get("id")
                        )

                    # Continue to next iteration to process tool results
                    continue

                # If we get here, we have a final response
                if response.get("content"):
                    self.memory.add("assistant", response["content"])

                    # End the trace successfully
                    self.tracer.end_run(output=response["content"])
                    return response["content"]

            except Exception as e:
                error = LLMError(f"Error in LLM communication: {str(e)}")
                if self.strict:
                    raise error
                logger.warning(str(error))
                return str(error)

        # If we've exhausted all steps
        error = MaxStepsExceeded(f"Maximum number of steps ({self.max_steps}) reached")
        self.tracer.end_run(error=error)
        raise error

    def explain(self) -> Dict[str, Any]:
        """Return the execution trace of the last run.

        Returns:
            A dictionary containing the execution trace
        """
        if not self.tracer.current_run:
            return {"status": "no_active_run"}
        return self.tracer.current_run.to_dict()

    def reset(self) -> None:
        """Reset the agent's memory and current run."""
        self.memory.clear()
        if hasattr(self, "tracer"):
            self.tracer.current_run = None
