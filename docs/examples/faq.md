# FAQ (Telekit DSL)

**Telekit DSL** — this is a custom domain-specific language (DSL) used to create interactive pages, such as FAQs.  
It allows you to describe the message layout, add images, and buttons for navigation between pages in a convenient, structured format that your bot can easily process.

The parser and analyzer provide an excellent system of warnings and errors with examples, so anyone can figure it out!

To integrate Telekit DSL into your project, simply add it as a Mixin to your Handler:

```python
import telekit

class FAQHandler(telekit.GuideMixin):
    @classmethod
    def init_handler(cls) -> None:
        cls.analyze_source(source)
        cls.on.command("faq").invoke(cls.start_script)

source = """...Telekit DSL..."""

telekit.Server(TOKEN).polling()
```

- Even easier: call the appropriate method:

```python
import telekit

telekit.TelekitDSL.from_string("""...Telekit DSL...""", ["start"])

telekit.Server(TOKEN).polling()
```

For more details on the syntax, see the [Telekit DSL Syntax reference](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/11_telekit_dsl.md)