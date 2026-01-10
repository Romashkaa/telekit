# Telekit DSL Integration

This guide explains how to integrate **Telekit DSL** into your project and start using scripted scenes in your bot.

## Basic Integration

To enable Telekit DSL, add the DSL mixin to your handler class and analyze the DSL source code during initialization.

```python
import telekit

script = """...Telekit DSL source..."""

class HelpHandler(telekit.TelekitDSL.Mixin):
    @classmethod
    def init_handler(cls) -> None:
        cls.analyze_source(script)
        cls.on.command("help").invoke(cls.start_script)

telekit.Server(TOKEN).polling()
```

In this example:

- `analyze_source()` parses and analyzes the DSL code stored in the `script` variable.
- The `/help` command is registered and bound to `start_script`, a method provided by the DSL mixin.
- When the command is triggered, the "main" scene of the script is executed.

## Available Analysis Methods

You can analyze Telekit DSL code using the following methods:

- `analyze_source` — Analyze a DSL script provided as a string.
- `analyze_file` — Analyze a DSL script from a file.

> **Note:**  
> Both `analyze_source` and `analyze_file` will raise an exception if syntax errors or analyzer warnings are detected.

Additional DSL-related methods are covered in later sections of the documentation.

## Simplified Setup

For quick setups, you can initialize and bind a DSL script in a single call:

```python
import telekit

telekit.TelekitDSL.from_string(
    """...Telekit DSL source...""",
    commands=["help"]
)

telekit.Server(TOKEN).polling()
```

This approach automatically analyzes the script and binds the specified commands to start the DSL flow.

## Next Steps

For a complete overview of the DSL language, supported syntax, and advanced features, continue with the next chapter:

[Telekit DSL Syntax »](13_telekit_dsl_syntax.md)