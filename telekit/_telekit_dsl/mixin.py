# Copyright (c) 2025 Ving Studio, Romashka
# Licensed under the MIT License. See LICENSE file for full terms.

import re
import json
from typing import NoReturn, Callable, Any
import jinja2

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

        self.static_vars = self._filter_configs("vars_")

    def _filter_configs(self, key_prefix: str):
        prefix_len = len(key_prefix)
        filtered_items = filter(lambda kv: kv[0].startswith(key_prefix), self.config.items())
        return {k[prefix_len:]: v for k, v in filtered_items}
        
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
    
    def get_template_engine(self, scene_name: str | None=None) -> str:
        if scene_name is None:
            scene = self.get_current_scene()
        else:
            scene = self.scenes[scene_name]
        return scene.get("template") or self.config.get("template", "vars")
    
    def get_prev_scene(self) -> dict:
        return self.scenes[self.get_prev_scene_name()]
    
    def get_next_scene_name(self) -> str | None:
        if not self.next_order:
            return None
        for item in self.history[::-1]:
            if item not in self.next_order:
                continue
            index = self.next_order.index(item)
            # check that next index exists
            if index + 1 >= len(self.next_order):
                return None
            return self.next_order[index + 1]
        return None
    
    def get_next_scene(self) -> dict:
        return self.scenes[self.get_next_scene_name() or "main"]
    
    # -----------------------------------------------------------------
    # Internal Logic
    # -----------------------------------------------------------------

    def _pop_prev_scene_name(self) -> str | None:
        if self.history:
            self.history.pop() # remove current
        if self.history:
            return self.history.pop() # get and remove previous

    @classmethod
    def _script_data_factory(cls, executable_model: dict[str, Any]):
        script_data = cls._extract_script_data(executable_model)

        def create(*_) -> ScriptData:
            return cls(*script_data)
        
        return create
    
    @classmethod
    def _extract_script_data(cls, executable_model: dict[str, Any]):
        # scenes
        if "scenes" not in executable_model:
            missing("scenes")
        if not isinstance(executable_model["scenes"], dict):
            raise TypeError("'scenes' should be a dictionary.")
        scenes: dict[str, dict] = executable_model["scenes"]

        # scene order
        if "order" not in executable_model:
            missing("order")
        if not isinstance(executable_model["order"], list):
            raise TypeError("'order' should be a list of strings.")
        scene_order: list[str] = executable_model["order"]

        # config
        if "config" not in executable_model:
            missing("config")
        if not isinstance(executable_model["config"], dict):
            raise TypeError("'config' should be a dictionary.")
        config = executable_model["config"]

        # next order
        next_order: list[str] | None = config.get("next_order")
        if not isinstance(next_order, list):
            raise TypeError("'next_order' config should be a list of strings.")
        
        # timeout
        timeout_time = config.get("timeout_time", 300) # 5min

        return config, scenes, scene_order, next_order, timeout_time

# -----------------------------------------------------------------
# Mixin
# -----------------------------------------------------------------

