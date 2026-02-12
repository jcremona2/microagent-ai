"""Tool system for microagent framework."""

import inspect
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union, get_args, get_origin

from .exceptions import InvalidToolArguments, ToolExecutionError

T = TypeVar("T")


@dataclass
class Tool:
    """A callable tool with metadata and schema."""

    name: str
    func: Callable[..., Any]
    description: str
    parameters: Dict[str, Any]
    strict: bool = False

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Execute the tool with validated arguments.

        This performs lightweight runtime validation against the function
        signature and type hints before calling the underlying function.
        """
        sig = inspect.signature(self.func)

        # First, let Python's binding logic enforce required/unknown args.
        # Using `bind` (not `bind_partial`) ensures missing required arguments
        # are surfaced as errors.
        try:
            bound = sig.bind(*args, **kwargs)
        except TypeError as exc:
            raise InvalidToolArguments(
                f"Invalid arguments for tool '{self.name}': {exc}"
            ) from exc

        # Type-check bound arguments using annotations where available.
        for param_name, value in bound.arguments.items():
            if param_name not in sig.parameters:
                # Should not happen, but be defensive.
                raise InvalidToolArguments(
                    f"Unexpected argument '{param_name}' for tool '{self.name}'"
                )

            param = sig.parameters[param_name]
            annotation = param.annotation

            if annotation is inspect.Parameter.empty or value is None:
                # No type hint or explicit None (handled by Optional/Union at call site).
                continue

            if not _is_instance_of_type(value, annotation):
                raise InvalidToolArguments(
                    f"Invalid type for argument '{param_name}' in tool '{self.name}': "
                    f"expected {annotation}, got {type(value).__name__}"
                )

        # Call the underlying function and wrap any errors.
        try:
            return self.func(*bound.args, **bound.kwargs)
        except Exception as exc:
            # Include underlying exception type and message for better debugging.
            raise ToolExecutionError(
                f"Error executing tool '{self.name}': "
                f"{type(exc).__name__}: {exc}"
            ) from exc


def tool(func: Optional[Callable[..., Any]] = None, *, name: Optional[str] = None) -> Callable[..., Any]:
    """
    Decorator to register a function as a tool.

    Args:
        func: The function to decorate
        name: Optional custom name for the tool

    Returns:
        The original function, with a `. _tool` attribute attached.
    """

    def decorator(f: Callable[..., Any]) -> Callable[..., Any]:
        tool_name = name or f.__name__
        description = f.__doc__ or ""

        # Extract parameter information
        sig = inspect.signature(f)
        parameters: Dict[str, Any] = {
            "type": "object",
            "properties": {},
            "required": [],
        }

        for param_name, param in sig.parameters.items():
            if param_name == "self":
                continue

            param_info: Dict[str, Any] = {"type": "string"}  # Default type

            # Handle type hints if available
            if param.annotation != inspect.Parameter.empty:
                param_info["type"] = _get_json_schema_type(param.annotation)

            # Handle parameter description from docstring (simplified placeholder)
            param_info["description"] = ""

            parameters["properties"][param_name] = param_info

            if param.default == inspect.Parameter.empty:
                parameters["required"].append(param_name)

        # Create tool instance
        tool_instance = Tool(
            name=tool_name,
            func=f,
            description=description.strip(),
            parameters=parameters,
        )

        # Attach the Tool instance to the function for external access
        setattr(f, "_tool", tool_instance)
        return f

    # Handle both @tool and @tool() syntax
    return decorator(func) if func is not None else decorator


def _get_json_schema_type(python_type: Type[Any]) -> str:
    """Convert Python type to JSON schema type string."""
    type_map: Dict[Any, str] = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object",
    }

    origin = get_origin(python_type)

    # Handle Optional[T] and general Union[...] as the schema type of the first
    # non-None argument, falling back to "string" if ambiguous.
    if origin is not None:
        args = get_args(python_type)
        if origin in (list, List):
            return "array"
        if origin in (dict, Dict):
            return "object"
        if origin in (tuple, set):
            return "array"

        # Optional[T] or Union[T1, T2, ...]
        if origin is Union:
            non_none_args = [arg for arg in args if arg is not type(None)]
            if len(non_none_args) == 1:
                return _get_json_schema_type(non_none_args[0])
            # For broader unions, default to string as a safe generic type.
            return "string"

    # Direct/simple types.
    return type_map.get(python_type, "string")


def _is_instance_of_type(value: Any, expected_type: Type[Any]) -> bool:
    """Best-effort runtime check for value against a typing annotation."""
    origin = get_origin(expected_type)
    args = get_args(expected_type)

    if origin is None:
        # Plain Python type like int, str, etc.
        if isinstance(expected_type, type):
            return isinstance(value, expected_type)
        return True

    # Optional[T] / Union[..., None]
    if origin is Union:
        if value is None and type(None) in args:
            return True
        return any(
            _is_instance_of_type(value, arg)
            for arg in args
            if arg is not type(None)
        )

    if origin in (list, tuple, set):
        if not isinstance(value, origin):
            return False
        # If we know the element type, check a few elements.
        if args:
            elem_type = args[0]
            return all(
                _is_instance_of_type(elem, elem_type) for elem in list(value)[:5]
            )
        return True

    if origin is dict:
        if not isinstance(value, dict):
            return False
        # Key/value type checks are intentionally shallow.
        if len(args) == 2:
            key_type, val_type = args
            for k, v in list(value.items())[:5]:
                if not _is_instance_of_type(k, key_type):
                    return False
                if not _is_instance_of_type(v, val_type):
                    return False
        return True

    # Fallback for unsupported/complex annotations.
    return True
