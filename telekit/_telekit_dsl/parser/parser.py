from .token import Token
from .nodes import *

# ---------------------------
# Exception
# ---------------------------

class ParseError(Exception):
    pass

# ---------------------------
# Main Parser
# ---------------------------

class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0

    # ---------------------------
    # Helpers
    # ---------------------------

    def token(self) -> Token:
        if self.pos >= len(self.tokens):
            raise ParseError("Unexpected end of input")
        return self.tokens[self.pos]

    def peek(self, offset=1) -> Token | None:
        idx = self.pos + offset
        return self.tokens[idx] if idx < len(self.tokens) else None

    def next(self) -> Token | None:
        self.pos += 1
        if self.pos >= len(self.tokens):
            return None
        return self.tokens[self.pos]

    def match(self, type_: str, value: str | None = None) -> bool:
        if self.pos >= len(self.tokens):
            return False
        t = self.token()
        if t.type != type_:
            return False
        if value is not None and t.value != value:
            return False
        self.next()
        return True

    def expect(self, type_: str, value: str | None = None) -> Token:
        t = self.token()
        if t.type != type_:
            raise ParseError(f"Expected token type '{type_}', got '{t.type}' at {self.pos}")
        if value is not None and t.value != value:
            raise ParseError(f"Expected '{value}', got '{t.value}' at {self.pos}")
        self.next()
        return t

    # ---------------------------
    # Main entry
    # ---------------------------

    def parse(self) -> Ast:
        ast = Ast()
        while self.pos < len(self.tokens):
            node = self.parse_statement()
            if node:
                ast.body.append(node)
        return ast

    # ---------------------------
    # Statements
    # ---------------------------

    def parse_statement(self):
        t = self.token()

        if t.value == "$":
            return self.parse_config_block()

        if t.value == "@":
            return self.parse_scene_block()

        # skip anything else
        self.next()
        return None

    def parse_config_block(self):
        self.expect("op", "$")
        if self.token().type == "kw":
            name = self.expect("kw").value
        else:
            name = ""
        self.expect("punc", "{")

        block = ConfigBlock(name=name)

        while self.token().value != "}":
            t = self.token()
            if t.type == "kw":
                key = t.value
                self.next()
                self.expect("op", "=")
                val = self.parse_value()
                block.fields[key] = val
                self.match("punc", ";")
            else:
                self.next()

        self.expect("punc", "}")
        return block

    def parse_scene_block(self):
        self.expect("op", "@")

        if self.token().type == "kw":
            name = self.expect("kw").value
        else:
            name = None

        # optional default label
        default_label = None
        if self.match("punc", "("):
            if self.token().type != "string":
                raise ParseError(f"Expected string as default label at {self.pos}")
            default_label = self.token().value
            self.next()
            self.expect("punc", ")")

        self.expect("punc", "{")

        scene = SceneBlock(name, default_label)

        while self.token().value != "}":
            t = self.token()
            if t.type == "kw":
                key = t.value
                self.next()

                # special case: buttons(width) { ... }
                if key == "buttons":
                    scene.fields[key] = self.parse_buttons_block()
                    continue

                # special case: on_enter / on_enter_once / ...
                if key in ("on_enter", "on_enter_once", "on_exit", "on_timeout"):
                    scene.fields[key] = self.parse_on_api_block()
                    continue

                # special case: entries { ... }
                if key == "entries":
                    scene.fields[key] = self.parse_entries_block()
                    continue

                self.expect("op", "=")
                val = self.parse_value()
                scene.fields[key] = val
                self.match("punc", ";")
            else:
                self.next()

        self.expect("punc", "}")
        return scene

    def parse_buttons_block(self) -> dict[str, int | dict[str | NoLabel, tuple[str, str | None]]]:
        width = 1

        # optional `(row_width)`
        if self.match("punc", "("):
            if self.token().type != "number":
                raise ParseError(f"Expected number after 'buttons(' at {self.pos}")
            width = int(self.token().value)
            self.next()
            self.expect("punc", ")")

        # expect `{`
        self.expect("punc", "{")
        buttons: dict[str | NoLabel, tuple[str, str | None]] = {}

        while self.token() and self.token().value != "}":
            t = self.token()

            # `scene_name("Label")` | `scene_name` | `scene_name()`
            if t.type == "kw":
                scene_name = t.value
                self.next()

                argument = None

                if self.match("punc", "("):
                    # expect only one argument (string)
                    if self.token().type == "string":
                        label = self.token().value
                        self.next()
                        self.match("punc", ",")
                        # expect argument (string)
                        if self.token().type == "string":
                            argument = self.token().value
                            self.next()
                    else:
                        label = NoLabel()
                        # raise ParseError(f"Expected string as button label at {self.pos}")
                    self.expect("punc", ")")
                else:
                    label = NoLabel()

                buttons[label] = (scene_name, argument)
            elif t.value == ";":
                self.next()
            else:
                raise ParseError(f"Expected name or ';' at {self.pos}: '{t.value}{getattr(self.peek(), "value", "")}'")

        self.expect("punc", "}")
        return {"width": width, "buttons": buttons}

    def parse_value(self):
        t = self.token()

        if t.type == "string":
            self.next() 
            return t.value

        if t.type == "number":
            self.next()
            return t.value
        
        if t.type == "kw":
            self.next()
            if t.value.lower() == "none":
                return None
            if t.value.lower() == "false":
                return False
            if t.value.lower() == "true":
                return True
            return t.value

        if t.value == "[":
            self.next()
            items = []
            while self.token().value != "]":
                items.append(self.parse_value())
                self.match("punc", ",")
            self.expect("punc", "]")
            return items

        raise ParseError(f"Unexpected token '{t.value}' at position {self.pos}")

    def parse_on_api_block(self) -> list[list]:
        self.expect("punc", "{")
        calls = []

        while self.token().value != "}":
            t = self.token()
            if t.type == "kw":
                method_name = t.value
                self.next()

                args = None
                if self.match("punc", "("):
                    args_list = []
                    while self.token().value != ")":
                        args_list.append(self.parse_value())
                        self.match("punc", ",")
                    self.expect("punc", ")")
                    args = args_list

                calls.append((method_name, args))
            elif t.value == ";":
                self.next()
            else:
                raise ParseError(f"Expected name or ';' at {self.pos}")

        self.expect("punc", "}")
        return calls
    
    def parse_entries_block(self):
        # expect `{`
        self.expect("punc", "{")
        entries: dict[str | AnyTrigger, str] = {}

        while self.token() and self.token().value != "}":
            t = self.token()

            # `scene_name("on text")`
            if t.type == "kw":
                scene_name = t.value
                self.next()

                if self.match("punc", "("):
                    # expect only one argument (string)
                    if self.token().type == "string":
                        trigger = self.token().value
                        self.next()
                    else:
                        trigger = AnyTrigger()

                    self.expect("punc", ")")
                else:
                    # on any text
                    trigger = AnyTrigger()

                entries[trigger] = scene_name
            elif t.value == ";":
                self.next()
            else:
                raise ParseError(f"Expected name or ';' at {self.pos}")

        self.expect("punc", "}")
        return entries