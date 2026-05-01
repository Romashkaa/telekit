## Utils

| **Name**       | **Description**                                                                 |
| -------------- | ------------------------------------------------------------------------------- |
| `load_env`     | Load all key-value pairs from a `.env` file into a dictionary.                  |
| `read_envar`   | Read a single variable by name from a `.env` file.                              |

- `read_token` and `read_canvas_path` now support reading from `.env` files.
  Pass `".env"` to use the default key, or `".env:KEY"` to specify a custom one:

```python
  read_token(".env")              # reads TOKEN
  read_token(".env:BOT_TOKEN")    # reads BOT_TOKEN

  read_canvas_path(".env")        # reads CANVAS_PATH
  read_canvas_path(".env:MY_CANVAS")
```