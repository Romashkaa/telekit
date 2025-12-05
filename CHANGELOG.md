# 1.1.0

## ✅ New Features
### Sender Improvements
- Context manager:
```python
with self.chain.sender as sender:
    sender.set_title("😃 Welcome!")
    sender.set_message("It's Telekit v1.1.0")
```

---

## ⏳ Delayed until v1.1.0
- DSL warning for strings with too many buttons or excessive text  
- Localization support for `self.user.enable_logging()` (currently global)