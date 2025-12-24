# Copyright (c) 2025 Ving Studio, Romashka
# Licensed under the MIT License. See LICENSE file for full terms.

import re
import json
from typing import NoReturn

import telekit
from telekit.styles import Sanitize
from . import parser

from ..logger import logger
library = logger.library

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

    script_data: dict | None = None
    script_analyzed: bool = False

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
        cls.script_analyzed = False

        with open(path, "r", encoding=encoding) as f:
            content = f.read()
            cls.analyze_source(content)

        cls.prepare_script()

    @classmethod
    def analyze_source(cls, script: str) -> None | NoReturn:
        """
        Analyze an script from string and store parsed data in the class.

        Raises an error if there are syntax errors or analyzer warnings.
        
        :param script: Telekit DSL script
        :type script: str
        """
        cls.script_analyzed = False
        cls.script_data = parser.analyze(script)
        cls.prepare_script()

    @classmethod
    def display_script_data(cls):
        """
        Prints the semantic model of the script to the console.
        """
        if not cls.script_data:
            print("display_script_data: Script data not loaded. Call `analyze_file` or `analyze_source` first.")
            return

        print(
            json.dumps(
                cls.script_data,
                indent=4,
                ensure_ascii=False
            )
        )

    @classmethod
    def prepare_script(cls):
        """
        Prepares the script; raises an error if the script data is not loaded or invalid
        """
        cls.script_analyzed = False

        if not cls.script_data:
            raise ValueError("Script data not loaded. Call `analyze_file` or `analyze_source` first.")

        # scenes
        if "scenes" not in cls.script_data:
            missing("scenes")
        if not isinstance(cls.script_data["scenes"], dict):
            raise TypeError("'scenes' should be a dictionary.")
        cls.scenes: dict[str, dict] = cls.script_data["scenes"]

        # scene order
        if "order" not in cls.script_data:
            missing("order")
        if not isinstance(cls.script_data["order"], list):
            raise TypeError("'order' should be a list of strings.")
        cls.scene_order: list[str] = cls.script_data["order"]

        # config
        if "config" not in cls.script_data:
            missing("config")
        if not isinstance(cls.script_data["config"], dict):
            raise TypeError("'config' should be a dictionary.")
        cls.config = cls.script_data["config"]

        # next order
        cls.next_order: list[str] | None = cls.config.get("next_order")
        if not isinstance(cls.next_order, list):
            raise TypeError("'next_order' config should be a list of strings.")
        
        # timeout
        cls.timeout_time = cls.config.get("timeout_time", 0)

        if not cls.timeout_time:
            library.warning(
                "No timeout configured for this DSL script. "
                "It is recommended to add a timeout to automatically clear callbacks "
                "after a period of inactivity.\n\n"
                "Example:\n\n"
                "$ timeout {\n"
                "    time = 30; // seconds\n"
                "}\n\n"
            )

        # end
        cls.script_analyzed = True

    # ----------------------------------------------------------------------------
    # Instance Attributes
    # ----------------------------------------------------------------------------

    def start_script(self) -> None | NoReturn:
        """
        Starts the script; raises an error if the script has not been analyzed
        """
        # quick check
        if not self.script_analyzed:
            message: str = "start_script: Script is not analyzed yet. Call analyze_file() or analyze_source() before starting it."
            library.error(message)
            self.chain.sender.pyerror(RuntimeError(message))
            return
        
        # initialize history
        self.history: list[str] = []

        # localize attributes
        self.config = self.config
        self.scenes = self.scenes
        self.scene_order = self.scene_order
        self.next_order = self.next_order

        # set timeout
        if isinstance(self.timeout_time, int):
            self.chain.set_timeout(self._on_timeout, self.timeout_time)
        self.chain.set_remove_timeout(False)

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
        self.chain.set_timeout(self._on_timeout, self.timeout_time)
        self.prepare_scene(self.history.pop())()

    # ----------------------------------------------------------------------------
    # Variables
    # ----------------------------------------------------------------------------

    def get_variable(self, name: str) -> str | None:
        """
        Return a custom variable value for use in Telekit DSL scripts.

        Telekit DSL supports **template variables** using double curly braces: `{{variable}}`.

        This method is called by the DSL engine when rendering template variables.
        If you return a string, that value will be used in place of the variable 
        `{{name}}` in the DSL script. If you return None, the engine will fallback 
        to the built-in variables. If the variable is not found there either, the 
        default value (if provided using the `:` syntax) will be used.

        :param name: The name of the variable to retrieve.
        :type name: str
        :return: The value of the variable to use in the DSL, or None to fallback 
                to built-in variables/defaults.
        :rtype: str | None
        """
        return

    def _get_variable(self, name: str) -> str | None:
        value = self.get_variable(name)

        if isinstance(value, str):
            return value

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
        if not self.next_order:
            raise ValueError("cannot use Next button: order is not defined")

        for item in self.history[::-1]:
            if item not in self.next_order:
                continue

            index = self.next_order.index(item)

            # check that next index exists
            if index + 1 >= len(self.next_order):
                raise IndexError("next_order index out of range: no next scene defined")

            return self.next_order[index + 1]

        raise ValueError("cannot determine next scene: no matching history entry")
    
def missing(name: str):
    raise KeyError(f"Missing '{name}' key in script data.")
