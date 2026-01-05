# Copyright (c) 2025 Ving Studio, Romashka
# Licensed under the MIT License. See LICENSE file for full terms.

import re
import json
from typing import NoReturn, Callable, Any

import telekit
from telekit.styles import Sanitize
from . import parser

from .._logger import logger
library = logger.library

MAGIC_SCENES = parser.MAGIC_SCENES

class ScriptData:
    def __init__(self, config: dict, scenes: dict[str, dict], scene_order: list[str], next_order: list[str], timeout_time: int | Any):
        self.config      = config
        self.scenes      = scenes
        self.scene_order = scene_order
        self.next_order  = next_order
        self.entry: str | None = None


        if timeout_time and isinstance(timeout_time, int):
            self.timeout_time = timeout_time
        else:
            self.timeout_time = None

        self._button_ref_count: dict[str, int] = {}
        self._scene_ref_count:  dict[str, int] = {}

        self.history: list[str] = []

        # keep track of which *_once hooks have already been executed
        self.executed_once_hooks: set[str] = set()
        
    def get_button_ref_count(self, name: str) -> int:
        if name in self._button_ref_count:
            return self._button_ref_count[name]

        ref_count = 0

        for scene in self.scenes.values():
            for button in scene["buttons"].values():
                if button.get("type") == "scene" and button.get("target") == name:
                    ref_count += 1

        self._button_ref_count[name] = ref_count
        return ref_count
    
    def get_scene_ref_count(self, name: str) -> int:
        if name in self._scene_ref_count:
            return self._scene_ref_count[name]

        ref_count = 0

        for scene in self.scenes.values():
            has_ref = False

            for button in scene["buttons"].values():
                if button.get("type") == "scene" and button.get("target") == name:
                    has_ref = True
                    break

            if has_ref:
                ref_count += 1

        self._scene_ref_count[name] = ref_count
        return ref_count
    
    def get_current_scene_name(self) -> str:
        if self.history:
            return self.history[-1]
        else:
            return "main"
        
    def get_prev_scene_name(self) -> str:
        if len(self.history) >= 2:
            return self.history[-2]
        else:
            return "main"
        
    def get_current_scene(self) -> dict:
        return self.scenes[self.get_current_scene_name()]
    
    def get_prev_scene(self) -> dict:
        return self.scenes[self.get_prev_scene_name()]

    @classmethod
    def script_data_factory(cls, config: dict, scenes: dict[str, dict], scene_order: list[str], next_order: list[str], timeout_time: int):
        def create(*args) -> ScriptData:
            return cls(config, scenes, scene_order, next_order, timeout_time)
        return create

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

    raw_script_data: dict | None = None
    script_data_factory: Callable[..., ScriptData] | None = None

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
        cls.script_data_factory = None
        cls.raw_script_data = parser.analyze(script)
        cls.prepare_script()

    @classmethod
    def display_script_data(cls):
        """
        Prints the semantic model of the script to the console.
        """
        if not cls.raw_script_data:
            print("display_script_data: Script data not loaded. Call `analyze_file` or `analyze_source` first.")
            return

        print(
            json.dumps(
                cls.raw_script_data,
                indent=4,
                ensure_ascii=False
            )
        )

    @classmethod
    def prepare_script(cls):
        """
        Prepares the script; raises an error if the script data is not loaded or invalid
        """
        cls.script_data_factory = None

        if not cls.raw_script_data:
            raise ValueError("Script data not loaded. Call `analyze_file` or `analyze_source` first.")

        # scenes
        if "scenes" not in cls.raw_script_data:
            missing("scenes")
        if not isinstance(cls.raw_script_data["scenes"], dict):
            raise TypeError("'scenes' should be a dictionary.")
        scenes: dict[str, dict] = cls.raw_script_data["scenes"]

        # scene order
        if "order" not in cls.raw_script_data:
            missing("order")
        if not isinstance(cls.raw_script_data["order"], list):
            raise TypeError("'order' should be a list of strings.")
        scene_order: list[str] = cls.raw_script_data["order"]

        # config
        if "config" not in cls.raw_script_data:
            missing("config")
        if not isinstance(cls.raw_script_data["config"], dict):
            raise TypeError("'config' should be a dictionary.")
        config = cls.raw_script_data["config"]

        # next order
        next_order: list[str] | None = config.get("next_order")
        if not isinstance(next_order, list):
            raise TypeError("'next_order' config should be a list of strings.")
        
        # timeout
        timeout_time = config.get("timeout_time", 0)

        if not timeout_time:
            library.warning(
                "No timeout configured for this DSL script. "
                "It is recommended to add a timeout to automatically clear callbacks "
                "after a period of inactivity.\n\n"
                "Example:\n\n"
                "$ timeout {\n"
                "    time = 30; // seconds\n"
                "}\n\n" + \
                f"{cls.raw_script_data["source"][:94].strip()}...\n\n" + \
                "Learn more about DSL Timeouts in the GitHub tutorial: https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/13_telekit_dsl_syntax.md#timeout\n"
            )

        # end
        cls.script_data_factory = ScriptData.script_data_factory(
            config, scenes, scene_order, next_order, timeout_time
        )

    # ----------------------------------------------------------------------------
    # Instance Attributes
    # ----------------------------------------------------------------------------

    def start_script(self, initial_scene: str="main") -> None | NoReturn:
        """
        Starts the script; raises an error if the script has not been analyzed
        """
        # quick check
        if not self.script_data_factory:
            message: str = "start_script: Script is not analyzed yet. Call analyze_file() or analyze_source() before starting it."
            library.error(message)
            self.chain.sender.pyerror(RuntimeError(message))
            return

        self.script_data = self.script_data_factory()

        # set timeout
        if self.script_data.timeout_time:
            self.chain.set_timeout(self._on_timeout, self.script_data.timeout_time)
        self.chain.disable_timeout_warnings()
        self.chain.set_remove_timeout(False)

        # start the initial scene
        if initial_scene not in self.script_data.scenes:
            initial_scene = "main"
            
        self.prepare_scene(initial_scene)()
    
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
                        scene_name = self._get_prev_scene_name()
                    case "next":
                        scene_name = self._get_next_scene_name()

            self.script_data.history.append(scene_name)

            # main logic
            scene = self.script_data.scenes[scene_name]

            # handler api
            if "on_enter" in scene:
                self._call_api_methods(scene["on_enter"])
            if "on_enter_once" in scene:
                hook_key = f"{scene_name}.on_enter_once"
                if hook_key not in self.script_data.executed_once_hooks:
                    self._call_api_methods(scene["on_enter_once"])
                    self.script_data.executed_once_hooks.add(hook_key)

            # view
            real_parse_mode: str | None = scene.get("parse_mode")
            parse_mode = real_parse_mode or "html"

            self.chain.sender.set_parse_mode(parse_mode)
            self.chain.sender.set_use_italics(scene.get("use_italics", False))
            self.chain.sender.set_photo(scene.get("image"))

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
            
            # buttons
            keyboard: dict = {}

            for button_label, button_attrs in scene.get("buttons", {}).items():
                label = self._parse_variables(button_label)
                target = button_attrs["target"]

                match button_attrs["type"]:
                    case "scene":
                        keyboard[label] = self.prepare_scene(target)
                    case "suggest":
                        keyboard[label] = self._prepare_suggestion(*target)
                    case "redirect":
                        keyboard[label] = self._prepare_redirect(target)
                    case "handoff":
                        keyboard[label] = self._prepare_handoff(target)
                    case "link":
                        keyboard[label] = target

            self.chain.set_inline_keyboard(keyboard, scene.get("row_width", 1))

            # entries
            if scene.get("entries") or scene.get("_default_entry_target"):
                self.chain.entry_text(self._filter_entry, True)(self._handle_entry)

            if "on_exit" in scene:
                self._call_api_methods(scene["on_exit"])

            self.script_data.entry = None

            if not scene.get("_has_back_option"):
                self.script_data.history.clear()
                self.script_data.history.append(scene_name)

            self.chain.edit()

        return render
    
    # ----------------------------------------------------------------------------
    # Redirect Logic
    # ----------------------------------------------------------------------------

    def _prepare_handoff(self, target: str):
        def render():
            self.handoff(target).handle()

        return render
    
    def _prepare_redirect(self, target: str):
        def render():
            self.simulate_user_message(target)

        return render
    
    # ----------------------------------------------------------------------------
    # Entry Logic
    # ----------------------------------------------------------------------------

    def _prepare_suggestion(self, target: str, text: str):
        def render():
            self.script_data.entry = text
            self.prepare_scene(target)()

        return render

    def _filter_entry(self, _, text: str):
        scene = self.script_data.get_current_scene()

        if text in scene.get("entries", {}): 
            return True
        if "_default_entry_target" in scene:
            return True
        
        return False

    def _handle_entry(self, _, text: str):
        scene_name = self.script_data.get_current_scene_name()
        scene = self.script_data.scenes[scene_name]

        self.script_data.entry = text

        entries = scene.get("entries", {})
        choosed_scene = entries.get(text)

        if not choosed_scene:
            choosed_scene = scene.get("_default_entry_target", "main")

        self.prepare_scene(choosed_scene)()
    
    # ----------------------------------------------------------------------------
    # Timeout Logic
    # ----------------------------------------------------------------------------

    def _on_timeout(self):
        scene = self.script_data.get_current_scene()
        if "on_timeout" in scene:
            self._call_api_methods(scene["on_timeout"])

        message = self.script_data.config.get("timeout_message", "👋 Are you still there?")
        message = self.chain.sender.styles.no_sanitize(message)
        label   = self.script_data.config.get("timeout_label", "Yes, I'm here ✓")

        self.chain.set_timeout(None, 7)
        self.chain.sender.add_message("\n\n", self.chain.sender.styles.bold(message))
        self.chain.set_inline_keyboard({label: self._continue})

        self.chain.edit()

    def _continue(self):
        if self.script_data.timeout_time:
            self.chain.set_timeout(self._on_timeout, self.script_data.timeout_time)
        else:
            self.chain.remove_timeout()
        self.prepare_scene(self.script_data.history.pop())()

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
        value = self._find_variable(name)

        if isinstance(value, str):
            return value
        
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
            case "scene_ref_count":
                return str(self.script_data.get_scene_ref_count(self.script_data.get_current_scene_name()))
            case "button_ref_count":
                return str(self.script_data.get_button_ref_count(self.script_data.get_current_scene_name()))
            case "prev_scene_name":
                return self.script_data.get_prev_scene_name()
            case "prev_scene_title":
                return self.script_data.get_prev_scene().get("title")
            case "prev_scene_message":
                return self.script_data.get_prev_scene().get("title")
            case "scene_name":
                return self.script_data.get_current_scene_name()
            case "scene_title":
                return self.script_data.get_current_scene().get("title")
            case "scene_message":
                return self.script_data.get_current_scene().get("message")
            case "entry":
                return self.script_data.entry if isinstance(self.script_data.entry, str) else None
            # case "next_scene_name": # TODO: check it in Analyzer
            #     return self._get_next_scene_name()
            # case "next_scene_title":
            #     return str(self.script_data.scenes[self._get_next_scene_name()]["title"])
            # case "next_scene_message":
            #     return str(self.script_data.scenes[self._get_next_scene_name()]["message"])
            case _:
                return
            
    def _find_variable(self, name: str) -> str | None:
        value = self.script_data.config.get(f"vars_{name}")
        return None if value is None else str(value)

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

    def _fail(self, message: str, exception: type[Exception]=Exception):
        self.chain.sender.error("🤷 Something went wrong...", message)
        library.error(message)
        return exception(message)

    def _get_next_scene_name(self):
        if not self.script_data.next_order:
            raise self._fail("Cannot use 'next' button: order is not defined", ValueError)

        for item in self.script_data.history[::-1]:
            if item not in self.script_data.next_order:
                continue

            index = self.script_data.next_order.index(item)

            # check that next index exists
            if index + 1 >= len(self.script_data.next_order):
                raise self._fail("'next_order' index out of range: no next scene defined", IndexError)

            return self.script_data.next_order[index + 1]

        raise self._fail("Cannot determine next scene: no matching history entry", ValueError)
    
    def _get_prev_scene_name(self):
        if self.script_data.history:
            self.script_data.history.pop() # remove current
        if self.script_data.history:
            return self.script_data.history.pop() # get and remove previous
        else:
            return "main" # (impossible)
        
    def _call_api_methods(self, api_calls: list[tuple[str, None | list[Any]]]):
        """
        Execute API methods from the list. Each element is [method_name, args]:
            args can be a list or None if no arguments.
        """
        for name, args in api_calls:
            if not hasattr(self, name):
                raise self._fail(f"Handler has no method named '{name}'")

            method = getattr(self, name)

            # ensure callable
            if not callable(method):
                raise self._fail(f"Attribute '{name}' exists but is not callable")

            # call with args
            try:
                if args is None:
                    method()
                else:
                    args = [
                        self._parse_variables(arg) if isinstance(arg, str) else arg
                        for arg in args
                    ]
                    method(*args)
            except TypeError as e:
                raise self._fail(f"Error calling '{name}' with args {args}: {e}")
            except Exception as e:
                raise self._fail(f"Unexpected error in '{name}': {e}")
    
