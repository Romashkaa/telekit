from . import (
    lexer, parser,
    token, nodes,
    builder
)

def analyze(src: str):
    tokens = lexer.Lexer(src).tokenize()
    ast = parser.Parser(tokens).parse()
    model = builder.Builder(ast, src).build()

    return model

MAGIC_SCENES = builder.MAGIC_SCENES

__all__ = [
    "analyze",
    "lexer",
    "parser",
    "builder",
    "token",
    "nodes",
    "MAGIC_SCENES"
]