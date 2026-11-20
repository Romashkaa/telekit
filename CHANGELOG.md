### v2.6.0 `a9` – Keyboards in Senders
- Added `InlineKeyboard.to_markup()`: compiles the keyboard into a ready-to-send `InlineKeyboardMarkup`. Only buttons that don't need a chain to register handlers are supported (`StaticButton`, `LinkButton` and its subclasses, `WebAppButton`, `SuggestButton`, `CopyTextButton`); callback-based buttons (`CallbackButton`, `InvokeButton`, `AnswerButton`, `AlertButton`, `NotificationButton`) raise `TypeError` and should be used via `chain.set_inline_keyboard()`
- Added `ReplyKeyboard.to_markup()`: a public counterpart of the internal `_compile()` that returns a `ReplyKeyboardMarkup`
- Added `set_keyboard()` to `BaseSender`: a shortcut for `set_reply_markup(keyboard.to_markup())` that accepts both `InlineKeyboard` and `ReplyKeyboard`, so keyboards can be passed to a plain `sender` without a chain

### v2.6.0 `a7` – Sender, Server, Logging
#### Sender: automatic `file_id` caching
- Added a `FileIdCache` that stores Telegram `file_id` for local files (photo, document, video, animation, audio, voice, video note), so repeated sends skip the upload
- Added `BaseSender.configure_file_cache()`: a class method that sets the database path, table name and global on/off switch
- Added `Sender.set_use_file_cache()`: a per-sender override of the global setting (`None` restores it)
- Changed missing local files to raise on `send()` instead of in the setter
- A rejected cached `file_id` is dropped and the send is retried with the original file
- Notes: URLs, `bytes` and file-like objects are not cached; rich messages and media groups are unaffected. A changed file is detected by `size/mtime`, with a `SHA-256` comparison as a fallback
#### Server: restarts and network protection
- Added `restart` parameter to `Server`: `"always"` (default), `"network"` or `"never"`; accepts `RestartMode` or the matching string
- Deprecated `Server(auto_restart=...)`: `True` is now `restart="always"`, `False` is `restart="never"`; emits `DeprecationWarning` and a log warning. Cannot be combined with `restart` (`TypeError`)
- Added network protection to `Server.polling()` and `Server.long_polling()`: restarts are now delayed by exponential backoff (5 s up to 60 s, reset after 120 s of stable work) instead of a fixed 10 s / 5 s. Tunable via `Server.RESTART_DELAY_MIN`, `RESTART_DELAY_MAX` and `STABLE_AFTER`
- Added `restart="network"`: survives only network errors and Bot API `429`, `500`, `502`, `503`, `504`; any other error (bad token, `409` conflict, bugs) is re-raised. `retry_after` from Telegram is respected
- Changed `Server.__init__()` to wait for the Bot API to become reachable before calling `getMe` (skipped for `restart="never"` and when `apihelper.proxy` is set)
- Fixed `Server.polling()` and `Server.long_polling()` restarting after `stop_polling()`: they now return instead
- Fixed a failed `getMe` in the restart cycle killing the server and hiding the original error
- Fixed bot tokens leaking into logs through request URLs: they are now masked as `bot<hidden>`
- Changed log levels in `Server`: network errors are logged as `WARNING` (without traceback), unexpected errors as `ERROR` (with traceback), `FATAL` is kept for `[server dead]`.
#### Logging
- Added Rich output for logs when `rich` is installed; set `TELEKIT_NO_RICH=1` to disable it
- Added direct exports `server_logger`, `library_logger`, `user_logger` and `get_user_logger()` to `_logger.py`. `logger.server`, `logger.library`, `logger.users()`, `_server` and `_library` still work
- Added `set_level()`, `disable_user_logging()` and `UserLogger.exception()`
- Changed `telekit` loggers to `propagate=False`: records no longer reach the root logger, so they are not duplicated when the app configures it. Attach custom handlers to `logging.getLogger("telekit")`
- Changed `enable_file_logging()` to be idempotent, to create parent folders, and to use one format (with `filename:lineno`) for all files, including `server.log`
- Fixed `UserLogger` reporting its own module as the log source

### v2.6.0 `a6` (fixes #6) – Timeout engine
- Reworked the timeout engine to fix thread exhaustion with many concurrent chats (#6): every `set_timeout()` used to start its own `threading.Timer` (one OS thread per waiting chat), so ~1000 active users crashed the bot with `can't start new thread`
- Timeout callback exceptions are now logged
- Added `configure_timeouts(max_workers, *, idle_timeout, log_worker_changes, warn_on_max_workers)` to tune the worker pool, log worker start/stop, and control the "all workers busy" warning (enabled by default)

### v2.6.0 `a4` – Handoff shortcuts
- Added `handle_handoff()` to `Handler`: a shortcut for `handoff(handler).handle()` that takes the target handler as an argument, so it can be passed to `add_callback()` without an extra closure
- Added `handle_handoff_back_or()` to `TrackHandoffOrigin`: a closure-free counterpart of `handoff_back_or()`
- Reworked `handoff_back_or()` as a thin `functools.partial` wrapper around `handle_handoff_back_or()`
- Fixed the `handoff_back_or()` docstring: the returned callable forwards its arguments to `handle()` instead of being zero-argument
- Converted the `handoff()` docstring to reST

### v2.6.0 `a3` – Rich HTML
- Added support for Rich HTML messages (Bot API 10.1+)
- Added the `_rich.py` module for Rich HTML parsing and serialization
- Added new rich tags to `styles.py` for enhanced text formatting
- Added the `rich.py` example handler demonstrating Rich HTML: inline styles, blocks, lists, tables, media, and sender integration

### v2.6.0 `a2` – Env parsing
- Reworked `.env` and token/canvas file reading in `utils`
- Added full `.env` syntax support: comments, `export`, quotes and escapes, multi-line values, `$VAR` interpolation
- Added the `cache` parameter (default `True`) and `clear_cache()`
- Added detailed errors with fix suggestions and creation commands, and new `Env*Error` exceptions
- Changed `load_env()` to raise `EnvFileNotFoundError` for a missing file instead of returning `{}`

### v2.6.0 `a1` – Module loader
- Added a module-loading utility to `utils`

### v2.6.0 `a0`
- Improved formatting in `_on.py`