from .token import Token
from .nodes import *

class BuilderError(Exception):
    pass

MAGIC_SCENES = ("back", "next")
SPECIAL_NAMES = ("link", "suggest", "redirect", "handoff", "return")

class NoValue:
    pass

class Builder:
    def __init__(self, ast: Ast, src: str):
        self.src = src
        self.ast = ast
        self.result = {
            "order": [],
            "config": {},
            "scenes": {},
            "source": self.src,
        }
        self.config_blocks: list[dict[str, Any]] = []
        self.scenes_default_labels: dict[str, str] = {
            "next": "Next »",
            "back": "« Back"
        }
        self.RESERVED_NAMES = MAGIC_SCENES + SPECIAL_NAMES
        self._anonymous_scenes_count = 0

    def build(self) -> dict:
        for item in self.ast.body:
            if isinstance(item, ConfigBlock):
                self.analyze_config(item)
        self.finalize_configs()

        self.check_main_scene()
        self.analyze_anonimous_scenes()
        self.check_unique_scene_names()

        self.analyze_scenes_default_labels()

        for item in self.ast.body:
            if isinstance(item, SceneBlock):
                self.analyze_scene(item)

        self.post_analysis()
        self.check_last_scene_has_no_next()

        self.remove_refers_to_attr()

        return self.result
    
    def remove_refers_to_attr(self):
        for _, scene in self.result["scenes"].items():
            scene.pop("refers_to", None)
            scene.pop("_has_back_button", None)
            scene.pop("_has_next_button", None)

    def analyze_anonimous_scenes(self):
        for scene in self.ast.body:
            if not isinstance(scene, SceneBlock):
                continue

            if isinstance(scene.name, str):
                if scene.name.startswith("anonymous_") or scene.name in self.RESERVED_NAMES:
                    raise NameError(f"The scene name '{scene.name}' is reserved by the Telekit DSL. Please choose another one.")
            else:
                self._anonymous_scenes_count += 1
                scene.name = f"anonymous_{self._anonymous_scenes_count}"
    
    def analyze_scenes_default_labels(self):
        if next_label := self.result["config"].get("next_label"):
            self.scenes_default_labels["next"] = next_label

        if next_label := self.result["config"].get("back_label"):
            self.scenes_default_labels["back"] = next_label

        for item in self.ast.body:
            if not isinstance(item, SceneBlock):
                continue

            scene_name = item.name

            if not isinstance(scene_name, str):
                raise TypeError()

            if item.default_label:
                self.scenes_default_labels[scene_name] = item.default_label
            elif isinstance(title := item.fields.get("title", None), str):
                self.scenes_default_labels[scene_name] = title
            elif isinstance(text := item.fields.get("text", None), str):
                self.scenes_default_labels[scene_name] = text.split("\n")[0]
            else:
                self.scenes_default_labels[scene_name] = scene_name
    
    def post_analysis(self):
        for scene_name, scene in self.result["scenes"].items():
            for label, target_scene in scene["refers_to"].items():
                if target_scene not in self.result["scenes"]:
                    if target_scene not in MAGIC_SCENES:
                        raise BuilderError(
                            f"{label} in scene '@{scene_name}' points to non-existent scene '@{target_scene}'"
                        )
                
        timeout = self.result["config"].get("timeout_time")
        if timeout is not None and timeout <= 0:
            raise BuilderError("Config 'timeout_time' cannot be negative or 0")

        if "next_order" not in self.result["config"]:
            next_order = ["main"]
            for scene_name in self.result["order"]:
                if scene_name != "main" and not scene_name.startswith("_"):
                    next_order.append(scene_name)
                
            self.result["config"]["next_order"] = next_order

        if "main" not in self.result["config"]["next_order"]:
            self.result["config"]["next_order"] = ["main"] + self.result["config"]["next_order"]

        # optimization:
        next_order = self.result["config"]["next_order"]
        for scene_name, scene in self.result["scenes"].items():
            if scene.get("_has_back_button"):
                self.result["scenes"][scene_name]["_keep_history"] = True

        for scene_name, scene in self.result["scenes"].items():
            if not scene.get("_has_next_button"):
                continue

            try:
                current: int = self.result["order"].index(scene_name)
                for next_name in self.result["order"][current+1:]:
                    if next_name in next_order:
                        self.result["scenes"][scene_name]["_next"] = next_name
                        break
            except ValueError:
                continue

    def check_last_scene_has_no_next(self):
        next_order = self.result["config"].get("next_order", [])
        if not next_order:
            return self.check_next_not_used_when_order_empty()

        last_scene_name = next_order[-1]

        if last_scene_name not in self.result["scenes"]:
            return

        last_scene = self.result["scenes"][last_scene_name]

        for _, target in last_scene.get("refers_to", {}).items():
            if target == "next":
                raise BuilderError(
                    f"Scene '@{last_scene_name}' is last in next_order but contains a reference to 'next' scene. "
                    f"cannot use 'next' from the final scene in order."
                )
            
    def check_next_not_used_when_order_empty(self):
        next_order = self.result["config"].get("next_order", [])

        if next_order:
            return

        for scene_name, scene in self.result["scenes"].items():
            for _, target in scene.get("refers_to", {}).items():
                if target == "next":
                    raise BuilderError(
                        f"Scene '@{scene_name}' uses a 'next' button, "
                        f"but next_order is empty. Define next_order or remove the 'next' button."
                    )

    def ensure_single_config_block(self):
        config_count = 0

        for node in self.ast.body:
            if isinstance(node, ConfigBlock):
                config_count += 1

        if config_count > 1:
            raise BuilderError("Multiple '$ config { ... }' blocks found; only one is allowed")
        
    def check_main_scene(self):
        for node in self.ast.body:
            if isinstance(node, SceneBlock) and node.name == "main":
                return

        raise BuilderError("Missing required '@ main { ... }' scene (entry point)")
    
    def check_unique_scene_names(self):
        seen = set()
    
        for node in self.ast.body:
            if isinstance(node, SceneBlock):
                if node.name in seen:
                    raise BuilderError(f"Duplicate scene name '@ {node.name}' found")
                seen.add(node.name)

    def type_name(self, t: type | tuple[type, ...]) -> str:
        if isinstance(t, tuple):
            return " or ".join(x.__name__ for x in t)
        return t.__name__

    def analyze_config(self, config: ConfigBlock):
        name = config.name
        prefix = f"{name}_" if name else ""
        fields = {f"{prefix}{field}": v for field, v in config.fields.items()}
        self.config_blocks.append(fields)

    def finalize_configs(self):
        fields = {}

        for config in self.config_blocks:
            for key, value in config.items():
                if key in fields:
                    raise BuilderError(f"Duplicate config field: {key}")
                fields[key] = value

        result = {}
        optional_fields = (
            ("timeout_time", int),
            ("timeout_message", str),
            ("timeout_label", str),

            ("next_label", str),
            ("next_order", list),

            ("back_label", str),

            ("template", str)
        )

        optional_keys = [key[0] for key in optional_fields]

        for key in fields:
            if key not in optional_keys and not key.startswith("vars_"):
                raise BuilderError(f"Unknown field: '{key}' — this option is not allowed")

        for key, typ in optional_fields:
            if key in fields:
                val = fields[key]
                if not isinstance(val, typ):
                    raise BuilderError(f"Field '{key}' must be of type {self.type_name(typ)}")
                result[key] = val

        # next order 
        
        if "next_order" in fields:
            next_order = fields["next_order"]

            for elem in next_order:
                if not isinstance(elem, str):
                    raise BuilderError("Field 'next_order' must be list of strings")
                
            if len(next_order) != len(set(next_order)):
                raise BuilderError("Field 'next_order' must contain only unique values")
            
        if "template" in fields:
            if fields.get("template") not in ["jinja", "vars", "plain"]:
                raise BuilderError("Field 'template' must contain only 'jinja', 'vars' or 'plain'")
        
        # variables

        result.update({k: v for k, v in fields.items() if k.startswith("vars_")})

        self.result["config"] = result

    def analyze_scene(self, scene: SceneBlock):
        name: str | None = scene.name

        if not isinstance(name, str):
            raise TypeError()

        fields: dict[str, Any] = scene.fields

        scene_data: dict[str, Any] = {"name": name}

        if name in MAGIC_SCENES + SPECIAL_NAMES:
            raise NameError(f"The scene name '{name}' is reserved by the Telekit DSL. Please choose another one.")

        # required fields: either title + message or text
        if "text" in fields:
            text_val = fields["text"]
            if not isinstance(text_val, str):
                raise BuilderError(f"Field 'text' in scene '@{name}' must be of type str")
            if not text_val.strip():
                raise BuilderError(f"Scene '@{name}' has an empty text")
            scene_data["text"] = text_val
            scene_data["_use_text"] = True
        else:
            if "title" not in fields or "message" not in fields:
                raise BuilderError(
                    f"Scene '@{name}' must contain 'title' and 'message' field\n\n"
                    f"Example:\n"
                    f"@ {name} {{\n"
                    f"    title = \"...\"\n"
                    f"    message = \"...\"\n"
                    f"}}"
                )

            title_val = fields["title"]
            message_val = fields["message"]

            if not isinstance(title_val, str):
                raise BuilderError(f"Field 'title' in scene '@{name}' must be of type str")
            if not isinstance(message_val, str):
                raise BuilderError(f"Field 'message' in scene '@{name}' must be of type str")
            
            if not title_val.strip():
                raise BuilderError(f"Scene '@{name}' has an empty title")
            if not message_val.strip():
                raise BuilderError(f"Scene '@{name}' has an empty message") 

            scene_data["title"] = title_val
            scene_data["message"] = message_val

        # optional fields
        optional: tuple[tuple[str, type | tuple[type, ...], Any], ...] = (
            # Style
            ("image", str, NoValue()),
            ("use_italics", bool, NoValue()),
            ("parse_mode", (str, type(None)), NoValue()),

            # Templates
            ("template", str, NoValue())
        )

        # check optional fields
        for key, typ, default in optional:
            if key in fields:
                text_val = fields[key]
                if not isinstance(text_val, typ):
                    raise BuilderError(f"Field '{key}' in scene '@ {name}' must be of type {self.type_name(typ)}")
                scene_data[key] = text_val
            elif not isinstance(default, NoValue):
                scene_data[key] = default
        
        # Style
        
        if scene_data.get("parse_mode") and scene_data["parse_mode"].lower() not in ("markdown", "html"):
            raise BuilderError(f"\n\nScene '@{name}' has invalid parse_mode '{scene_data['parse_mode']}'.\nUse: 'markdown' or 'html'")
        
        if "template" in scene_data and scene_data.get("template") not in ["jinja", "vars", "plain"]:
            raise BuilderError("\n\nScene '@{name}' has invalid 'template' attribute: must contain only 'jinja', 'vars' or 'plain'")
        
        # Handler API

        if "on_enter" in fields:
            scene_data["on_enter"]      = fields["on_enter"]
        if "on_enter_once" in fields:
            scene_data["on_enter_once"] = fields["on_enter_once"]
        if "on_exit" in fields:
            scene_data["on_exit"]       = fields["on_exit"]
        if "on_timeout" in fields:
            scene_data["on_timeout"]    = fields["on_timeout"]

        # Entries

        scene_data["refers_to"] = {}

        if "entries" in fields:
            scene_data["entries"] = {}
            for trigger, target_scene in fields["entries"].items():
                if target_scene == scene.name:
                    raise BuilderError(f"Entry '{target_scene}' in scene '@{scene.name}' points to itself")

                if target_scene not in self.scenes_default_labels:
                    raise BuilderError(f"Scene '@{name}' contains a entry that points to unknown scene '{target_scene}'")

                if isinstance(trigger, AnyTrigger):
                    if "_default_entry_target" in scene_data:
                        raise BuilderError(f"Scene '@{name}' contains multiple default entries")
                    scene_data["_default_entry_target"] = target_scene
                else:
                    scene_data["entries"][trigger] = target_scene

                if target_scene == "back":
                    scene_data["_has_back_button"] = True
                if target_scene == "next":
                    scene_data["_has_next_button"] = True

                scene_data["refers_to"][f"Entry '{trigger}'"] = target_scene
                

        # Buttons

        scene_data["buttons"] = {}

        # handle buttons if present
        if "buttons" in fields:
            buttons_block = fields["buttons"]
            buttons: dict[str | NoLabel, tuple[str, str | None]] = buttons_block.get("buttons", [])

            width = buttons_block.get("width") # row_width
            if width is not None and width != 1:
                scene_data["row_width"] = int(width)

            for label, [target_scene, argument] in buttons.items():
                match target_scene:
                    case "handoff":
                        if isinstance(label, NoLabel):
                            raise BuilderError(f"\n\nScene '@{name}' contains a handoff-button that needs a label and handler name. \n\n- Example: handoff('Start', StartHandler)\n")
                        if not label.strip():
                            raise BuilderError(f"\n\nScene '@{name}' contains a handoff-button with an empty label")
                        if argument is None:
                            raise BuilderError(f"\n\nScene '@{name}' contains a handoff-button that missing argument. \n\n- Example: handoff('Start', StartHandler)\n")
                        scene_data["buttons"][label] = {
                            "type": "handoff",
                            "target": argument
                        }
                    case "redirect":
                        if isinstance(label, NoLabel):
                            raise BuilderError(f"\n\nScene '@{name}' contains a redirect-button that needs a label and argument. \n\n- Example: redirect('Start', '/start INVITE_CODE')\n")
                        if not label.strip():
                            raise BuilderError(f"\n\nScene '@{name}' contains a redirect-button with an empty label")
                        if argument is None:
                            raise BuilderError(f"\n\nScene '@{name}' contains a redirect-button that missing argument. \n\n- Example: redirect('Start', '/start INVITE_CODE')\n")
                        scene_data["buttons"][label] = {
                            "type": "redirect",
                            "target": argument
                        }
                    case "suggest":
                        if isinstance(label, NoLabel):
                            raise BuilderError(f"\n\nScene '@{name}' contains a suggest-button that needs a label and suggestion. \n\n- Example: suggest('Hint', 'mypassword')\n- Example: suggest('mypassword')\n")
                        if not label.strip():
                            raise BuilderError(f"\n\nScene '@{name}' contains a suggest-button with an empty label")
                        if argument is None:
                            argument = label.strip()

                        if argument in scene_data["entries"]:
                            target = scene_data["entries"][argument]
                        elif scene_data.get("_default_entry_target"):
                            target = scene_data["_default_entry_target"]
                        else:
                            raise BuilderError(f"Scene '@{name}' contains a suggest-button '{label}' that points to entry '{argument}', but no such entry exists and no default entry is defined")
                        
                        scene_data["buttons"][label] = {
                            "type": "suggest",
                            "target": (target, argument)
                        }
                    case "return":
                        if isinstance(label, NoLabel):
                            raise BuilderError(f"\n\nScene '@{name}' contains a return-button that needs a label and target scene name")
                        if not label.strip():
                            raise BuilderError(f"\n\nScene '@{name}' contains a return-button that needs a label AND target scene name")
                        if argument is None:
                            argument = label.strip()
                            
                            if label in self.scenes_default_labels:
                                label = self.scenes_default_labels[label]
                            else:
                                raise BuilderError(f"Scene '@{name}' contains a return-button that points to unknown scene '{label}'")
                        if argument in MAGIC_SCENES:
                            raise BuilderError(f"Scene '@{name}' contains a return-button that points to magic scene '{argument}' (It is forbidden in this context)")
                        scene_data["buttons"][label] = {
                            "type": "return",
                            "target": argument
                        }
                    case "link":
                        if isinstance(label, NoLabel):
                            raise BuilderError(f"\n\nScene '@{name}' contains a link-button that needs a label and URL. \n\n- Example: link('YouTube', 'https://youtube.com')\n")
                        if not label.strip():
                            raise BuilderError(f"\n\nScene '@{name}' contains a button with an empty label")
                        if argument is None:
                            raise BuilderError(f"\n\nScene '@{name}' contains a link-button that missing target URL. \n\n- Example: link('YouTube', 'https://youtube.com')\n")
                        if not argument.startswith(("http://", "https://")):
                            raise BuilderError(f"\n\nScene '@{name}' contains a link-button '{label}' that has invalid URL: '{argument}'")
                        scene_data["buttons"][label] = {
                            "type": "link",
                            "target": argument
                        }
                    case _:
                        if isinstance(label, NoLabel):
                            if target_scene in self.scenes_default_labels:
                                label = self.scenes_default_labels[target_scene]
                            else:
                                raise BuilderError(f"Scene '@{name}' contains a button that points to unknown scene '{target_scene}'")

                        if not label.strip():
                            raise BuilderError(f"Scene '@{name}' contains a button with an empty label")
                            
                        if target_scene == scene.name:
                            raise BuilderError(f"Button '{label}' in scene '@{scene.name}' points to itself")

                        scene_data["buttons"][label] = {
                            "type": "scene",
                            "target": target_scene
                        }
                        scene_data["refers_to"][f"Button '{label}'"] = target_scene

                        if target_scene == "back":
                            scene_data["_has_back_button"] = True

                        if target_scene == "next":
                            scene_data["_has_next_button"] = True

        self.result["scenes"][scene.name] = scene_data
        self.result["order"].append(scene.name)