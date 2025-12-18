# Copyright (c) 2025 Ving Studio, Romashka
# Licensed under the MIT License. See LICENSE file for full terms.

from . import parser

import telekit

from telekit.styles import Sanitize

from typing import NoReturn
import re

MAGIC_SCENES = parser.MAGIC_SCENES

class TelekitDSLMixin(telekit.Handler):
    """
    TelekitDSLMixin — Mixin for creating interactive FAQ inside a Telekit handler.

    This class allows you to:
    - Load guide data from a Telekit DSL file or string.
    - Automatically handle user navigation between scenes.
    - Render scenes with inline keyboards and formatting.

    Requirements:
    - The handler using this mixin must call `analyze_file()` or `analyze_source()` before `start_script()`.

    [Learn more on GitHub](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/11_telekit_dsl.md)

    ## Usage:
    ```
        import telebot.types
        import telekit

        class MyFAQHandler(telekit.TelekitDSL.Mixin):
            @classmethod
            def init_handler(cls) -> None:
                cls.analyze_source(guide)
                cls.on.command("faq").invoke(cls.start_script)

            # If you want to add your own bit of logic:

            # def start_script(self):
            #     # Your logic
            #     super().start_script()
    ```

    [Learn more on GitHub](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/11_telekit_dsl.md) · Tutorial
    """

    data: dict | None = None

    @classmethod
    def analyze_file(cls, path: str, encoding: str="utf-8")  -> None | NoReturn:
        """
        Analyze an script file and store parsed data in the class.

        Raises an error if there are syntax errors or analyzer warnings.

        :param path: Path to the script. Supports any file extension
        :type path: str
        :param encoding: Encoding
        :type encoding: str
        """
        with open(path, "r", encoding=encoding) as f:
            content = f.read()
            cls.analyze_source(content)

    @classmethod
    def analyze_source(cls, script: str) -> None | NoReturn:
        """
        Analyze an script from string and store parsed data in the class.

        Raises an error if there are syntax errors or analyzer warnings.
        
        :param script: Telekit DSL script
        :type script: str
        """
        cls.data = parser.analyze(script)

    # ----------------------------------------------------------------------------
    # Preparation
    # ----------------------------------------------------------------------------

    def start_script(self) -> None | NoReturn:
        """
        Start the guide; Raises an error if data is not loaded.
        """
        if not self.data:
            raise RuntimeError("Script data not loaded. Call `analyze_file` or `analyze_source` first.")
        
        # initialize history
        self.history: list[str] = []

        # check if 'scenes' exists and is a dictionary
        if "scenes" not in self.data:
            raise KeyError("Missing 'scenes' key in script data.")
        if not isinstance(self.data["scenes"], dict):
            raise TypeError("'scenes' should be a dictionary.")
        self.scenes: dict[str, dict] = self.data["scenes"]

        # check if 'order' exists and is a dictionary
        if "order" not in self.data:
            raise KeyError("Missing 'order' key in script data.")
        if not isinstance(self.data["order"], list):
            raise TypeError("'order' should be a list of strings.")
        self.order: list[str] = self.data["order"]

        # check if 'config' exists and is a dictionary
        if "config" not in self.data:
            raise KeyError("Missing 'config' key in script data.")
        if not isinstance(self.data["config"], dict):
            raise TypeError("'config' should be a dictionary.")
        self.config = self.data["config"]

        # timeout
        self._timeout_time = self.config.get("timeout_time", 0)
        if isinstance(self._timeout_time, int):
            self.chain.set_timeout(self._on_timeout, self._timeout_time)
        self.chain.set_remove_timeout(False)

        # next_order
        self._next_order: list[str] | None = self.config.get("next_order")
        if not isinstance(self._next_order, list):
            raise TypeError("'next_order' config should be a list of strings.")

        # start the main scene
        self.prepare_scene("main")()
    
    # ----------------------------------------------------------------------------
    # Scene Rendering
    # ----------------------------------------------------------------------------

    def prepare_scene(self, _scene_name: str):
        """
        Prepare the scene renderer
        """

        def render():

            scene_name = _scene_name

            # magic scenes logic
            if scene_name in MAGIC_SCENES:
                match scene_name:
                    case "back":
                        if self.history:
                            self.history.pop() # current
                        if self.history:
                            scene_name = self.history.pop()
                    case "next":
                        scene_name = self._get_next_scene_name()

            self.history.append(scene_name)

            # main logic
            scene = self.scenes[scene_name]

            real_parse_mode: str | None = scene.get("parse_mode")
            parse_mode = real_parse_mode or "html"

            self.chain.sender.set_parse_mode(parse_mode)
            self.chain.sender.set_use_italics(scene.get("use_italics", False))

            styles = self.chain.sender.styles
            title = scene.get("title", "[ no title ]")
            message = scene.get("message", "[ no message ]")
            do_sanitize = not real_parse_mode

            # variables
            if "{{" in title or "{{" in message:
                title = self._parse_variables(title, real_parse_mode)
                message = self._parse_variables(message, real_parse_mode)

            # title and message
            if do_sanitize:
                self.chain.sender.set_title(styles.sanitize(title))
                self.chain.sender.set_message(styles.sanitize(message))
            else:
                self.chain.sender.set_title(styles.no_sanitize(title))
                self.chain.sender.set_message(styles.no_sanitize(message))
            
            # image
            self.chain.sender.set_photo(scene.get("image", None))

            # keyboard
            keyboard: dict = {}
            has_back_button = False

            for button_label, button_scene in scene.get("buttons", {}).items():
                keyboard[button_label] = self.prepare_scene(button_scene)

                if "back" in button_scene:
                    has_back_button = True

            if not has_back_button:
                self.history.clear()
                self.history.append(scene_name)

            self.chain.set_inline_keyboard(keyboard, scene.get("row_width", 1))
            self.chain.edit()

        return render
    
    # ----------------------------------------------------------------------------
    # Timeout Logic
    # ----------------------------------------------------------------------------

    def _on_timeout(self):
        message = self.config.get("timeout_message", "👋 Are you still there?")
        message = self.chain.sender.styles.no_sanitize(message)
        label   = self.config.get("timeout_label", "Yes, I'm here ✓")

        self.chain.set_timeout(None, 7)
        self.chain.sender.add_message("\n\n", self.chain.sender.styles.bold(message))
        self.chain.set_inline_keyboard({label: self._continue})

        self.chain.edit()

    def _continue(self):
        self.chain.set_timeout(self._on_timeout, self._timeout_time)
        self.prepare_scene(self.history.pop())()

    # ----------------------------------------------------------------------------
    # Variables
    # ----------------------------------------------------------------------------

    def _get_variable(self, name: str) -> str | None:
        match name:
            case "first_name":
                return self.user.first_name
            case "last_name":
                return self.user.last_name
            case "full_name":
                return str(self.user.full_name)
            case "chat_id":
                return str(self.message.chat.id)
            case "user_id":
                return str(self.user.id)
            case "username":
                return getattr(self.message.from_user, "username", None)
            case _:
                return

    def _parse_variables(self, template_str: str, parse_mode: str | None=None):
        """
        Replace {{variables}} in template_str with values from the dict or callables.
        Supports optional default values using the syntax {{variable|default text}}.
        Non-recursive: {{…}} inside values are left as-is.

        Args:
            template_str (str): The template string containing {{variables}}.
            parse_mode (str | None): Optional parse mode for sanitization.

        Returns:
            str: The template string with variables replaced.
        """

        # match {{variable:default}} or {{variable}}
        pattern = re.compile(r'\{\{(\w+)(?::([^}]+))?\}\}')

        def replacer(match: re.Match):
            var_name = match.group(1)
            default = match.group(2)

            value = self._get_variable(var_name)

            if value:
                return str(Sanitize(value, parse_mode=parse_mode))
            elif default:
                return str(default)
            else:
                return match.group(0)

        return pattern.sub(replacer, template_str)

    # ----------------------------------------------------------------------------
    # Other
    # ----------------------------------------------------------------------------

    def _get_next_scene_name(self):
        if not self._next_order:
            raise ValueError("cannot use Next button: order is not defined")

        for item in self.history[::-1]:
            if item not in self._next_order:
                continue

            index = self._next_order.index(item)

            # check that next index exists
            if index + 1 >= len(self._next_order):
                raise IndexError("next_order index out of range: no next scene defined")

            return self._next_order[index + 1]

        raise ValueError("cannot determine next scene: no matching history entry")