### v2.6.0 `a4`
- Added `handle_handoff()` to `Handler`: a shortcut for `handoff(handler).handle()` that takes the target handler as an argument, so it can be passed to `add_callback()` without an extra closure
- Added `handle_handoff_back_or()` to `TrackHandoffOrigin`: a closure-free counterpart of `handoff_back_or()`
- Reworked `handoff_back_or()` as a thin `functools.partial` wrapper around `handle_handoff_back_or()`
- Fixed the `handoff_back_or()` docstring: the returned callable forwards its arguments to `handle()` instead of being zero-argument
- Converted the `handoff()` docstring to reST

### v2.6.0 `a3`
- Added support for Rich HTML messages (Bot API 10.1+)
- Added the `_rich.py` module for Rich HTML parsing and serialization
- Added new rich tags to `styles.py` for enhanced text formatting
- Added the `rich.py` example handler demonstrating Rich HTML: inline styles, blocks, lists, tables, media, and sender integration

### v2.6.0 `a2`
- Reworked `.env` and token/canvas file reading in `utils`
- Added full `.env` syntax support: comments, `export`, quotes and escapes, multi-line values, `$VAR` interpolation
- Added the `cache` parameter (default `True`) and `clear_cache()`
- Added detailed errors with fix suggestions and creation commands, and new `Env*Error` exceptions
- Changed `load_env()` to raise `EnvFileNotFoundError` for a missing file instead of returning `{}`

### v2.6.0 `a1`
- Added a module-loading utility to `utils`

### v2.6.0 `a0`
- Improved formatting in `_on.py`