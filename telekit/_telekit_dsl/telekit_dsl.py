# Copyright (c) 2025 Ving Studio, Romashka
# Licensed under the MIT License. See LICENSE file for full terms.

from . import mixin

class TelekitDSL:
    """
    Telekit DSL handler class for integrating domain-specific scripts (like FAQ pages) into your bot.
    
    This class provides convenient methods to load scripts either from a file or from a source string,
    and automatically binds them to bot commands.

    [Learn more on GitHub](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/11_telekit_dsl.md)
    """

    Mixin = mixin.TelekitDSLMixin
    MAGIC_SCENES = mixin.MAGIC_SCENES

    @classmethod
    def from_file(cls, path: str, on_commands: list[str]=["help"]):
        """
        Creates a handler class that loads a Telekit DSL script from a file.

        **Telekit DSL** — this is a custom domain-specific language (DSL) used to create interactive pages, such as FAQs.  
        It allows you to describe the message layout, add images, and buttons for navigation between pages in a convenient, structured format that your bot can easily process.
        
        Args:
            path (str): Path to the DSL script file.
            on_commands (list[str]): List of bot commands that will trigger this DSL.

        [Learn more on GitHub](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/11_telekit_dsl.md)
        """
        class _DefaultTelekitDSLHandler(mixin.TelekitDSLMixin):
            @classmethod
            def init_handler(cls) -> None:
                cls.on.message(on_commands).invoke(cls.start_script)
                cls.analyze_file(path)

    @classmethod
    def from_string(cls, source: str, on_commands: list[str]=["help"]):
        """
        Creates a default handler class that loads a Telekit DSL script from a source string.

        **Telekit DSL** — this is a custom domain-specific language (DSL) used to create interactive pages, such as FAQs.  
        It allows you to describe the message layout, add images, and buttons for navigation between pages in a convenient, structured format that your bot can easily process.
        
        Args:
            source (str): The DSL script as a string.
            on_commands (list[str]): List of bot commands that will trigger this DSL.

        [Learn more on GitHub](https://github.com/Romashkaa/telekit/blob/main/docs/tutorial/11_telekit_dsl.md)
        """
        class _DefaultTelekitDSLHandler(mixin.TelekitDSLMixin):
            @classmethod
            def init_handler(cls) -> None:
                cls.on.message(on_commands).invoke(cls.start_script)
                cls.analyze_source(source)


