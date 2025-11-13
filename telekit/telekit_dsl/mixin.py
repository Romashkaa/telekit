# Copyright (c) 2025 Ving Studio, Romashka
# Licensed under the MIT License. See LICENSE file for full terms.

from . import parser

import telekit

from typing import NoReturn

class TelekitDSLMixin(telekit.Handler):

    """
    TelekitDSLMixin — Mixin for creating interactive FAQ or guide flows inside a Telekit handler.

    This class allows you to:
    - Load guide data from a Telekit DSL file or string.
    - Automatically handle user navigation between scenes (including "back" functionality).
    - Render scenes with inline keyboards and formatting.

    Requirements:
    - The handler using this mixin must have `self.chain` available (Telekit Chain instance).
    - Must call `analyze_file()` or `analyze_source()` before `start_script()`.

    ## Usage:
    ```
        import telebot.types
        import telekit

        class MyFAQHandler(telekit.TelekitDSL.Mixin):
            @classmethod
            def init_handler(cls) -> None:
                @cls.message_handler(commands=["faq"])
                def handler(message: telebot.types.Message) -> None:
                    cls(message).start_script()

                cls.analyze_source(guide)

            # If you want to add your own bit of logic:

            # def start_script(self):
            #     # Your logic
            #     super().start_script()
    ```

    Notes:
    - Scenes support backtracking via a 'back' button.
    - All chain rendering is handled automatically; developers only provide scene data.
    """

    data: dict | None = None

    @classmethod
    def analyze_file(cls, path: str, encoding: str="utf-8")  -> None | NoReturn:
        """Analyze an FML file and store parsed data in the class. (any file extension)"""
        with open(path, "r", encoding=encoding) as f:
            content = f.read()
            cls.analyze_source(content)

    @classmethod
    def analyze_source(cls, source: str) -> None | NoReturn:
        """Analyze FML source string and store parsed data."""
        cls.data = parser.analyze(source)

    def start_script(self) -> None | NoReturn:
        """Start the guide; raises an error if data is not loaded."""
        if not self.data:
            raise RuntimeError("Guide data not loaded. Call `analyze_file` or `analyze_source` first.")
        
        # initialize history
        self.history = []

        # check if 'scenes' exists and is a dictionary
        if "scenes" not in self.data:
            raise KeyError("Missing 'scenes' key in guide data.")
        if not isinstance(self.data["scenes"], dict):
            raise TypeError("'scenes' should be a dictionary.")
        self.scenes = self.data["scenes"]

        # check if 'config' exists and is a dictionary
        if "config" not in self.data:
            raise KeyError("Missing 'config' key in guide data.")
        if not isinstance(self.data["config"], dict):
            raise TypeError("'config' should be a dictionary.")
        self.config = self.data["config"]

        timeout = self.config.get("timeout", 0)
        if isinstance(timeout, int):
            self.chain.set_timeout(self.prepare_scene("timeout"), timeout)
        self.chain.set_remove_timeout(False)

        # start the main scene
        self.prepare_scene("main")()

    def prepare_scene(self, _scene_name: str):
        """Prepare page"""
        def render():
            # magic scenes logic

            scene_name = _scene_name

            match scene_name:
                case "back":
                    if self.history:
                        self.history.pop() # current
                    if self.history:
                        scene_name = self.history.pop()
                case "timeout":
                    self.chain.remove_timeout()
            
            self.history.append(scene_name)

            # main logic
            scene = self.scenes[scene_name]

            self.chain.sender.set_parse_mode(scene.get("parse_mode", "HTML"))
            self.chain.sender.set_use_italics(scene.get("use_italics", False))

            self.chain.sender.set_title(scene.get("title", "[ Title ]"))
            self.chain.sender.set_message(scene.get("message", "[ Message ]"))
            self.chain.sender.set_photo(scene.get("image", None))

            # keyboard
            keyboard: dict = {}

            for btn_label, btn_scene in scene.get("buttons", {}).items():
                keyboard[btn_label] = self.prepare_scene(btn_scene)

            self.chain.set_inline_keyboard(keyboard, scene.get("row_width", 1))
            self.chain.edit()

        return render
