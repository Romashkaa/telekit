# 
# Copyright (C) 2026 Romashka
# 
# This file is part of Telekit.
# 
# Telekit is free software: you can redistribute it and/or modify it 
# under the terms of the GNU General Public License as published by 
# the Free Software Foundation, either version 3 of the License, or 
# (at your option) any later version.
# 
# Telekit is distributed in the hope that it will be useful, 
# but WITHOUT ANY WARRANTY; without even the implied warranty 
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See 
# the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License 
# along with Telekit. If not, see <https://www.gnu.org/licenses/>.
# 

from typing import Iterable

from . import mixin

class TelekitDSL:
    """
    Telekit DSL integration class for bot commands.

    Provides methods to load DSL scripts from files or strings and bind them automatically
    to bot commands.

    [Learn more on GitHub](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/11_telekit_dsl.md)
    """

    Mixin = mixin.TelekitDSLMixin
    MAGIC_SCENES = mixin.MAGIC_SCENES

    @classmethod
    def from_file(cls, path: str, on_commands: Iterable[str]=("start",)):
        """
        Creates a handler class that loads a Telekit DSL script from a file.

        Args:
            path (str): Path to the DSL script file.
            on_commands (Iterable[str]): Commands that will trigger this DSL.

        [Learn more on GitHub](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/11_telekit_dsl.md)
        """
        @classmethod
        def init_handler(cls) -> None:
            cls.analyze_file(path)
            cls.on.command(*on_commands).invoke(cls.start_script)

        class_name = f"_DLSFromPath_{id(path)}"
        class_dict = {
            "init_handler": init_handler
        }

        return type(class_name, (mixin.TelekitDSLMixin,), class_dict)


    @classmethod
    def from_string(cls, script: str, on_commands: Iterable[str]=("start",)):
        """
        Creates a default handler class that loads a Telekit DSL script from a source string.

        Args:
            script (str): The DSL script as a string.
            on_commands (Iterable[str]): Commands that will trigger this DSL.

        [Learn more on GitHub](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/11_telekit_dsl.md)
        """
        @classmethod
        def init_handler(cls) -> None:
            cls.analyze_string(script)
            cls.on.command(*on_commands).invoke(cls.start_script)

        class_name = f"_DSLFromString_{id(script)}"
        class_dict = {
            "init_handler": init_handler
        }

        return type(class_name, (mixin.TelekitDSLMixin,), class_dict)