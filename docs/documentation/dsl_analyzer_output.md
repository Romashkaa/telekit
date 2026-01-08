# Telekit DSL Analyzer Output

## Display Data

Use the cls.display_script_data() method inside init_handler to inspect the Executable Model:

```py
@classmethod
def init_handler(cls) -> None:
    cls.on.command("start").invoke(cls.start_script)
    cls.analyze_source(script)
    
    cls.display_script_data() # prints cls.executable_model
```

## Executable Model

Example script:

```js
$ timeout {
    time = 64
}

$ vars {
    BOT_NAME = "Example Bot"
    ANOTHER_VAR = 12
}

@ main {
    title = "👋 This is the {{BOT_NAME}}!"
    message = "Available features:"

    buttons (2) {
        redirect("Redirect", "/start")
        handoff("Handoff", "PyAPIHandler")

        link("Link", "https://github.com/Romashkaa/telekit")

        scene2("Scene #2 »")
    }
}

@ scene2 {
    title = "⌨️ Scene #2"
    message = "Send a message..."

    buttons (2) {
        suggest("Suggestion #1", "suggestion*")
        suggest("#2", "Default Suggestion")
        back()
        next("Skip »")
    }

    entries {
        entry_test("suggestion*")
        my_default_entry
    }
}

@ entry_test {
    title = "🤖 Scene #3"
    message = "Result: {{entry:🕸️}}"

    buttons (2) {
        back()
        main("↺ Restart")
    }
}

@ my_default_entry {
    title = "🤖 Scene #4"
    message = "_Unexpected_ Result: {{entry}}"
    parse_mode = "markdown"

    buttons (2) {
        back()
        main("↺ Restart")
    }
}
```

Executable Model generated from this script:

```json
{
    "config": {
        "timeout_time": 64,
        "vars_BOT_NAME": "Example Bot",
        "vars_ANOTHER_VAR": 12,
        "next_order": [
            "main",
            "scene2",
            "entry_test",
            "my_default_entry"
        ]
    },
    "scenes": {
        "main": {
            "name": "main",
            "title": "👋 This is the {{BOT_NAME}}!",
            "message": "Available features:",
            "buttons": {
                "Redirect": {
                    "type": "redirect",
                    "target": "/start"
                },
                "Handoff": {
                    "type": "handoff",
                    "target": "PyAPIHandler"
                },
                "Link": {
                    "type": "link",
                    "target": "https://github.com/Romashkaa/telekit"
                },
                "Scene #2 »": {
                    "type": "scene",
                    "target": "scene2"
                }
            },
            "row_width": 2
        },
        "scene2": {
            "name": "scene2",
            "title": "⌨️ Scene #2",
            "message": "Send a message...",
            "entries": {
                "suggestion*": "entry_test"
            },
            "_default_entry_target": "my_default_entry",
            "buttons": {
                "Suggestion #1": {
                    "type": "suggest",
                    "target": [
                        "entry_test",
                        "suggestion*"
                    ]
                },
                "#2": {
                    "type": "suggest",
                    "target": [
                        "my_default_entry",
                        "Default Suggestion"
                    ]
                },
                "« Back": {
                    "type": "scene",
                    "target": "back"
                },
                "Skip »": {
                    "type": "scene",
                    "target": "next"
                }
            },
            "row_width": 2,
            "_has_back_option": true
        },
        "entry_test": {
            "name": "entry_test",
            "title": "🤖 Scene #3",
            "message": "Result: {{entry:🕸️}}",
            "buttons": {
                "« Back": {
                    "type": "scene",
                    "target": "back"
                },
                "↺ Restart": {
                    "type": "scene",
                    "target": "main"
                }
            },
            "row_width": 2,
            "_has_back_option": true
        },
        "my_default_entry": {
            "name": "my_default_entry",
            "title": "🤖 Scene #4",
            "message": "_Unexpected_ Result: {{entry}}",
            "parse_mode": "markdown",
            "buttons": {
                "« Back": {
                    "type": "scene",
                    "target": "back"
                },
                "↺ Restart": {
                    "type": "scene",
                    "target": "main"
                }
            },
            "row_width": 2,
            "_has_back_option": true
        }
    },
    "order": [
        "main",
        "scene2",
        "entry_test",
        "my_default_entry"
    ],
    "source": "$ timeout { ... main(\"↺ Restart\")\n    }\n}"
}
```