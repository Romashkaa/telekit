# 1.2.2

## DSL Improvements

- Added support for `get_variable` in handler classes, allowing custom variables
  to be dynamically resolved in Telekit DSL scripts.

## Chain Improvements
- `row_width` now supports iterables (e.g. `[2, 1, 3]`):
```py
@self.chain.inline_keyboard(
    {
        "🧮 Counter": "CounterHandler",
        "⌨️ Entry":     "EntryHandler",
        "📚 FAQ":         "FAQHandler",
        "📄 Pages":     "PagesHandler",
        "🦻 On Text":  "OnTextHandler",
    }, row_width=[2, 1, 2]
)
def handle_response(message, handler: str):
    self.handoff(handler).handle()
```