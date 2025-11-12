# Telekit DSL Integration

To integrate Telekit DSL into your project, simply add it as a Mixin to your Handler:

```python
import telekit

source = """...Telekit DSL..."""

class GuideHandler(telekit.GuideMixin):
    @classmethod
    def init_handler(cls) -> None:
        cls.on.message(["faq"]).invoke(cls.start_script)
        cls.analyze_source(source)

telekit.Server(TOKEN).polling()
```

Even easier: call the appropriate method:

```python
import telekit

telekit.TelekitDSL.from_string("""...Telekit DSL...""", ["faq"])

telekit.Server(TOKEN).polling()
```

[Telekit DSL Syntax »](13_telekit_dsl_syntax.md)