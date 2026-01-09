## Sender Improvements

- Message editing error warning has been deleted.

## DSL Improvements

- New variables:
    - `next_scene_name` – internal name of the next scene
    - `next_scene_title` – title of the next scene
    - `next_scene_message`  – message text of the next scene
- Timeout changes:
    - The default value for `timeout_time` congig is now 300 seconds (5 minutes).
    - Set `timeout_time = 0` to disable the timeout.
- Jinja:
    - The Jinja environment is now shared globally (class attribute).
    - You can configure the environment using:
    ```py
    cls.set_jinja_env(jinja2.Environment(loader=jinja2.FileSystemLoader("templates")))
    ```
    - Access the environment via:
    ```py
    cls.jinja_env
    self.jinja_env
    ```
- Internal DSL mixin refactoring
