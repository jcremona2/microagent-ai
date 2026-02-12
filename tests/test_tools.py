"""Tests for the tool system."""

from unittest.mock import MagicMock

import pytest

from microagent.exceptions import InvalidToolArguments, ToolExecutionError
from microagent.tools import Tool, tool


def test_tool_decorator_without_args():
    """Test @tool decorator without arguments."""

    @tool
    def test_func(x: int) -> int:
        """Test function."""
        return x * 2

    assert hasattr(test_func, "_tool")
    assert isinstance(test_func._tool, Tool)
    assert test_func._tool.name == "test_func"
    assert test_func._tool.description == "Test function."
    assert test_func._tool.parameters["properties"]["x"]["type"] == "integer"


def test_tool_decorator_with_name():
    """Test @tool decorator with custom name."""

    @tool(name="custom_name")
    def test_func():
        pass

    assert test_func._tool.name == "custom_name"


def test_tool_execution():
    """Test tool execution with arguments."""

    @tool
    def add(a: int, b: int) -> int:
        """Add two numbers."""
        return a + b

    result = add._tool(a=2, b=3)
    assert result == 5


def test_tool_execution_with_invalid_args():
    """Test tool execution with invalid arguments."""

    @tool
    def test_func(x: int):
        pass

    with pytest.raises(InvalidToolArguments):
        test_func._tool()  # Missing required argument

    with pytest.raises(InvalidToolArguments):
        test_func._tool(x="not_an_int")  # Wrong type


def test_tool_with_optional_args():
    """Test tool with optional arguments."""

    @tool
    def greet(name: str, title: str = "Mr.") -> str:
        """Greet someone."""
        return f"Hello, {title} {name}"

    # Test with both args
    assert greet._tool(name="Smith", title="Dr.") == "Hello, Dr. Smith"

    # Test with default arg
    assert greet._tool(name="Smith") == "Hello, Mr. Smith"


def test_tool_with_complex_types():
    """Test tool with complex type hints."""
    from typing import Dict, List, Optional

    @tool
    def process_data(items: List[Dict[str, int]], limit: Optional[int] = None) -> int:
        """Process a list of items."""
        return sum(sum(item.values()) for item in items[:limit] if limit)

    # This test just checks that the schema is generated correctly
    params = process_data._tool.parameters
    assert params["properties"]["items"]["type"] == "array"
    assert params["properties"]["limit"]["type"] == "integer"


def test_tool_error_handling():
    """Test tool error handling."""

    @tool
    def error_func():
        """Raise an error."""
        raise ValueError("Something went wrong")

    with pytest.raises(ToolExecutionError) as exc_info:
        error_func._tool()

    assert "Error executing tool 'error_func'" in str(exc_info.value)
    assert "ValueError: Something went wrong" in str(exc_info.value)


def test_tool_metadata():
    """Test tool metadata is correctly extracted."""

    @tool
    def example(name: str, age: int = 30, active: bool = True) -> str:
        """An example function with metadata.

        Args:
            name: The person's name
            age: The person's age
            active: Whether the person is active

        Returns:
            A greeting message
        """
        return f"{name} is {age} years old"

    tool_instance = example._tool

    # Check basic metadata
    assert tool_instance.name == "example"
    assert "An example function with metadata" in tool_instance.description

    # Check parameters
    params = tool_instance.parameters
    assert params["required"] == ["name"]
    assert params["properties"]["name"]["type"] == "string"
    assert params["properties"]["age"]["type"] == "integer"
    assert params["properties"]["active"]["type"] == "boolean"

    # Check parameter descriptions (if implemented in the tool decorator)
    # This is a placeholder for when docstring parsing is implemented
    # assert 'The person\'s name' in params['properties']['name']['description']
