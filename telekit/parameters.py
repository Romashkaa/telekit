"""
This module defines parameter types for command handlers.

- Each parameter type (`Str`, `Int`, `Bool`, etc.) converts a string input from the user
  into the desired Python type.
- If the user **does not provide a value** for a parameter, the handler function's own default
  argument value (e.g., `def handle(message, value: int=0)`) is used.
- If the user **provides an invalid value** (like `"abc"` for an `Int` parameter), then
  the parameter type's `default_value` is used instead.

Usage example:

```
@cls.on.command("start", params=[Int(-1), Str()])
def _(message, age: int=-1, name: str="DEFAULT") # default used if user doesn't provide this parameter
    ...

```
"""

import typing

class Parameter:
    """Base class for parameter type conversion"""
    def __init__(self, func: typing.Callable[[str], typing.Any]):
        """
        Initialize with a conversion function.

        ```
        @cls.on.command("start", params=[Parameter(lambda p: list(p))])
        def _(message, value: list=DEFAULT) # default used if user doesn't provide this parameter
            ...
        ```

        Args:
            func (Callable[[str], Any]): Function to convert string parameter to desired type.
        """
        self.func = func

    def __call__(self, param_value):
        """
        Convert the parameter value using the stored function.

        Args:
            param_value (str): The parameter value as a string.

        Returns:
            Any: Converted parameter value.
        """
        return self.func(param_value)
    
class Str(Parameter):
    """Parameter type for string values"""
    def __init__(self):
        """
        Initialize Str parameter type
        ```
        @cls.on.command("start", params=[Str()])
        def _(message, value: str="DEFAULT") # default used if user doesn't provide this parameter
            ...
        ```
        """
        pass

    def __call__(self, param_value: str) -> str:
        """
        Return the string parameter value as is.

        Args:
            param_value (str): The parameter value.

        Returns:
            str: The same string value.
        """
        return param_value
    
class Int(Parameter):
    """Parameter type for integer values"""
    def __init__(self, default_value: int=0):
        """
        Initialize Int parameter type.

        ```
        @cls.on.command("start", params=[Int(DEFAULT_1)]) # default 1 value to return if conversion fails.
        def _(message, value: int=DEFAULT_2) # default 2 used if user doesn't provide this parameter
            ...
        ```

        Args:
            default_value (int): Value to return if conversion fails.
        """
        self.default_value = default_value

    def __call__(self, param_value: str):
        """
        Convert the string parameter to an integer.

        Args:
            param_value (str): The parameter value as a string.

        Returns:
            int | None: Converted integer value or default_value if conversion fails.
        """
        try:
            return int(param_value.replace("_", ""))
        except:
            return self.default_value
        
class Bool(Parameter):
    """Parameter type for boolean values"""
    def __init__(self, true_values: tuple[str, ...]=("true", "t", "yes", "y", "1")):
        """
        Initialize Bool parameter type.

        ```
        @cls.on.command("start", params=[Bool()])
        def _(message, value: bool=DEFAULT) # default used if user doesn't provide this parameter
            ...
        ```

        Args:
            true_values (tuple[str, ...]): Strings considered as True.
        """
        self.true_values = true_values

    def __call__(self, param_value: str):
        """
        Convert the string parameter to a boolean.

        Args:
            param_value (str): The parameter value as a string.

        Returns:
            bool: True if param_value is in true_values, False otherwise.
        """
        return param_value.lower() in self.true_values