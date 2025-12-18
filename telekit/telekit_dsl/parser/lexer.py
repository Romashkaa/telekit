from typing import Optional
import ast

from .token import Token

# ---------------------------
#  Exceptions
# ---------------------------

class TokenizingError(Exception):
    pass

# ---------------------------
#  Tools
# ---------------------------

def dedent_multiline(message: str) -> str:
    """
    Removes leading empty lines and normalizes indentation
    by removing the minimum common leading whitespace from all lines.
    
    Args:
        message (str): Multiline string with backticks or regular string.
    
    Returns:
        str: Cleaned multiline string with minimal indentation removed.
    """
    lines = message.splitlines()
    
    # Remove first/last empty lines
    while lines and lines[0].strip() == "":
        lines.pop(0)
    while lines and lines[-1].strip() == "":
        lines.pop()
    
    if not lines:
        return ""
    
    # Determine minimal indentation (only spaces/tabs)
    min_indent = None
    for line in lines:
        stripped = line.lstrip()
        if stripped:  # ignore empty lines
            indent = len(line) - len(stripped)
            if min_indent is None or indent < min_indent:
                min_indent = indent
    
    # Remove minimal indentation from all lines
    if min_indent is None:
        min_indent = 0
    dedented_lines = [line[min_indent:] if len(line) >= min_indent else line for line in lines]
    
    return "\n".join(dedented_lines)

# ---------------------------
#  Main Lexer
# ---------------------------

class Lexer:
    def __init__(self, source: str):
        self.src = source
        self.pos = 0
        self.length = len(source)
        self.current_char = self.src[self.pos] if self.src else None
        self.tokens: list[Token] = []

    def next(self):
        self.pos += 1
        self.current_char = self.src[self.pos] if self.pos < self.length else None

    def peek(self, offset=1) -> Optional[str]:
        idx = self.pos + offset
        return self.src[idx] if idx < self.length else None

    def skip_whitespace(self):
        while self.current_char and self.current_char.isspace():
            self.next()

    def skip_comment(self):
        # Handle // single-line
        if self.peek() == '/':
            while self.current_char and self.current_char != '\n':
                self.next()
        # Handle /* multi-line */
        elif self.peek() == '*':
            self.next()  # skip '*'
            self.next()
            while self.current_char and not (self.current_char == '*' and self.peek() == '/'):
                self.next()
            if self.current_char == '*':
                self.next()  # skip '*'
                self.next()  # skip '/'
        else:
            self.add_token('op', '/')
            self.next()

    def add_token(self, type_, value):
        self.tokens.append(Token(type_, value, self.pos))

    # ---------------------------
    #  Core scanning
    # ---------------------------

    def read_number(self):
        start = self.pos
        while self.current_char and (self.current_char.isdigit() or self.current_char == '.'):
            self.next()
        value = self.src[start:self.pos]
        number = self._parse_number(value)
        self.add_token('number', number)

    def _parse_number(self, string: str | int | float) -> int | float | None:
        try:
            number = float(string)
            if number.is_integer():
                return int(number)
            return number
        except ValueError:
            return None

    def read_identifier(self):
        start = self.pos
        while self.current_char and (self.current_char.isalnum() or self.current_char == '_'):
            self.next()
        value = self.src[start:self.pos]
        self.add_token('kw', value)

    def read_string(self, quote_char):
        self.next()  # skip opening quote
        start = self.pos
        value = ''
        while self.current_char and self.current_char != quote_char:
            if self.current_char == '\\':
                value += self.current_char
                self.next()
            value += self.current_char
            self.next()
        if self.current_char != quote_char:
            raise TokenizingError(f"Unterminated string at {start}")
        self.next()  # skip closing quote
        value = ast.literal_eval(f'"""{value}"""')
        self.add_token('string', value)

    def read_backtick_string(self):
        self.next()  # skip `
        start = self.pos
        value = ''
        while self.current_char and self.current_char != '`':
            value += self.current_char
            self.next()
        if self.current_char != '`':
            raise TokenizingError(f"Unterminated `string` at {start}")
        self.next()
        value = dedent_multiline(value)
        self.add_token('string', value)

    def tokenize(self):
        while self.current_char:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char == '/':
                if self.peek() in ('/', '*'):
                    self.skip_comment()
                else:
                    self.add_token('op', '/')
                    self.next()
                continue

            if self.current_char in ('"', "'"):
                self.read_string(self.current_char)
                continue

            if self.current_char == '`':
                self.read_backtick_string()
                continue

            if self.current_char.isdigit():
                self.read_number()
                continue

            if self.current_char.isalpha() or self.current_char == '_':
                self.read_identifier()
                continue

            if self.current_char in '{}[]();,':
                self.add_token('punc', self.current_char)
                self.next()
                continue

            if self.current_char in '=$@': # +-*/<>!%^&|~:?.
                self.add_token('op', self.current_char)
                self.next()
                continue

            # unknown character outside string
            raise TokenizingError(f"Unexpected character '{self.current_char}' at position {self.pos}")

        return self.tokens
