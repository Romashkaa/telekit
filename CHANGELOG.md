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

### Handler Improvements
- Added `handoff` method — allows passing control to another handler by name or class.  
  The method creates a new handler instance, passes it the current message, and transfers the previous message context:

```python
self.handoff("QuizHandler").start_quiz()

# OR

from quiz_handler import QuizHandler
self.handoff(QuizHandler).start_quiz()
```

---

## ⏳ Delayed
- DSL warning for strings with too many buttons or excessive text  
- Localization support for `self.user.enable_logging()` (currently global)