def missing(name: str):
    message: str = f"Missing '{name}' key in script data."
    library.error(message)
    raise KeyError(message)

"""
// ----------------------------------------------------
// Script Data Structure (JSON)
// ----------------------------------------------------

{
    "config": {
        "timeout_time": 20,
        "next_order": [
            "main",
            "question_1",
            "question_2",
            "question_3",
            "question_4",
            "question_5",
            "question_6",
            "question_7",
            "question_8",
            "question_9",
            "question_10"
        ]
    },
    "scenes": {
        "main": {
            "name": "main",
            "title": "🎉 Fun Facts Quiz",
            "message": "Hello, {{first_name}}. Test your knowledge with 10 fun questions!",
            "image": null,
            "use_italics": false,
            "parse_mode": null,
            "buttons": {
                "Start Quiz": {
                    "type": "scene",
                    "target": "next"
                }
            },
            "row_width": 1
        },
        "question_1": {
            "name": "question_1",
            "title": "🐶 Question 1",
            "message": "Which animal is the fastest on land?",
            "image": null,
            "use_italics": false,
            "parse_mode": null,
            "buttons": {
                "Elephant": "_lose",
                "Cheetah": "next",
                "Horse": "_lose",
                "Lion": "_lose"
            },
            "row_width": 1
        },
        "question_2": {
            "name": "question_2",
            "title": "🍫 Question 2",
            "message": "From which product is chocolate made?",
            "image": null,
            "use_italics": false,
            "parse_mode": null,
            "buttons": {
                "Cocoa powder": "_lose",
                "Cocoa beans": "next",
                "Cocoa butter": "_lose",
                "Cocoa drink": "_lose"
            },
            "row_width": 1
        },
        "question_3": {
            "name": "question_3",
            "title": "🌌 Question 3",
            "message": "Which planet is known for its prominent rings?",
            "image": null,
            "use_italics": false,
            "parse_mode": null,
            "buttons": {
                "Jupiter": "_lose",
                "Saturn": "next",
                "Mars": "_lose",
                "Neptune": "_lose"
            },
            "row_width": 1
        },
        "question_4": {
            "name": "question_4",
            "title": "🦎 Question 4",
            "message": "Which animal can change the color of its skin?",
            "image": null,
            "use_italics": false,
            "parse_mode": null,
            "buttons": {
                "Chameleon": "next",
                "Crocodile": "_lose",
                "Turtle": "_lose",
                "Snake": "_lose"
            },
            "row_width": 1
        },
        "question_5": {
            "name": "question_5",
            "title": "🍌 Question 5",
            "message": "Which vitamin is most abundant in a banana?",
            "image": null,
            "use_italics": false,
            "parse_mode": null,
            "buttons": {
                "Vitamin C": "_lose",
                "Vitamin B6": "next",
                "Vitamin D": "_lose",
                "Vitamin A": "_lose"
            },
            "row_width": 1
        },
        "question_6": {
            "name": "question_6",
            "title": "🎨 Question 6",
            "message": "Which artist painted the 'Mona Lisa'?",
            "image": null,
            "use_italics": false,
            "parse_mode": null,
            "buttons": {
                "Leonardo da Vinci": "next",
                "Pablo Picasso": "_lose",
                "Vincent van Gogh": "_lose",
                "Michelangelo": "_lose"
            },
            "row_width": 1
        },
        "question_7": {
            "name": "question_7",
            "title": "🎵 Question 7",
            "message": "Which musical instrument has 88 keys?",
            "image": null,
            "use_italics": false,
            "parse_mode": null,
            "buttons": {
                "Guitar": "_lose",
                "Harmonica": "_lose",
                "Piano": "next",
                "Saxophone": "_lose"
            },
            "row_width": 1
        },
        "question_8": {
            "name": "question_8",
            "title": "🧩 Question 8",
            "message": "How many faces does a cube have?",
            "image": null,
            "use_italics": false,
            "parse_mode": null,
            "buttons": {
                "6": "next",
                "8": "_lose",
                "12": "_lose"
            },
            "row_width": 1
        },
        "question_9": {
            "name": "question_9",
            "title": "🌊 Question 9",
            "message": "Which is the largest ocean on Earth?",
            "image": null,
            "use_italics": false,
            "parse_mode": null,
            "buttons": {
                "Pacific Ocean": "next",
                "Atlantic Ocean": "_lose",
                "Indian Ocean": "_lose",
                "Arctic Ocean": "_lose"
            },
            "row_width": 1
        },
        "question_10": {
            "name": "question_10",
            "title": "🍕 Question 10",
            "message": "Which country is pizza originally from?",
            "image": null,
            "use_italics": false,
            "parse_mode": null,
            "buttons": {
                "France": "_lose",
                "Italy": "_end",
                "Spain": "_lose",
                "USA": "_lose"
            },
            "row_width": 1
        },
        "_lose": {
            "name": "_lose",
            "title": "❌ Wrong Answer!",
            "message": "Oops! {{random_lose_phrase}}",
            "image": null,
            "use_italics": false,
            "parse_mode": null,
            "buttons": {
                "« Retry": "back"
            },
            "row_width": 1
        },
        "_end": {
            "name": "_end",
            "title": "🎉 Quiz Complete!",
            "message": "Congratulations! You've completed the Fun Facts Quiz! 🌟\n\nWant to try again?",
            "image": null,
            "use_italics": false,
            "parse_mode": null,
            "buttons": {
                "↺ Restart Quiz": "main"
            },
            "row_width": 1
        }
    },
    "source": "...",
    "order": [
        "main",
        "question_1",
        "question_2",
        "question_3",
        "question_4",
        "question_5",
        "question_6",
        "question_7",
        "question_8",
        "question_9",
        "question_10",
        "_lose",
        "_end"
    ]
}

"""