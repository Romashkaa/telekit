### v2.6.0 `a3`
- Added support for Rich HTML messages (Bot API 10.1+) and enhance styles
    - Introduced a new module `_rich.py` to handle Rich HTML parsing and serialization.
    - Updated `styles.py` to include new rich tags for enhanced text formatting.
    - Created `rich.py` example handler to demonstrate the usage of Rich HTML features, including inline styles, blocks, lists, tables, media, and sender integration.


### v2.6.0 `a2`
- Reworked `.env` and token/canvas file reading in `utils`: full `.env` syntax support (comments, `export`, quotes and escapes, multi-line values, `$VAR` interpolation), a `cache` parameter (default `True`) with `clear_cache()`, detailed errors with fix suggestions and creation commands, and new `Env*Error` exceptions; `load_env` now raises `EnvFileNotFoundError` for a missing file instead of returning `{}`

### v2.6.0 `a1`
- Added a module-loading utility in `utils`

### v2.6.0 `a0`
- Improved formatting in `_on.py`