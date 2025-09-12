# type: ignore

# # MIT License  
# © 2025 Romashka (Ving Studio)   
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
#
# Documentation: https://t.me/snapvault_io

import os, time

from . import snapcode

import sqlite3
from typing import Any, NoReturn
import collections
from enum import Enum

class Status(Enum):
    ALL = 1

class EasyDataBaseError(Exception):
    pass


class BaseDB:
    def _base_init(self, path: str, table_name: str | None=None):
        if not path.endswith((".db", ".sqlite")):
            path += ".db"

        self.file_name = os.path.basename(path)
        self.path = path
        
        if table_name is None:
            self.table_name = "_".join(self.file_name.split(".")[:-1])
        else:
            self.table_name = table_name

        self._create_table()

    def _connect(self):
        '''Function to connect to the database.'''
        try:
            return sqlite3.connect(self.path)
        except:
            raise EasyDataBaseError(f"Unable to connect to database ({self.file_name})")
        
    def _execute(self, query: str, parameters: tuple[Any] | None=None) -> sqlite3.Cursor:
        failed: int = 0

        while True:
            try:
                with self._connect() as conn:
                    cursor = conn.cursor()
                    if parameters:
                        cursor.execute(query, parameters)
                    else:
                        cursor.execute(query)
                    conn.commit()
                    return cursor
            except BaseException:
                if failed > 10:
                    raise EasyDataBaseError(f"Unable to execute \"{query}\" with parameters: {parameters}. ({self.file_name}: {self.table_name})")

            time.sleep(failed/10)
            failed += 1
        
    def _fetch_one(self, query: str, params: tuple[Any] | None=None):
        cursor = self._execute(query, params)
        return cursor.fetchone()

    def _create_table(self) -> NoReturn | None:
        raise NotImplementedError()
    
    def _prepare_string(self, string: str) -> str:
        return str(string).replace('"', "'")


class Vault(BaseDB):
    def __init__(self, path: str, table_name: str | None=None, key_field_name: str="key", value_field_name: str="value"):
        '''Constructor. Defines the database file.'''

        self.key_field_name = key_field_name
        self.value_field_name = value_field_name

        self._base_init(path, table_name)

    def _create_table(self):
        self._execute(f"""
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                {self.key_field_name} TEXT,
                {self.value_field_name} TEXT
            )
        """)

    # ------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------

    def drop_table(self) -> None:
        self._execute(f"DROP TABLE IF EXISTS {self.table_name}")

    def length(self) -> int:
        query = f"SELECT COUNT(*) FROM {self.table_name}"
        result = self._fetch_one(query)
        return result[0] if result else 0

    def contains(self, key: collections.abc.Hashable) -> bool: # type: ignore
        query = f"SELECT 1 FROM {self.table_name} WHERE {self.key_field_name} = ?"
        result = self._fetch_one(query, (snapcode.pack(key),))
        return result is not None

    def set(self, key: collections.abc.Hashable, value: Any): # type: ignore
        if self.contains(key):
            self._update(key, value)
        else:
            self._insert(key, value)

    def _insert(self, key, value):
        assert isinstance(key, collections.abc.Hashable), f"Key '{key}' is unhashable (e.g., list, dict, set...)"
        
        key = snapcode.pack(key)
        serialized_value = snapcode.pack(value)

        self._execute(f"""
            INSERT INTO {self.table_name}
            VALUES (?, ?);
        """, (key, serialized_value))

    def _update(self, key, value):
        assert isinstance(key, collections.abc.Hashable), f"Key '{key}' is unhashable (e.g., list, dict, set...)"

        key = snapcode.pack(key)
        serialized_value = snapcode.pack(value)

        self._execute(f"""
            UPDATE {self.table_name}
            SET {self.value_field_name} = ?
            WHERE {self.key_field_name} = ?;
        """, (serialized_value, key))

    def push(self, value, key_handler=None):
        new_key = self.length() + 1

        if key_handler:
            new_key = key_handler(new_key)
            
        self.set(new_key, value)
        return new_key

    def get(self, key, default: Any=None):
        row = self._fetch_one(f"""
            SELECT {self.value_field_name} FROM {self.table_name}
            WHERE {self.key_field_name} = ?;
        """, (snapcode.pack(key),))

        return snapcode.unpack(row[0]) if row else default
    
    def _get_keys_by_value(self, value):
        cursor = self._execute(f"""
            SELECT {self.key_field_name} FROM {self.table_name}
            WHERE {self.value_field_name} = ?;
        """, (snapcode.pack(value),))

        rows = cursor.fetchall()

        if not rows:
            return ()

        return tuple(snapcode.unpack(row[0]) for row in rows)

    def delete(self, key) -> int:
        cursor = self._execute(f"""
            DELETE FROM {self.table_name}
            WHERE {self.key_field_name} = ?;
        """, (snapcode.pack(key),))

        return cursor.rowcount

    def clear(self) -> int:
        cursor = self._execute(f"""
            DELETE FROM {self.table_name}
        """)

        return cursor.rowcount

    def all(self) -> dict:
        cursor = self._execute(f"""
            SELECT {self.key_field_name}, {self.value_field_name} FROM {self.table_name}
            ORDER BY rowid DESC
        """)

        rows = cursor.fetchall()

        return {
            snapcode.unpack(key): snapcode.unpack(serialized_value)
                for key, serialized_value in rows
        }
    
    def keys(self, value=Status.ALL) -> tuple:
        if value is Status.ALL:
            return tuple(self.all())
        
        return self._get_keys_by_value(value)

    def values(self, key=Status.ALL) -> tuple:
        if key is Status.ALL:
            return tuple(self.all().values())
        
        value = self.get(key)
        
        return (value,) if value else ()

    def items(self):
        return self.all().items()
    
    def update(self, items: dict[collections.abc.Hashable]) -> None:
        for key, value in items.items():
            self.set(key, value)

    def output(self) -> None:
        print(*self.all().items(), sep="\n")

    def filter(self, func) -> dict:
        return {k: v for k, v in self.all().items() if func(k, v)}
    
    def map(self, func):
        updated = {k: func(v) for k, v in self.all().items()}
        self.update(updated)
    
    def last_modified(self) -> float:
        return os.path.getmtime(self.path)

    # ------------------------------------------------------------------
    # Magic Methods
    # ------------------------------------------------------------------

    def __bool__(self):
        return bool(self.length())

    def __len__(self) -> int:
        return self.length()

    def __contains__(self, item) -> bool:
        return self.contains(item)

    def __getitem__(self, key, default=None):
        return self.get(key, default)

    def __setitem__(self, key, value):
        self.set(key, value)

    def __delitem__(self, key):
        self.delete(key)

    def __iter__(self):
        return iter(self.all())

    def __repr__(self):
        return f"<SnapVault-Table {self.table_name}: {self.all()}>"