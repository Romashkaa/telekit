from .token import Token
from .nodes import *

class BuilderError(Exception):
    pass

MAGIC_SCENES = ("back", "next")

class Builder:
    def __init__(self, ast: Ast, src: str):
        self.src = src
        self.ast = ast
        self.result = {
            "config": {},
            "scenes": {},
            "source": self.src,
            "order": []
        }
        self.config_blocks: list[dict[str, Any]] = []
        self.scenes_default_labels: dict[str, str] = {
            "next": "Next »",
            "back": "« Back"
        }

    def build(self) -> dict:
        # self.ensure_single_config_block()
        self.check_main_scene()
        self.check_unique_scene_names()

        self.analyze_scenes_default_labels()

        for item in self.ast.body:
            match item:
                case ConfigBlock():
                    self.analyze_config(item)
                case SceneBlock():
                    self.analyze_scene(item)

        self.finalize_configs()
        self.post_analysis()
        self.check_last_scene_has_no_next()

        return self.result
    
    def analyze_scenes_default_labels(self):
        for item in self.ast.body:
            if not isinstance(item, SceneBlock):
                continue

            if item.default_label:
                self.scenes_default_labels[item.name] = item.default_label
            elif isinstance(title := item.fields.get("title", None), str):
                self.scenes_default_labels[item.name] = title
            else:
                self.scenes_default_labels[item.name] = item.name
    
    def post_analysis(self):
        for scene_name, scene in self.result["scenes"].items():
            for label, target_scene in scene["buttons"].items():
                if target_scene not in self.result["scenes"]:
                    if target_scene not in MAGIC_SCENES:
                        raise BuilderError(
                            f"Button '{label}' in scene '@{scene_name}' points to non-existent scene '@{target_scene}'"
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

    def check_last_scene_has_no_next(self):
        next_order = self.result["config"].get("next_order", [])
        if not next_order:
            return self.check_next_not_used_when_order_empty()

        last_scene_name = next_order[-1]

        if last_scene_name not in self.result["scenes"]:
            return

        last_scene = self.result["scenes"][last_scene_name]

        for label, target in last_scene.get("buttons", {}).items():
            if target == "next":
                raise BuilderError(
                    f"Scene '@{last_scene_name}' is last in next_order but contains a Next button ('{label}'). "
                    f"cannot use 'next' from the final scene in order."
                )
            
    def check_next_not_used_when_order_empty(self):
        next_order = self.result["config"].get("next_order", [])

        if next_order:
            return

        for scene_name, scene in self.result["scenes"].items():
            for label, target in scene.get("buttons", {}).items():
                if target == "next":
                    raise BuilderError(
                        f"Scene '@{scene_name}' uses a Next button ('{label}'), "
                        f"but next_order is empty. Define next_order or remove the Next button."
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
            ("next_order", list)
        )

        optional_keys = [key[0] for key in optional_fields]

        for key in fields:
            if key not in optional_keys:
                raise BuilderError(f"Unknown field: '{key}' — this option is not allowed")

        for key, typ in optional_fields:
            if key in fields:
                val = fields[key]
                if not isinstance(val, typ):
                    raise BuilderError(f"Field '{key}' must be of type {self.type_name(typ)}")
                result[key] = val

        if "next_order" in fields:
            next_order = fields["next_order"]

            for elem in next_order:
                if not isinstance(elem, str):
                    raise BuilderError("Field 'next_order' must be list of strings")
                
            if len(next_order) != len(set(next_order)):
                raise BuilderError("Field 'next_order' must contain only unique values")

        self.result["config"] = result

    def analyze_scene(self, scene: SceneBlock):
        name: str = scene.name
        fields: dict[str, Any] = scene.fields

        # required fields
        required: tuple[tuple[str, type], ...] = (
            ("title", str),
            ("message", str),
        )

        # optional fields
        optional: tuple[tuple[str, type | tuple[type, ...], Any], ...] = (
            ("image", str, None),
            ("use_italics", bool, False),
            ("parse_mode", (str, type(None)), None)
        )

        scene_data: dict[str, Any] = {"name": name}

        if name in MAGIC_SCENES:
            raise ValueError(f"The scene name '{name}' is reserved by the Telekit DSL. Please choose another one.")

        # check required fields
        for key, typ in required:
            if key not in fields:
                raise BuilderError(
                    f"Scene '@ {name}' must contain '{key}' field\n\n"
                    f"Example:\n"
                    f"@ {name}" + " {\n"
                    + "\n".join(f"  {k} = \"...\";" for k, _ in required)
                    + "\n}"
                )
            val = fields[key]
            if not isinstance(val, typ):
                raise BuilderError(f"Field '{key}' in scene '@ {name}' must be of type {self.type_name(typ)}")
            scene_data[key] = val

        # check optional fields
        for key, typ, default in optional:
            if key in fields:
                val = fields[key]
                if not isinstance(val, typ):
                    raise BuilderError(f"Field '{key}' in scene '@ {name}' must be of type {self.type_name(typ)}")
                scene_data[key] = val
            else:
                scene_data[key] = default

        if not scene_data["title"].strip():
            raise BuilderError(f"Scene '@{name}' has an empty title")
        if not scene_data["message"].strip():
            raise BuilderError(f"Scene '@{name}' has an empty message")
        
        if scene_data["parse_mode"] and scene_data["parse_mode"].lower() not in ("markdown", "html"):
            raise BuilderError(f"Scene '@{name}' has invalid parse_mode '{scene_data['parse_mode']}'")

        scene_data["buttons"] = {}

        # handle buttons if present
        if "buttons" in fields:
            buttons_block = fields["buttons"]
            buttons: dict[str | NoLabel, str] = buttons_block.get("buttons", [])

            width = buttons_block.get("width", 1) # row_width
            scene_data["row_width"] = int(width)

            for label, target in buttons.items():

                if isinstance(label, NoLabel):
                    label = self.scenes_default_labels[target]

                if not label.strip():
                    raise BuilderError(f"Scene '@{name}' contains a button with an empty label")

                if label in scene_data["buttons"]:
                    raise BuilderError(f"Duplicate button label '{label}' in scene '@ {name}'")
                    
                if target == scene.name:
                    raise BuilderError(f"Button '{label}' in scene '@{scene.name}' points to itself")

                scene_data["buttons"][label] = target

        self.result["scenes"][scene.name] = scene_data
        self.result["order"].append(scene.name)

