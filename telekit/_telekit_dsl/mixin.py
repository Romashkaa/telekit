# 
# Copyright (C) 2026 Romashka
# 
# This file is part of Telekit.
# 
# Telekit is free software: you can redistribute it and/or modify it 
# under the terms of the GNU General Public License as published by 
# the Free Software Foundation, either version 3 of the License, or 
# (at your option) any later version.
# 
# Telekit is distributed in the hope that it will be useful, 
# but WITHOUT ANY WARRANTY; without even the implied warranty 
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See 
# the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License 
# along with Telekit. If not, see <https://www.gnu.org/licenses/>.
# 

import re
import json
from typing import NoReturn, Callable, Any
import jinja2

import telekit
from telekit.styles import Escape
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
        return self.get_current_scene().get("_next")
    
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
        
    def _trim_list(self, items: list[str], delimiter: str) -> list[str] | None:
        if delimiter not in items:
            return
        last_index: int = len(items) - 1 - items[::-1].index(delimiter)
        return items[:last_index]

    def _rollback_to(self, rollback_point: str) -> None:
        new_history = self._trim_list(self.history, rollback_point)

        if new_history is not None:
            self.history = new_history

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

class DSLHandler(telekit.Handler):
    """
    DSLHandler — Mixin for creating interactive pages, such as FAQs. 
    
    It allows you to describe the message layout, add images, and buttons for navigation between pages in a convenient, structured format that your bot can easily process.

    [Learn more on GitHub](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/11_telekit_dsl.md) · Tutorial

    ### Usage:
    ```
        import telekit

        class MyFAQHandler(telekit.DSLHandler):
            @classmethod
            def init_handler(cls) -> None:
                cls.analyze_file("faq.scr")
                cls.on.command("faq").invoke(cls.start_script)
    ```
    """

    # class attributes
    _script_data_factory: Callable[..., ScriptData]
    executable_model: dict
    _jinja_env: jinja2.Environment

    # instance attributes
    jinja_context: dict[str, Any]

    # ----------------------------------------------------------------------------
    # Class Attributes
    # ----------------------------------------------------------------------------

    @classmethod
    def get_jinja_env(cls):
        return cls._jinja_env

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
        
        cls.analyze_string(content)

    @classmethod
    def analyze_string(cls, script: str) -> None | NoReturn:
        """
        Analyze an script from string and store parsed data in the class.

        Raises an error if there are syntax errors or analyzer warnings.
        
        :param script: Telekit DSL script
        :type script: str
        """
        cls.executable_model = parser.analyze(script)
        cls._prepare_script(cls.executable_model)

    @classmethod
    def display_script_data(cls, path: str | None=None):
        """
        Prints the semantic model of the script to the console.
        """
        if not hasattr(cls, "executable_model"):
            print("display_script_data: Script data not loaded. Call `analyze_file` or `analyze_string` first.")
            return
        
        executable_model = cls.executable_model.copy()
        executable_model.pop("source", None)

        string = json.dumps(
            executable_model,
            indent=4,
            ensure_ascii=False
        )

        if path:
            with open(path, "w") as f:
                f.write(string)
        else:
            print(string)

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
            cls._jinja_env = jinja2.Environment(autoescape=False)
        else:
            cls._jinja_env = env

        cls._jinja_env.filters["e_md"] = JinjaFilters.escape_md
        cls._jinja_env.filters["e_html"] = JinjaFilters.escape_html

    @classmethod
    def _prepare_script(cls, executable_model: dict[str, Any]):
        """
        Prepares the script; raises an error if the script data is not loaded or invalid
        """

        if not executable_model:
            raise ValueError("Script data not loaded. Call `analyze_file` or `analyze_string` first.")

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
            message: str = "start_script: Script is not analyzed yet. Call analyze_file() or analyze_string() before starting it."
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
            
        self._render(initial_scene)
    
    # ----------------------------------------------------------------------------
    # Scene Rendering
    # ----------------------------------------------------------------------------

    def _prepare_scene(self, _scene_name: str):
        """
        Prepare the scene renderer
        """

        def render():
            self._render(_scene_name)

        return render
    
    def _render(self, _scene_name: str):
        scene_name = _scene_name

        # magic scenes logic
        if scene_name in MAGIC_SCENES:
            match scene_name:
                case "back":
                    scene_name = self.script_data._pop_prev_scene_name() or "main"
                case "next":
                    scene_name = self.script_data.get_next_scene_name() or "main"

        # get scene
        self.script_data.history.append(scene_name)
        scene = self.script_data.scenes[scene_name]

        # metadata & parse mode setup
        template_engine: str = self.script_data.get_template_engine()
        real_parse_mode: str | None = scene.get("parse_mode")
        parse_mode = real_parse_mode or "html"

        # main logic
        self._execute_on_enter_hooks(scene, scene_name, template_engine)
        self._render_context(scene, parse_mode)
        self._render_text_content(scene, real_parse_mode, template_engine)
        self._apply_inline_keyboard(scene, template_engine)
        self._apply_entry_handler(scene)
        self._execute_on_exit_hooks(scene, template_engine)
        self._remove_garbage(scene, scene_name)

        # send the message
        self.chain.edit()
    
    def _execute_on_enter_hooks(self, scene: dict, scene_name: str, template_engine: str):
        if "on_enter" in scene:
            self._execute_hook(scene["on_enter"], template_engine)
        if "on_enter_once" in scene:
            hook_key = f"{scene_name}.on_enter_once"
            if hook_key not in self.script_data.executed_once_hooks:
                self._execute_hook(scene["on_enter_once"], template_engine)
                self.script_data.executed_once_hooks.add(hook_key)

    def _render_context(self, scene: dict, parse_mode: str):
        self.chain.sender.set_parse_mode(parse_mode)
        self.chain.sender.set_use_italics(scene.get("use_italics", False))
        self.chain.sender.set_photo(scene.get("image"))
    
    def _render_text_content(self, scene: dict, real_parse_mode: str | None, template_engine: str):
        # get title/message or text
        title = scene.get("title")
        message = scene.get("message")
        text = scene.get("text")

        # process templates
        if title and "{" in title:
            title = self._parse_template(title, real_parse_mode, template_engine)
        if message and "{" in message:
            message = self._parse_template(message, real_parse_mode, template_engine)
        if text and "{" in text:
            text = self._parse_template(text, real_parse_mode, template_engine)

        styles = self.chain.sender.styles
        
        # apply sanitization
        if real_parse_mode:
            # no sanitize
            if title:
                self.chain.sender.set_title(styles.no_sanitize(title))
            if message:
                self.chain.sender.set_message(styles.no_sanitize(message))
            if text:
                self.chain.sender.set_text(styles.no_sanitize(text))
        else:
            # sanitize
            if title:
                self.chain.sender.set_title(styles.sanitize(title))
            if message:
                self.chain.sender.set_message(styles.sanitize(message))
            if text:
                self.chain.sender.set_text(styles.sanitize(text))

    def _apply_inline_keyboard(self, scene, template_engine):
        keyboard: dict = {}

        for button_label, button_attrs in scene.get("buttons", {}).items():
            label = self._parse_template(button_label, template_engine=template_engine)
            target = button_attrs["target"]

            match button_attrs["type"]:
                case "scene":
                    keyboard[label] = self._prepare_scene(target)
                case "return":
                    keyboard[label] = self._prepare_return(target)
                case "suggest":
                    keyboard[label] = self._prepare_suggestion(*target)
                case "redirect":
                    keyboard[label] = self._prepare_redirect(target)
                case "handoff":
                    keyboard[label] = self._prepare_handoff(target)
                case "link":
                    keyboard[label] = self._prepare_link(target)

        self.chain.set_inline_keyboard(keyboard, row_width=scene.get("row_width", 1))

    def _apply_entry_handler(self, scene: dict):
        if scene.get("entries") or scene.get("_default_entry_target"):
            self.chain.entry_text(self._filter_entry, True)(self._handle_entry)

    def _execute_on_exit_hooks(self, scene: dict, template_engine: str):
        if "on_exit" in scene:
            self._execute_hook(scene["on_exit"], template_engine)

    def _remove_garbage(self, scene: dict, scene_name: str):
        self.script_data.entry = None

        if not scene.get("_keep_history"):
            self.script_data.history.clear()
            self.script_data.history.append(scene_name)
    
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
        if context is not None:
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
    # Link Logic
    # ----------------------------------------------------------------------------
    
    def _prepare_link(self, url: str):
        return telekit.types.LinkButton(url)
    
    # ----------------------------------------------------------------------------
    # Return Logic
    # ----------------------------------------------------------------------------

    def _prepare_return(self, target: str):
        def render():
            self.script_data._rollback_to(target)
            self._render(target)

        return render
    
    # ----------------------------------------------------------------------------
    # Redirect & Handoff Logic
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
            self._render(target)

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

        self._render(choosed_scene)
    
    # ----------------------------------------------------------------------------
    # Timeout Logic
    # ----------------------------------------------------------------------------

    def _on_timeout(self):
        # "on timeout" handler api
        scene = self.script_data.get_current_scene()
        template_engine: str = self.script_data.get_template_engine()

        if "on_timeout" in scene:
            self._execute_hook(scene["on_timeout"], template_engine)

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

        self._render(self.script_data.history.pop())

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
            template = self._jinja_env.from_string(template_str)
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
                return str(Escape(value, parse_mode=parse_mode))
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
        
    def _execute_hook(self, api_calls: list[tuple[str, None | list[Any]]], template_engine: str):
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
        return str(Escape(str(value), parse_mode="markdown"))

    @staticmethod
    def escape_html(value):
        if value is None:
            return ""
        return str(Escape(str(value), parse_mode="html"))

# ----------------------------------------------------
# Script Data Structure (JSON)
# ----------------------------------------------------
#
# See on GitHub: https://github.com/Romashkaa/telekit/blob/main/docs/documentation/dsl_analyzer_output.md
