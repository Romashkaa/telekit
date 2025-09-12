# --------------------------------------------------
# Local
# --------------------------------------------------

class Parser:
    def __init__(self, path: str):
        self.path = path
        self.data = ""
        self.position = 0
        self.code_length = 0

    def _read_file(self):
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                self.data = f.read()
                self.code_length = len(self.data)
        except Exception as e:
            print(f"Failed to load file '{self.path}': {e}")

    def parse(self) -> dict[str, str]:
        self._read_file()

        sections: dict[str, str] = {}
        current_title: str | None = None
        buffer: list[str] = []

        while not self.is_eof():
            line = self._read_line()

            if line.startswith("# "):
                if current_title:
                    sections[current_title] = "\n".join(buffer).strip()
                    buffer = []
                current_title = line[2:].strip()

            else:
                buffer.append(line)

        if current_title:
            sections[current_title] = "\n".join(buffer).strip()

        return sections

    def _read_line(self) -> str:
        if self.is_eof():
            return ""

        start = self.position
        while not self.is_eof() and self.data[self.position] != "\n":
            self.position += 1

        line = self.data[start:self.position]
        if not self.is_eof():
            self.position += 1
        return line

    def scan_length(self) -> int:
        char: str = self.char()
        length: str = ""

        while char.isdigit():
            length += char
            char = self.next()

        return int(length) if length.isdigit() else 0

    def char(self) -> str:
        if self.position >= self.code_length:
            return ""
        return self.data[self.position]

    def skip(self):
        self.position += 1

    def next(self) -> str:
        self.position += 1
        return self.char()

    def consume(self) -> str:
        char: str = self.char()
        self.position += 1
        return char

    def is_eof(self) -> bool:
        return self.position >= self.code_length
    

__all__ = ["version", "read"]

version = "x250708"
    
def read(path: str) -> dict[str, str]:
    return Parser(path).parse()
