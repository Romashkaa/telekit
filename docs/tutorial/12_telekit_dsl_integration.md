# Telekit DSL Integration

## Basic Integration

To use the Telekit DSL, inherit from `DSLHandler` and call `analyze_string()` with your script during initialization

```python
import telekit

class MyHandler(telekit.DSLHandler):
    @classmethod
    def init_handler(cls) -> None:
        cls.analyze_string(script)
        cls.on.command("start").invoke(cls.start_script)

script = """...Telekit DSL script..."""

telekit.Server(TOKEN).polling()
```

In this example:

- `analyze_string()` parses the script and registers all scenes.
- The `/start` command is bound to `start_script` — a built-in method provided by `DSLHandler`.
- When triggered, the bot executes the `main` scene defined in the script.

### Available Analysis Methods

You can load a Telekit DSL script using one of the following methods:

- `analyze_string` — parse a DSL script from a string.
- `analyze_file` — parse a DSL script from a file.
- `analyze_canvas` — parse an Obsidian Canvas as a DSL script.
- `analyze_executable_model` — load a dict as a pre-built executable model.

> [!NOTE]
> All methods except `analyze_executable_model` raise an exception if syntax errors or validation warnings are detected.

## Simplified Setup

For quick setups, you can initialize and bind a DSL script in a single call:

```python
import telekit

telekit.TelekitDSL.from_string(
    """...Telekit DSL script...""", ["start"]
)

telekit.Server(TOKEN).polling()
```

Or:

```python
import telekit

telekit.TelekitDSL.from_file("script.scr", ["help"])

telekit.Server(TOKEN).polling()
```

This approach automatically analyzes the script and binds the specified commands to start the DSL flow.

## Next Steps

For a complete overview of the DSL language, supported syntax, and advanced features, continue with the next chapter:

- [More Examples »](../../docs/examples/examples.md#telekit-dsl)
- [Next: Syntax »](13_telekit_dsl_syntax.md)