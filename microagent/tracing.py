"""Tracing utilities for the microagent framework.

This module provides lightweight execution tracing so you can inspect
how an agent interacted with the LLM and tools during a run.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from .llm import Message


class StepType(str, Enum):
    """Types of steps that can occur during an agent run."""

    LLM_CALL = "llm_call"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"


@dataclass
class TraceStep:
    """Represents a single step in an agent run."""

    step_type: StepType
    timestamp: float
    data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_type": self.step_type.value,
            "timestamp": self.timestamp,
            "data": self.data,
        }


@dataclass
class RunTrace:
    """Represents a full agent run for debugging and introspection."""

    run_id: str
    input: str
    start_time: float
    end_time: Optional[float] = None
    output: Optional[str] = None
    error: Optional[str] = None
    steps: List[TraceStep] = field(default_factory=list)

    @property
    def duration(self) -> Optional[float]:
        if self.end_time is None:
            return None
        return self.end_time - self.start_time

    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "input": self.input,
            "output": self.output,
            "error": self.error,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "steps": [step.to_dict() for step in self.steps],
        }


class Tracer:
    """Collects structured trace data for an agent run."""

    def __init__(self, enabled: bool = True) -> None:
        self.enabled = enabled
        self.current_run: Optional[RunTrace] = None

    # Run lifecycle -----------------------------------------------------

    def start_run(self, input_text: str) -> None:
        """Start tracing a new agent run."""
        if not self.enabled:
            return

        self.current_run = RunTrace(
            run_id=str(uuid.uuid4()),
            input=input_text,
            start_time=time.time(),
        )

    def end_run(self, output: Optional[str] = None, error: Optional[Exception] = None) -> None:
        """Finish the current run, recording output or error."""
        if not self.enabled or not self.current_run:
            return

        self.current_run.end_time = time.time()
        self.current_run.output = output
        if error is not None:
            self.current_run.error = f"{type(error).__name__}: {error}"

    # Step logging ------------------------------------------------------

    def _add_step(self, step_type: StepType, data: Dict[str, Any]) -> None:
        if not self.enabled or not self.current_run:
            return

        step = TraceStep(
            step_type=step_type,
            timestamp=time.time(),
            data=data,
        )
        self.current_run.steps.append(step)

    def log_llm_call(
        self,
        *,
        messages: List[Message],
        tools: List[Any],
        **kwargs: Any,
    ) -> None:
        """Log an LLM invocation."""
        self._add_step(
            StepType.LLM_CALL,
            {
                "messages": messages,
                "tools": tools,
                "params": kwargs,
            },
        )

    def log_tool_call(self, name: str, arguments: Dict[str, Any]) -> None:
        """Log a tool call requested by the LLM."""
        self._add_step(
            StepType.TOOL_CALL,
            {
                "tool_name": name,
                "arguments": arguments,
            },
        )

    def log_tool_result(
        self,
        name: str,
        result: Any,
        error: Optional[Exception] = None,
    ) -> None:
        """Log the result (or error) of a tool execution."""
        data: Dict[str, Any] = {
            "tool_name": name,
            "result": result,
        }
        if error is not None:
            data["error"] = f"{type(error).__name__}: {error}"

        self._add_step(StepType.TOOL_RESULT, data)

