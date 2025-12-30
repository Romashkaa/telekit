from .token import Token
from .nodes import *

# ---------------------------
# Exception
# ---------------------------

class ParserError(Exception):
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
            raise ParserError("Unexpected end of input")
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
            raise ParserError(f"Expected token type '{type_}', got '{t.type}' at {self.pos}")
        if value is not None and t.value != value:
            raise ParserError(f"Expected '{value}', got '{t.value}' at {self.pos}")
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
        name = self.expect("kw").value

        # optional default label
        default_label = None
        if self.match("punc", "("):
            if self.token().type != "string":
                raise ParserError(f"Expected string as default label at {self.pos}")
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

                # special case: buttons[width] { ... }
                if key == "buttons":
                    scene.fields[key] = self.parse_buttons_block()
                    continue

                self.expect("op", "=")
                val = self.parse_value()
                scene.fields[key] = val
                self.match("punc", ";")
            else:
                self.next()

        self.expect("punc", "}")
        return scene

    def parse_buttons_block(self) -> dict[str, int | dict[str | NoLabel, str]]:
        width = 1

        # optional `(row_width)`
        if self.match("punc", "("):
            if self.token().type != "number":
                raise ParserError(f"Expected number after 'buttons(' at {self.pos}")
            width = int(self.token().value)
            self.next()
            self.expect("punc", ")")

        # expect `{`
        self.expect("punc", "{")
        buttons: dict[str | NoLabel, str] = {}

        while self.token() and self.token().value != "}":
            t = self.token()

            # `scene_name("Label")`
            if t.type == "kw":
                scene_name = t.value
                self.next()

                label = NoLabel()
                if self.match("punc", "("):
                    # expect only one argument (string)
                    if self.token().type == "string":
                        label = self.token().value
                        self.next()
                    else:
                        raise ParserError(f"Expected string as button label at {self.pos}")
                    self.expect("punc", ")")

                # # if no label provided, use scene name as fallback
                # label = label or scene_name
                buttons[label] = scene_name

            elif t.value == ";":
                self.next()
                continue
            else:
                self.next()

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

        raise ParserError(f"Unexpected token '{t.value}' at position {self.pos}")