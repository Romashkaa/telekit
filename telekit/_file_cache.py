import hashlib
import os
from typing import Any, Literal

from telebot.types import Message

from ._logger import logger
library = logger.library

FileKind = Literal["photo", "document", "video", "animation", "audio", "voice", "video_note"]

# for BaseSender
FILE_KINDS: tuple[FileKind, ...] = (
    "photo", "document", "video", "animation", "audio", "voice", "video_note"
)

CacheEntry = tuple[str, str, str]
"""(db key, stat signature, content hash)"""


class FileIdCache:
    """Caches Telegram file_id for LOCAL files, validated by a content hash."""

    enabled: bool = True
    path: str = "file_cache"
    table_name: str = "file_ids"

    _vault: Any = None

    @classmethod
    def configure(
        cls, *,
        path: str | None = None,
        enabled: bool | None = None,
        table_name: str | None = None,
    ) -> None:
        if path is not None and path != cls.path:
            cls.path = path
            cls._vault = None
        if table_name is not None and table_name != cls.table_name:
            cls.table_name = table_name
            cls._vault = None
        if enabled is not None:
            cls.enabled = enabled

    @classmethod
    def _get_vault(cls):
        if cls._vault is None:
            from telekit import Vault
            cls._vault = Vault(
                path=cls.path,
                table_name=cls.table_name,
                key_field_name="source",
                value_field_name="file_id",
            )
        return cls._vault

    # ---------------- hashing ----------------

    @staticmethod
    def file_hash(path: str) -> str | None:
        h = hashlib.sha256()
        try:
            with open(path, "rb") as f:
                while chunk := f.read(1024 * 1024):
                    h.update(chunk)
        except OSError:
            return None
        return h.hexdigest()

    # ---------------- storage ----------------

    @classmethod
    def forget(cls, key: str) -> None:
        try:
            cls._get_vault()[key] = ""  # empty value == miss
        except Exception as e:
            library.warning(f"file_id cache write failed: {e}")

    @staticmethod
    def extract(kind: str, message: Message | None) -> str | None:
        if message is None:
            return None
        if kind == "photo":
            return message.photo[-1].file_id if message.photo else None
        obj = getattr(message, kind, None)
        return getattr(obj, "file_id", None)

    @classmethod
    def lookup(cls, bot_id: str, kind: str, source: str) -> tuple[str | None, CacheEntry | None]:
        """
        Returns (file_id | None, entry | None).
        entry is None if the file can't be read.
        A hash is computed only when size/mtime differ from the stored record.
        """
        try:
            st = os.stat(source)
        except OSError:
            return None, None

        key = f"{bot_id}|{kind}|{os.path.abspath(source)}"
        sig = f"{st.st_size}:{st.st_mtime_ns}"

        stored_sig = stored_hash = stored_id = ""
        try:
            value = cls._get_vault().get(key, None)
            if value:
                parts = value.split("|")
                if len(parts) == 3:
                    stored_sig, stored_hash, stored_id = parts
        except Exception as e:
            library.warning(f"file_id cache read failed: {e}")

        # fast path: nothing changed
        if stored_id and stored_sig == sig:
            return stored_id, (key, sig, stored_hash)

        # slow path: size/mtime changed (or no record) -> hash the content
        file_hash = cls.file_hash(source)
        if file_hash is None:
            return None, None

        if stored_id and stored_hash == file_hash:
            # content is the same, only the stat changed: refresh the record
            cls.set(key, sig, file_hash, stored_id)
            return stored_id, (key, sig, file_hash)

        return None, (key, sig, file_hash)

    @classmethod
    def set(cls, key: str, sig: str, file_hash: str, file_id: str) -> None:
        try:
            cls._get_vault()[key] = f"{sig}|{file_hash}|{file_id}"
        except Exception as e:
            library.warning(f"file_id cache write failed: {e}")