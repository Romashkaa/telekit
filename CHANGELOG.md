# 1.2.0

## ✅ New Features
### Sender Improvements

### Handler Improvements

### Chain Improvements

### DSL Improvements
- Added support for {{variables}} in `title=` and `message=`.
  - HTML and Markdown tags in variable values are automatically sanitized.
  - Recursive variable replacement is prevented (only first-level substitution is performed).
  - Example: (`<b>username</b>` - bold; `{{first_name}}` and `{{username}}` - sanitized>)
```js
@ main {
    title = "Welcome, {{first_name:user}}!"; // "user" is default value
    message = "Did you know your <b>username</b> is {{username}}? Cool, isn't it?";
    parse_mode = "html";
}
```
- Improved indentation handling in multiline strings.

---

## ⏳ Delayed
- DSL warning for strings with too many buttons or excessive text  
- Localization support for `self.user.enable_logging()` (currently global)