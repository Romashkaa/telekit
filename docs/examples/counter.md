# Counter

Counter with "+" and "-" buttons.

<details>
  <summary>Click to See Results</summary>
  <table>
    <tr>
      <td><img src="../images/telekit_example_2.jpg" alt="Telekit Example 2" width="300"></td>
      <td><img src="../images/telekit_example_3.jpg" alt="Telekit Example 3" width="300"></td>
    </tr>
  </table>
</details>

```python
import telekit

class CounterHandler(telekit.Handler):

    @classmethod
    def init_handler(cls) -> None:
        """
        Initializes the message handler for the '/start' command.
        """
        cls.on.command("start").invoke(cls.handle)

    def handle(self) -> None:
        self.chain.sender.set_title("Hello")
        self.chain.sender.set_message("Click the button below to start interacting")
        self.chain.sender.set_photo("https://static.wikia.nocookie.net/ssb-tourney/images/d/db/Bot_CG_Art.jpg/revision/latest?cb=20151224123450")
        self.chain.sender.set_effect(self.chain.sender.Effect.PARTY)

        self.click_count: int = 0

        @self.chain.inline_keyboard({"⊕": 1, "⊖": -1}, row_width=2)
        def _(value: int) -> None:
            self.click_count += value
            self.chain.sender.set_message(f"You clicked {self.click_count} times")
            self.chain.edit()
            
        self.chain.set_remove_inline_keyboard(False)
        self.chain.disable_timeout_warnings()
        self.chain.edit()

telekit.Server(TOKEN).polling()
```