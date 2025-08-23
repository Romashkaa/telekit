# type: ignore

# MIT License  
# © 2025 Romashka (Ving Studio)   
#
# Documentation: https://t.me/snapcode_io
#
# This file contains the official implementation of the **Snapcode** data serialization format,  
# authored and originally developed by Romashka.  
#
# Snapcode is an open serialization format designed to store nested data structures (such as lists,  
# dictionaries, sets, and tuples) in a compact, efficient, and machine-friendly way.  
#
# This Python codebase represents the reference implementation of the Snapcode format.  
# Both the format itself and this implementation are released under the terms of the MIT license.  
#
# You are free to use, modify, and distribute this implementation, as well as adopt the Snapcode  
# format in your own software, tools, or libraries — commercial or non-commercial —  
# as long as the terms below are respected.
#
# --- MIT License Terms ---
#
# Permission is hereby granted, free of charge, to any person obtaining a copy  
# of this software and associated documentation files (the "Software"), to deal  
# in the Software without restriction, including without limitation the rights  
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell  
# copies of the Software, and to permit persons to whom the Software is  
# furnished to do so, subject to the following conditions:
#
# The above copyright notice, link to documentation and this permission notice shall be included  
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,  
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,  
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.

# -- SUPPORTED TYPES -- 
# list  -> l, 
# dict  -> d, 
# str   -> s, 
# int   -> i, 
# float -> f, 
# bool  -> b,
# tuple -> t, 
# set   -> e,
# None  -> n (with no content)

# -- EXAMPLE --
# [1, "2"]   2l 1i12s2
# ["A","AB","ABC","ABCD"]  4l 1sA2sAB3sABC4sABCD
# [True, False] 2l 1bT1bF

# --------------------------------------------------
# Export
# --------------------------------------------------

from typing import Any

__all__ = ["pack", "unpack", "version"]

version = "x250708-telekit-edition"

def unpack(snapcode: str) -> Any: 
    return SnapDecoder(snapcode).decode()
    
def pack(item: bool | int | float | str | list | tuple | set | dict | None) -> str:
    return SnapEncoder(item).encode()

# --------------------------------------------------
# Local
# --------------------------------------------------

class SnapEncoder:
    def __init__(self, data):
        self.data = data

    def encode(self) -> str:
        return self.encode_item(self.data)
    
    def encode_item(self, item) -> str:
        match item: # TODO encoders[type(item)]
            case None:
                return self.encode_none(item)
            case bool():
                return self.encode_bool(item)
            case int():
                return self.encode_int(item)
            case float():
                return self.encode_float(item)
            case str():
                return self.encode_str(item)
            case list():
                return self.encode_list(item)
            case tuple():
                return self.encode_tuple(item)
            case set():
                return self.encode_set(item)
            case dict():
                return self.encode_dict(item)
            
    def encode_none(self, value: None) -> str:
        return "0n"
            
    def encode_bool(self, value: bool) -> str:
        return "1bT" if value else "1bF"

    def encode_int(self, integer: int) -> str:
        return f"{len(str(integer))}i{integer}"
    
    def encode_float(self, number: float) -> str:
        return f"{len(str(number))}f{number}"
    
    def encode_str(self, string: str) -> str:
        return f"{len(string)}s{string}"
    
    def encode_list(self, items: list) -> str:
        return f"{len(items)}l{"".join(map(self.encode_item, items))}"
    
    def encode_tuple(self, items: tuple) -> str:
        return f"{len(items)}t{"".join(map(self.encode_item, items))}"

    def encode_set(self, items: set) -> str:
        items = tuple(items)
        return f"{len(items)}e{"".join(map(self.encode_item, items))}"
    
    def encode_dict(self, items) -> str:
        return f"{len(items)}d{"".join([f"{self.encode_item(k)}{self.encode_item(v)}" for k, v in items.items()])}"
    

class SnapDecoder:
    def __init__(self, code: str):
        self.code = code
        self.code_length = len(code)
        self.position = 0

    def decode(self):
        return self.decode_item()

    def decode_item(self):
        length: int = self.scan_length()

        item_type = self.consume()

        match item_type:
            case "n":
                return self.decode_none()
            case "b":
                return self.decode_bool()
            case "i":
                return self.decode_int(length)
            case "f":
                return self.decode_float(length)
            case "s":
                return self.decode_str(length)
            case "l":
                return self.decode_list(length)
            case "t":
                return self.decode_tuple(length)
            case "e":
                return self.decode_set(length) 
            case "d":
                return self.decode_dict(length) 
            case _:
                raise Exception() # TODO "message"
            
    def decode_none(self) -> None:
        return None
            
    def decode_bool(self) -> bool:
        return self.consume().upper() == "T" # 1bT | 1bF
    
    def decode_int(self, length: int) -> int:
        return int(self.scan_chunk(length))
    
    def decode_float(self, length: int) -> float:
        return float(self.scan_chunk(length))
    
    def decode_str(self, length: int) -> str:
        return str(self.scan_chunk(length))
    
    def decode_list(self, length: int) -> list:
        return [self.decode_item() for _ in range(length)]
    
    def decode_tuple(self, length: int) -> tuple:
        return tuple([self.decode_item() for _ in range(length)])
    
    def decode_set(self, length: int) -> set:
        return set([self.decode_item() for _ in range(length)])
    
    def decode_dict(self, length: int) -> list:
        return dict([(self.decode_item(), self.decode_item()) for _ in range(length)])
    
    def scan_chunk(self, length: int) -> str:
        return "".join([self.consume() for _ in range(length)])

    def scan_length(self) -> int:
        char: str = self.char()
        length: str = ""

        while char.isdigit():
            length += char
            char = self.next()

        return int(length) # TODO .isdigit()

    def char(self) -> str:
        if self.position >= self.code_length:
            return ""
        
        return self.code[self.position]
    
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
    

if __name__ == "__main__":
    playground()
