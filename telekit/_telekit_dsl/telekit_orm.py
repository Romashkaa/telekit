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



#    .-*-: ALPHA VERSION :-*-.    #

class ORM:
    class Scene:
        def __init__(self):
            self._title = None # str
            self._message = None # str
            self._image = None  # path / reference / file_id
            self._use_italics = False  # default: False
            self._parse_mode = None  # html | markdown | None

        # title property
        @property
        def title(self):
            return self._title

        @title.setter
        def title(self, value):
            if not isinstance(value, str):
                raise TypeError("title must be a string")
            self._title = value

        # message property
        @property
        def message(self):
            return self._message

        @message.setter
        def message(self, value):
            if not isinstance(value, str):
                raise TypeError("message must be a string")
            self._message = value

        # image property
        @property
        def image(self):
            return self._image

        @image.setter
        def image(self, value):
            if not isinstance(value, str) and value is not None:
                raise TypeError("image must be a string or None")
            self._image = value

        # use_italics property
        @property
        def use_italics(self):
            return self._use_italics

        @use_italics.setter
        def use_italics(self, value):
            if not isinstance(value, bool):
                raise TypeError("use_italics must be a boolean")
            self._use_italics = value

        # parse_mode property
        @property
        def parse_mode(self):
            return self._parse_mode

        @parse_mode.setter
        def parse_mode(self, value):
            if value not in (None, "html", "markdown"):
                raise ValueError("parse_mode must be 'html', 'markdown', or None")
            self._parse_mode = value

        # context manager support
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    def __init__(self):
        self._scenes: dict[str, "ORM.Scene"] = {}

    def scene(self, name: str, create: bool=True):
        if name in self._scenes:
            return self._scenes[name]
        
        if not create:
            raise KeyError(f"Scene '{name}' does not exist")
        
        self._scenes[name] = self.Scene()
        return self._scenes[name]

    def __getitem__(self, name: str):
        return self.scene(name, False)

    def __setitem__(self, name: str, scene):
        if not isinstance(scene, self.Scene):
            raise TypeError("Value must be a Scene instance")
        self._scenes[name] = scene

if __name__ == "__main__":
    orm = ORM()

    main = orm["main"]
    main.title = "Hello"
    main.message = "Message..."
    main.buttons = {
        "Start 1": orm.scene["start"],
        "Start 2": start,
        "Start 3": "start",
    } 

    with orm.scene("start") as start:
        start.title = "Start..."
        start.message = "Message..."
        start.buttons = {
            "« Back": orm.back,
        }
    print(orm.compile())