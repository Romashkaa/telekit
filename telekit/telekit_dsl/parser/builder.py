from .token import Token
from .nodes import *

class BuilderError(Exception):
    pass

class Builder:
    def __init__(self, ast: Ast, src: str):
        self.src = src
        self.ast = ast
        self.result = {
            "config": {},
            "scenes": {},
            "source": self.src
        }
        self.scenes_default_labels: dict[str, str] = {}

    def build(self) -> dict:
        self.ensure_single_config_block()
        self.check_main_scene()
        self.check_unique_scene_names()

        self.analyze_scenes_default_labels()

        for item in self.ast.body:
            match item:
                case ConfigBlock():
                    self.analyze_config(item)
                case SceneBlock():
                    self.analyze_scene(item)

        self.post_analysis()

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
        if "timeout" in self.result["config"]:
            if "timeout" not in self.result["scenes"]:
                raise BuilderError("`@ timeout {...}` scene is missing, but defined in `$ config {...}`. Add the scene or remove it from config.")

        for scene_name, scene in self.result["scenes"].items():
            for label, target_scene in scene["buttons"].items():
                if target_scene not in self.result["scenes"]:
                    if target_scene not in ("back",):
                        raise BuilderError(
                            f"Button '{label}' in scene '@{scene_name}' points to non-existent scene '@{target_scene}'"
                        )
                
        timeout = self.result["config"].get("timeout")
        if timeout is not None and timeout <= 0:
            raise BuilderError("Config 'timeout' cannot be negative or 0")

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
        result = {}

        # requirements = (
        #     ...
        # )

        optional = (
            ("timeout", int),
        )

        # # required fields
        # for key, typ in requirements:
        #     if key not in info.fields:
        #         raise BuilderError(f"Missing required field '{key}' in info block")
        #     val = info.fields[key]
        #     if not isinstance(val, typ):
        #         raise BuilderError(f"Field '{key}' must be of type {self.type_name(typ)}")
        #     result[key] = val

        # optional fields
        for key, typ in optional:
            if key in config.fields:
                val = config.fields[key]
                if not isinstance(val, typ):
                    raise BuilderError(f"Field '{key}' must be of type {self.type_name(typ)}")
                result[key] = val

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