class TelekitDSLMixin(telekit.Handler):
    """
    TelekitDSLMixin — Mixin for creating interactive FAQ inside a Telekit handler.

    This class allows you to:
    - Load script data from a Telekit DSL file or string.
    - Automatically handle user navigation between scenes.
    - Render scenes with inline keyboards and formatting.

    Requirements:
    - The handler using this mixin must call `analyze_file()` or `analyze_source()` before `start_script()`.

    [Learn more on GitHub](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/11_telekit_dsl.md)

    ## Usage:
    ```
        import telekit

        class MyFAQHandler(telekit.TelekitDSL.Mixin):
            @classmethod
            def init_handler(cls) -> None:
                cls.analyze_source(script)
                cls.on.command("faq").invoke(cls.start_script)
    ```

    [Learn more on GitHub](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/11_telekit_dsl.md) · Tutorial
    """

    # class attributes
    _script_data_factory: Callable[..., ScriptData]
    executable_model: dict
    jinja_env: jinja2.Environment

    # instance attributes
    jinja_context: dict[str, Any]

    # ----------------------------------------------------------------------------
    # Class Attributes
    # ----------------------------------------------------------------------------

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
        cls.executable_model = parser.analyze(script)
        cls._prepare_script(cls.executable_model)

    @classmethod
    def display_script_data(cls):
        """
        Prints the semantic model of the script to the console.
        """
        if not hasattr(cls, "executable_model"):
            print("display_script_data: Script data not loaded. Call `analyze_file` or `analyze_source` first.")
            return

        print(
            json.dumps(
                cls.executable_model,
                indent=4,
                ensure_ascii=False
            )
        )

    @classmethod
    def set_jinja_env(cls, env: jinja2.Environment | None=None):
        """
        Sets the Jinja Environment for the handler **class**.

        - If `env` is None, creates a default Environment with `autoescape` disabled.
        - Otherwise, uses the provided custom Environment.
        - Registers custom escape filters for Markdown (`e_md`) and HTML (`e_html`).
        - The Environment is shared across all instances of this class.
        """
        if env is None:
            cls.jinja_env = jinja2.Environment(autoescape=False)
        else:
            cls.jinja_env = env

        cls.jinja_env.filters["e_md"] = JinjaFilters.escape_md
        cls.jinja_env.filters["e_html"] = JinjaFilters.escape_html

    @classmethod
    def _prepare_script(cls, executable_model: dict[str, Any]):
        """
        Prepares the script; raises an error if the script data is not loaded or invalid
        """

        if not executable_model:
            raise ValueError("Script data not loaded. Call `analyze_file` or `analyze_source` first.")

        # update script data factory
        cls._script_data_factory = ScriptData._script_data_factory(executable_model)

        # set default jinja environment
        if not hasattr(cls, "jinja_env"):
            cls.set_jinja_env()
        
    # ----------------------------------------------------------------------------
    # Instance Methods
    # ----------------------------------------------------------------------------

    def start_script(self, initial_scene: str="main") -> None | NoReturn:
        """
        Starts the script; raises an error if the script has not been analyzed
        """
        # quick check
        if not hasattr(self, "_script_data_factory"):
            message: str = "start_script: Script is not analyzed yet. Call analyze_file() or analyze_source() before starting it."
            library.error(message)
            self.chain.sender.pyerror(RuntimeError(message))
            return

        self.script_data = self._script_data_factory()

        # set timeout
        if self.script_data.timeout_time:
            self.chain.set_timeout(self._on_timeout, self.script_data.timeout_time)
        self.chain.disable_timeout_warnings()
        self.chain.set_remove_timeout(False)

        # set default jinja context
        if not hasattr(self, "jinja_context"):
            self.set_jinja_context()

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
                        scene_name = self.script_data._pop_prev_scene_name() or "main"
                    case "next":
                        scene_name = self.script_data.get_next_scene_name() or "main"

            # main logic
            self.script_data.history.append(scene_name)
            scene = self.script_data.scenes[scene_name]

            # template engine
            template_engine: str = self.script_data.get_template_engine()

            # "on enter" handler api
            if "on_enter" in scene:
                self._call_api_methods(scene["on_enter"], template_engine)
            if "on_enter_once" in scene:
                hook_key = f"{scene_name}.on_enter_once"
                if hook_key not in self.script_data.executed_once_hooks:
                    self._call_api_methods(scene["on_enter_once"], template_engine)
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
                title = self._parse_template(title, real_parse_mode, template_engine)
                message = self._parse_template(message, real_parse_mode, template_engine)

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
                label = self._parse_template(button_label, template_engine=template_engine)
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

            # "on exit" handler api
            if "on_exit" in scene:
                self._call_api_methods(scene["on_exit"], template_engine)

            # remove the garbage
            self.script_data.entry = None

            if not scene.get("_has_back_option"):
                self.script_data.history.clear()
                self.script_data.history.append(scene_name)

            # send the message
            self.chain.edit()

        return render
    
    # ----------------------------------------------------------------------------
    # Jinja & Vars API
    # ----------------------------------------------------------------------------
    
    def set_jinja_context(self, context: dict[str, Any] | None=None, **kwcontext):
        """
        Sets the Jinja rendering context for the current handler instance.

        - If `context` dict is provided, it is merged with keyword arguments.
        - Keyword arguments always override values from `context` on key conflicts.
        - If `context` is None, only keyword arguments are used.

        This context is later passed to Jinja templates during rendering.

        ---

        If keys conflict, values provided by this method override the default ones:
        - the built-in `handler` variable
        - variables defined in the DSL (`$ vars { ... }`)
        """
        if context:
            self.jinja_context = context | kwcontext
        else:
            self.jinja_context = kwcontext

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
        # "on timeout" handler api
        scene = self.script_data.get_current_scene()
        template_engine: str = self.script_data.get_template_engine()

        if "on_timeout" in scene:
            self._call_api_methods(scene["on_timeout"], template_engine)

        # timeout logic
        message = self.script_data.config.get("timeout_message", "👋 Are you still there?")
        message = self.chain.sender.styles.no_sanitize(message)
        label   = self.script_data.config.get("timeout_label", "Yes, I'm here ✓")

        self.chain.set_timeout(None, 7)
        self.chain.sender.add_message("\n\n", self.chain.sender.styles.bold(message))
        self.chain.set_inline_keyboard({label: self._on_continue})

        # edit the message
        self.chain.edit()

    def _on_continue(self):
        if self.script_data.timeout_time:
            self.chain.set_timeout(self._on_timeout, self.script_data.timeout_time)
        else:
            self.chain.remove_timeout()

        self.prepare_scene(self.script_data.history.pop())()

    # ----------------------------------------------------------------------------
    # Template Logic
    # ----------------------------------------------------------------------------

    def _parse_template(self, template_str: str, parse_mode: str | None=None, template_engine: str="plain"):
        match template_engine:
            case "vars":
                return self._parse_variables(template_str, parse_mode)
            case "jinja":
                return self._parse_jinja_template(template_str)
            case _:
                return template_str

    def _get_jinja_context(self) -> dict[str, Any]:
        return {"handler": self} | self.script_data.static_vars | self.jinja_context
            
    def _parse_jinja_template(self, template_str: str):
        context = self._get_jinja_context()

        try:
            template = self.jinja_env.from_string(template_str)
            rendered = template.render(context)
        except Exception as exception:
            raise self._fail(f"Jinja Error: {exception}")

        return rendered
    
    def _get_variable(self, name: str) -> str | None:
        value = self._get_static_var(name)

        if isinstance(value, str):
            return value
        
        value = self.get_variable(name)

        if isinstance(value, str):
            return value
        
        value =  self._get_default_var(name)

        if isinstance(value, str):
            return value
        
    def _get_static_var(self, name: str) -> str | None:
        value = self.script_data.static_vars.get(name)
        return None if value is None else str(value)
    
    def _get_default_var(self, name: str):
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
                return self.script_data.get_prev_scene().get("message")
            case "scene_name":
                return self.script_data.get_current_scene_name()
            case "scene_title":
                return self.script_data.get_current_scene().get("title")
            case "scene_message":
                return self.script_data.get_current_scene().get("message")
            case "next_scene_name":
                return self.script_data.get_next_scene_name()
            case "next_scene_title":
                return self.script_data.get_next_scene().get("title")
            case "next_scene_message":
                return self.script_data.get_next_scene().get("message")
            case "entry":
                return self.script_data.entry
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

    def _fail(self, message: str, exception: type[Exception]=Exception):
        self.chain.sender.error("🤷 Something went wrong...", message)
        library.error(message)
        return exception(message)
        
    def _call_api_methods(self, api_calls: list[tuple[str, None | list[Any]]], template_engine: str):
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
                        self._parse_template(arg, template_engine=template_engine) if isinstance(arg, str) else arg
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

class JinjaFilters:
    @staticmethod
    def escape_md(value):
        if value is None:
            return ""
        return str(Sanitize(str(value), parse_mode="markdown"))

    @staticmethod
    def escape_html(value):
        if value is None:
            return ""
        return str(Sanitize(str(value), parse_mode="html"))

# ----------------------------------------------------
# Script Data Structure (JSON)
# ----------------------------------------------------
#
# See on GitHub: https://github.com/Romashkaa/telekit/blob/main/docs/documentation/dsl_analyzer_output.md
