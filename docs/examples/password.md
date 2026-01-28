# Password: Input Handling

```python
import telekit

class PasswordHandler(telekit.TelekitDSL.Mixin):
    @classmethod
    def init_handler(cls) -> None:
        cls.analyze_string(script)
        cls.on.command("start").invoke(cls.start_script)

# ------------------------------------------------------
# Telekit DSL
# ------------------------------------------------------
#
# Tuturial on GitHub: https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/11_telekit_dsl.md
#

script = """
@ main {
    title = "Welcome!"
    message = "Enter the password:"

    buttons (2) {
        suggest("Help", "1111") // opens the `okay` scene; {{entry}} becomes "1111"
        okay("Skip »")          // skips input; {{entry}} will be `none`
    }

    entries {
        okay("1111") // opens the `okay` scene when the user enters "1111"
        fail         // opens the `fail` scene for any other input
    }
}

@ okay {
    title = "Correct!"
    message = `
        You entered: {{entry:Nothing, you just clicked 'Skip'}}

        Your reward is the following link:
    `
    buttons (2) {
        back() // back to `main`
        link("Reward", "https://github.com/Romashkaa/telekit")
    }
}

@ fail {
    title = "Wrong password: {{entry}}!"
    message = "The password you entered is incorrect. Please try again."

    buttons {
        back("« Try again") // back to `main`
    }
}
"""

telekit.Server(TOKEN).polling()
```