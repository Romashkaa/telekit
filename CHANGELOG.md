# 1.1.0

## ✅ New Features
### Sender Improvements
- Context manager:
```python
with self.chain.sender as sender:
    sender.set_title("😃 Welcome!")
    sender.set_message("It's Telekit v1.1.0")
```
- New `sender.then_send()` method.
- Bug Fixed: Fix handling of `None` values in `set_edit_message` and `set_reply_to` methods (Commit `1c1f3fc`)
- Enhance `append` method in Sender

### Handler Improvements
- Added `handoff` method — allows passing control to another handler by name or class.  
  The method creates a new handler instance, passes it the current message, and transfers the previous message context:

```python
self.handoff("QuizHandler").start_quiz()

# OR

from quiz_handler import QuizHandler
self.handoff(QuizHandler).start_quiz()
```
- Added `freeze` method — provides a zero-argument wrapper for passing callbacks with bound arguments into inline keyboards:

```python
btn = self.freeze((lambda a, b: a + b), 2, 3)
btn() # 5
```

### Chain Improvements
- `chain.set_default_timeout(seconds, message)` method - Sets a default timeout for user inactivity.

---

## ⏳ Delayed
- DSL warning for strings with too many buttons or excessive text  
- Localization support for `self.user.enable_logging()` (currently global)