## DSL Improvements

This update enhances Telekit DSL templating by introducing **Jinja** as an alternative template engine.

- Added global `template` configuration option — `"jinja"`, `"vars"`, or `"plain"` (`"vars"` is the default):
    ```js
    $ {
        template = "jinja"
    }
    ```

- Added a per-scene `template` attribute — `"jinja"`, `"vars"`, or `"plain"`.  
  If not specified, the global `template` configuration value is used by default.
    ```js
    @ main {
        ...
        template = "jinja"
    }
    ```

- Added the `set_jinja_context` method — sets variables in the Jinja rendering context, making them available across all DSL templates (such as `title`, `message`, and others).
    - Example 1 (keyword arguments):
    ```py
    def handle(self):
        self.set_jinja_context(
            name="value"
        )
        self.start_script()
    ```
    - Example 2 (dictionary-based context):
    ```py
    def handle(self):
        self.set_jinja_context(
            {
                "name": "value"
            }
        )
        self.start_script()
    ```
