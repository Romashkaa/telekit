# Copyright (c) 2025 Ving Studio, Romashka
# Licensed under the MIT License. See LICENSE file for full terms.

class Parser:
    def __init__(self, data: str):
        self.data = data
        self.code_length = len(data)
        self.position = 0

    def parse(self) -> dict[str, str]:

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
    """
    Reads a text file and parses its content into a dictionary of key-value pairs.

    ---

    Args:
        path (str): The file path to read.

    Returns:
        dict[str, str]: A dictionary where keys are section titles (lines starting with `#`)
                        and values are the corresponding text blocks.
                        Returns an empty dictionary if reading or parsing fails.

    ---

    ## Example:
    ```
        result = telekit.chapters.read("example.txt").items()
        print(result)
        # Output:
        # {
        #     "Key": "Value",
        #     "Another Key": "Value line1\\nValue line2"
        # }
    ```
    ## Output:
    ```
    {
        "Key": "Value",
        "Another Key": "Value line1\\nValue line2\\nValue line3"
    }
    ```
    ## example.txt:
    ```
    # Key
    Value

    # Another Key
    Value line1
    Value line2
    Value line3
    ```
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            source = f.read()
        return Parser(source).parse()
    except Exception as e:
        print(f"Failed to load file '{path}': {e}")
        return {}
        
def parse(source: str) -> dict[str, str]:
    """
    Parses a text source into a dictionary of key-value pairs. 
    Keys are lines starting with `#`, and values are the text that follows until the next key.

    ---

    Args:
        source (str): The source string containing keys and values.

    Returns:
        dict[str, str]: A dictionary where keys are the section titles (without `#`) 
                        and values are the corresponding text blocks.

    ---

    ## Example
    ```
    source = \"""
    # Key
    Value

    # Another Key
    Value line1
    Value line2
    Value line3
    \"""

    pages = telekit.chapters.parse(source).items()
    print(pages)
    ```

    ## Output:
    ```
    {
        "Key": "Value",
        "Another Key": "Value line1\\nValue line2\\nValue line3"
    }
    ```
    """
    return Parser(source).parse()
