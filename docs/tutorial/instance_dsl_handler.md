## `InstanceDSLHandler`: Instance-based DSL Handler

Instance-oriented variant of `DSLHandler` where each instance carries its own
`executable_model`, `_script_data_factory`, and `_jinja_env` — allowing multiple
instances to run completely independent scripts simultaneously.

Use the `*_locally` instance methods instead of the class-level ones:

```python
class MyHandler(telekit.InstanceDSLHandler):
    @classmethod
    def init_handler(cls) -> None:
        cls.on.message().invoke(cls.handle)

    def handle(self):
        script = fetch_script_from_db(self.user.id)  # per-user DSL
        self.analyze_string_locally(script)
        self.start_script()
```

| **Method**                              | **Description**                                      |
| --------------------------------------- | ---------------------------------------------------- |
| `analyze_file_locally(path, encoding)`  | Analyse a script file on this instance.              |
| `analyze_string_locally(script)`        | Analyse a DSL string on this instance.               |
| `analyze_canvas_locally(file_path)`     | Analyse an Obsidian `.canvas` file on this instance. |
| `analyze_executable_model_locally(model)` | Load a pre-built model dict on this instance.      |

**Security**

When accepting scripts from untrusted users, restrict dangerous features via the
`RESTRICTED` class attribute. Set `DEFAULT_TIMEOUT` to control the fallback timeout,
and `DEFAULT_CONFIG` to provide a safe base config.

```python
class SafeDSL(telekit.InstanceDSLHandler):
    RESTRICTED: list[RestrictedToken] = ["hook", "jinja", "redirect", "handoff", "config"]
    DEFAULT_TIMEOUT = 120
    DEFAULT_CONFIG  = {"template": "vars"}
```

| **Token**      | **Effect**                                                                                      |
| -------------- | ----------------------------------------------------------------------------------------------- |
| `"handoff"`    | Disables `handoff` button type (cross-handler transitions).                                     |
| `"redirect"`   | Disables `redirect` button type (simulated user messages).                                      |
| `"hook"`       | Removes all `on_enter`, `on_enter_once`, `on_exit`, `on_timeout` hooks.                        |
| `"jinja"`      | Forces template engine to `"vars"`; Jinja is never executed.                                    |
| `"timeout"`    | Ignores per-script `timeout_time`; uses `DEFAULT_TIMEOUT` only.                                 |
| `"config"`     | Replaces script config with `DEFAULT_CONFIG`; `vars_*` keys are preserved unless `"vars"` is also set. |
| `"vars"`       | Removes all `vars_*` keys and disables `{{variable}}` substitution.                             |
| `"images"`     | Strips `image` field from every scene.                                                          |
| `"links"`      | Disables `link` button type (external URLs).                                                    |
| `"suggest"`    | Disables `suggest` button type (pre-filled entry suggestions).                                  |
| `"entry"`      | Disables entry handlers (free-text input routing).                                              |
| `"next"`       | Disables `next` magic scene navigation.                                                         |
| `"back"`       | Disables `back` magic scene navigation.                                                         |