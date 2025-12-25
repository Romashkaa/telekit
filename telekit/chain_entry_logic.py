# Copyright (c) 2025 Ving Studio, Romashka
# Licensed under the MIT License. See LICENSE file for full terms.

# Standard library
import typing
import telebot
from typing import Callable, Any

# Third-party packages
import charset_normalizer
from telebot.types import Message
from .chain_base import ChainBase

if typing.TYPE_CHECKING:
    from .chain import Chain  # only for type hints

from dataclasses import dataclass

@dataclass
class TextDocument:
    message: telebot.types.Message
    document: telebot.types.Document
    file_name: str
    encoding: str
    text: str

class ChainEntryLogic(ChainBase):
    def entry(self, 
              filter_message: Callable[[Message], bool] | None=None,
              delete_user_response: bool=False) -> Callable[[Callable[[Message], Any]], None]:
        """
        Decorator for registering an entry callback with optional message filtering.

        ---
        ## Example:
        ```
        # Receive any message type:
        @self.chain.entry(
            filter_message=lambda message: bool(message.text),
            delete_user_response=True)
        def handler(message):
            print(message.text)
        ```

        ## Example 2 (Cancel button):
        ```python
        # Receive any message type:
        @self.chain.entry()
        def handler(message):
            print(message.text)

        self.chain.set_inline_keyboard(
            {   
                "🚫 Cancel": self.display_cancel,
            }
        )
        ```
        ---

        Args:
            filter_message (Callable[[Message], bool] | None): 
                A filter function that takes a Message and returns True if it should be processed.
            delete_user_response (bool): 
                If True, deletes the user's message after receiving it.
        """
        def wrapper(func: Callable[[Message], Any]) -> None:
            def callback(message: Message) -> bool:
                if delete_user_response:
                    self.sender.delete_message(message, True)
                    
                if filter_message and not filter_message(message):
                    return False
                
                self._got_response_or_callback()
                func(message)
                return True
            
            self.handler.set_entry_callback(callback)

        return wrapper 
    
    def entry_text(self, 
              filter_message: Callable[[Message, str], bool] | None=None,
              delete_user_response: bool=False) -> Callable[[Callable[[Message, str], Any]], None]:
        """
        Decorator for registering a text-only entry callback with optional message filtering.

        ---
        ## Example:
        ```
        @self.chain.entry_text(
            filter_message=lambda _, name: " " not in name)
        def name_handler(message, name: str):
            print(name)
        ```
        ## Example 2 (Suggestions):
        ```
        # Receive text message:
        @self.chain.entry_text()
        def name_handler(message, name: str):
            print(name)

        # Add inline keyboard with suggested options:
        self.chain.set_entry_suggestions(["Romashka", "NotRomashka"])
        ```
        ---

        Args:
            filter_message (Callable[[Message, str], bool] | None): 
                A filter function that takes a Message and its text, 
                returns True if it should be processed.
            delete_user_response (bool): 
                If True, deletes the user's message after receiving it.
        """
        def wrapper(func: Callable[[Message, str], Any]) -> None:
            def callback(message: Message) -> bool:
                if delete_user_response:
                    self.sender.delete_message(message, True)

                if not message.text:
                    return False # Only text messages
                    
                if filter_message and not filter_message(message, message.text):
                    return False
                
                self._got_response_or_callback()
                func(message, message.text)
                return True
            
            self.handler.set_entry_callback(callback)

        return wrapper
    
    def entry_photo(self, 
            filter_message: Callable[[Message, list[telebot.types.PhotoSize]], bool] | None=None,
            delete_user_response: bool=False) -> Callable[[Callable[[Message, list[telebot.types.PhotoSize]], Any]], None]:
        """
        Decorator for registering a callback that only processes messages containing photos.
        Optionally applies a custom filter or deletes the user's message.

        ---
        ## Example:
        ```
        @self.chain.entry_photo()
        def save_photos(message: Message, photos: list[telebot.types.PhotoSize]):
            for i, photo in enumerate(photos):
                file_info = bot.get_file(photo.file_id)
                downloaded_file = bot.download_file(file_info.file_path)
                filename = f"{message.message_id}_{i}.jpg"
                with open(filename, "wb") as f:
                    f.write(downloaded_file)
        ```
        ---

        Args:
            filter_message (Callable[[Message, list[telebot.types.PhotoSize]], bool] | None): 
                A custom filter function that takes a Message and its list of PhotoSize objects. 
                Returns True if the message should be processed.
            delete_user_response (bool): 
                If True, the user's photo message will be deleted after being received.
        """
        def wrapper(func: Callable[[Message, list[telebot.types.PhotoSize]], Any]) -> None:
            def callback(message: Message) -> bool:
                if delete_user_response:
                    self.sender.delete_message(message, True)

                if not message.photo:
                    return False # Only photos
                    
                if filter_message and not filter_message(message, message.photo):
                    return False
                
                self._got_response_or_callback()
                func(message, message.photo)
                return True
            
            self.handler.set_entry_callback(callback)

        return wrapper
    
    def entry_document(self, 
            filter_message: Callable[[Message, telebot.types.Document], bool] | None=None,
            allowed_extensions: tuple[str, ...] | None = None,
            delete_user_response: bool=False) -> Callable[[Callable[[Message, telebot.types.Document], Any]], None]:
        """
        Decorator for registering a callback that processes messages containing documents.

        This decorator allows filtering by file extensions, applying a custom filter, 
        and optionally deleting the user's document message after processing.

        ---
        ## Example:
        ```
        @self.chain.entry_document(allowed_extensions=(".zip",))
        def doc_handler(message, document: telebot.types.Document):
            print(document.file_name, document)
        ```
        ---

        Args:
            filter_message (Callable[[Message, Document], bool] | None): 
                Optional function to filter messages. Receives the message and document,
                should return True if the message should be processed.
            allowed_extensions (tuple[str, ...] | None):
                Only documents with these file extensions will be processed.
                Example: (".txt", ".js")
                If None, all document types are allowed.
            delete_user_response (bool): 
                If True, deletes the user's document message after it is received.
        """
        def wrapper(func: Callable[[Message, telebot.types.Document], Any]) -> None:
            def callback(message: Message) -> bool:
                if delete_user_response:
                    self.sender.delete_message(message, True)

                if not message.document:
                    return False # only documents
                
                if message.content_type != 'document':
                    return False # only documents
                
                if allowed_extensions and not str(message.document.file_name).endswith(allowed_extensions):
                    return False # only allowed_extensions
                    
                if filter_message and not filter_message(message, message.document):
                    return False # only filtered
                
                self._got_response_or_callback()
                func(message, message.document)
                return True # success
            
            self.handler.set_entry_callback(callback)

        return wrapper
    
    def entry_text_document(self, 
            filter_message: Callable[[Message, TextDocument], bool] | None=None,
            allowed_extensions: tuple[str, ...] = (".txt",),
            encoding: str | None = None,
            decoding_errors: str = "strict",
            delete_user_response: bool=False) -> Callable[[Callable[[Message, TextDocument], Any]], None]:
        """
        Decorator for registering a callback that processes text-based documents.

        This decorator automatically downloads the document, detects or applies a
        specified encoding, decodes the text, wraps it in a TextDocument object, 
        and passes it to the callback.

        ---
        ## Example:
        ```
        # Receive a text document (Telekit auto-detects encoding):
        @self.chain.entry_text_document(allowed_extensions=(".txt", ".js", ".py"))
        def text_document_handler(message, text_document: telekit.types.TextDocument):
            print(
                text_document.text,      # "Example\\n..."
                text_document.file_name, # "example.txt"
                text_document.encoding,  # "utf-8"
                text_document.document   # <telebot.types.Document>
            )
        ```
        ---

        Args:
            filter_message (Callable[[Message, TextDocument], bool] | None):
                Optional function to filter messages. Receives the message and TextDocument,
                should return True if the message should be processed.
            allowed_extensions (tuple[str, ...]):
                File extensions that are allowed. Defaults to (".txt",).
            encoding (str | None):
                Encoding to decode the document. If None, charset-normalizer is used to detect it.
            decoding_errors (str):
                Error handling strategy for decoding. Defaults to "strict".
                Other options: "ignore", "replace".
            delete_user_response (bool):
                If True, deletes the user's document message after it is received.
        """
        def wrapper(func: Callable[[Message, TextDocument], Any]) -> None:
            def callback(message: Message) -> bool:
                if delete_user_response:
                    self.sender.delete_message(message, True)

                if not message.document:
                    return False # only documents
                
                if message.content_type != 'document':
                    return False # only documents
                
                file_name = str(message.document.file_name)
                
                if not file_name.endswith(allowed_extensions):
                    return False # only allowed_extensions
                
                try:
                    file_info = self.bot.get_file(message.document.file_id)
                    downloaded_file = self.bot.download_file(str(file_info.file_path))

                    if not encoding:
                        results = charset_normalizer.from_bytes(downloaded_file)
                        best_guess = results.best()

                        if not best_guess:
                            return False # unknown encoding
                        
                        _encoding = best_guess.encoding
                    else:
                        _encoding = encoding

                    text = downloaded_file.decode(_encoding, decoding_errors)
                except Exception as extension:
                    print(extension)
                    return False
                
                text_doc = TextDocument(
                    message, message.document,
                    file_name, _encoding, text
                )
                    
                if filter_message and not filter_message(message, text_doc):
                    return False # only filtered
                
                self._got_response_or_callback()
                func(message, text_doc)
                return True # success
            
            self.handler.set_entry_callback(callback)

        return wrapper

    def entry_location(
        self,
        filter_message: Callable[[Message, telebot.types.Location], bool] | None = None,
        delete_user_response: bool = False
    ) -> Callable[[Callable[[Message, telebot.types.Location], Any]], None]:
        """
        Decorator for registering a callback that processes messages containing a location.

        ---
        ## Example:
        ```
        @self.chain.entry_location()
        def location_handler(message, location: telebot.types.Location):
            print(location.latitude, location.longitude)
        ```
        ---

        Args:
            filter_message: Optional function to filter messages. Receives message and location,
                            should return True if the message should be processed.
            delete_user_response: If True, deletes the user's location message after it is received.
        """
        def wrapper(func: Callable[[Message, telebot.types.Location], Any]) -> None:
            def callback(message: Message) -> bool:
                if not message.location:
                    return False  # only location messages
                
                loc = message.location

                if filter_message and not filter_message(message, loc):
                    return False  # only filtered
                
                if delete_user_response:
                    self.sender.delete_message(message, True)
                
                self._got_response_or_callback()
                func(message, loc)
                return True  # success
            
            self.handler.set_entry_callback(callback)
        return wrapper