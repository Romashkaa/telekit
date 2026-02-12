from typing import Any, overload

import telebot
from telebot.types import Message

from ._logger import logger
library = logger.library
from ._chain import Chain
from ._callback_query_handler import CallbackQueryHandler
from ._user import User
from ._on import On
from . import senders

class Handler:
    
    # Base Class Attributes
    bot: telebot.TeleBot
    _default_sender_type: type[senders.BaseSender] = senders.BaseSender

    # Subclas Attributes
    on:  On

    # Instance Attributes
    user: User
    chain: Chain
    message: Message

    # -----------------------------------------------------
    # Initialization of all Handlers
    # -----------------------------------------------------

    handlers: list[type['Handler']] = []

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        Handler.handlers.append(cls)
    
    @classmethod
    def _init(cls, bot: telebot.TeleBot):
        """
        Initializes the bot instance for the handler class and sets up all registered handlers.

        For each subclass of Handler, this method attaches an On instance for message handling 
        and calls its `init_handler` method to register the message callbacks.

        Args:
            bot (`TeleBot`): The Telegram bot instance to be used for sending messages.
        """
        if cls is not Handler:
            raise RuntimeError("Do not call `Handler.init` on a subclass. Use the base Handler class only.")

        cls.bot = bot
        cls.handlers_dict = {}

        for handler in cls.handlers:
            handler.on = On(handler, bot)
            handler.init_handler()

            cls.handlers_dict[handler.__name__] = handler
    
    @classmethod
    def init_handler(cls) -> None:
        """
        Initializes the message handler. 
        You should redefine it in your handler class to add message handlers:

        ```python
        class HelpHandler(telekit.Handler):

            @classmethod
            def init_handler(cls) -> None:
                cls.on.command("help").invoke(cls.handle_help)
        ```
        """
        pass

    @classmethod
    def use_sender(cls, sender_type: type[senders.BaseSender]):
        """
        Overrides the default sender type for this handler subclass.

        This method allows configuring which `Sender` implementation will be
        used when creating new `Chain` instances associated with the handler.

        The override is **scoped to the subclass** and cannot be applied to the
        base `telekit.Handler` class itself. Attempting to call this method on the base
        class raises a `TypeError` to prevent unintended global side effects.

        :param sender_type: The `Sender` class to use as the default for this handler subclass.
        :type sender_type: `type[senders.BaseSender]`
        
        :raises TypeError: If called on the base `telekit.Handler` class.
        """
        if cls is Handler:
            raise TypeError("Cannot override sender type globally on the base Handler class")
        cls._default_sender_type = sender_type

    # -----------------------------------------------------
    # Initialization of handlers Instances
    # -----------------------------------------------------

    def __init__(self, message: Message):
        self.message: Message = message
        self.user = User(self.message.chat.id, self.message.from_user)
        self.new_chain()

    def handle(self) -> Any:
        """
        Recommended method _(name)_ to serve as a unified entry point 
        for your handler. The library does not call this method automatically, 
        but having a single `handle` method is convenient when delegating 
        control to another handler via `handoff` or similar mechanisms. 

        Using one `handle` method to start processing the message 
        avoids the need for multiple custom entry methods 
        like `start` or `handle_start`.
        """
        library.warning("Handler `handle` was called but not overridden; no logic executed.")
        return

    # -----------------------------------------------------
    # Methods
    # -----------------------------------------------------

    def simulate_user_message(self, message_text: str) -> None:
        """
        Simulates a user sending a message to the bot.

        Useful for testing, triggering handlers programmatically, 
        or switching between commands without sending real Telegram messages.

        Args:
            message_text (`str`): The text of the message to simulate.

        Example:
            >>> self.simulate_user_message("/start")
        """
        CallbackQueryHandler().simulate(self.message, message_text)

    def delete_user_initial_message(self):
        """
        Deletes the user's original message associated with this handler (`self.message`):

        >>> self.chain.sender.delete_message(self.message)
        """
        self.chain.sender.delete_message(self.message)
    
    def new_chain(self):
        """
        Creates a new `Chain` instance and assigns it to the handler.

        The previous `self.chain` (if present) is discarded and fully
        replaced with a fresh Chain configured with the current chat ID
        and default sender type.

        Use this when you want to completely reset the handler’s chain
        state, including previous message id, input handlers, and sender configuration:

        >>> self.new_chain()
        """
        if hasattr(self, "chain"):
            del self.chain

        self.chain = Chain(
            chat_id     = self.message.chat.id,
            sender_type = self._default_sender_type
        )

    def get_local_chain(self) -> Chain:
        """
        Returns a new independent `Chain` instance without modifying
        the handler's current `self.chain`.

        The returned chain is fully isolated and does not retain or affect
        any state from the handler's main chain. 
        
        Unlike `new_chain()`, this method does not replace `self.chain`.
        """
        return Chain(
            chat_id     = self.message.chat.id,
            sender_type = self._default_sender_type
        )
    
    @overload
    def handoff(self, handler: str) -> "Handler": ...

    @overload
    def handoff[THandler: "Handler"](self, handler: type[THandler]) -> THandler: ...
    
    def handoff(self, handler: str | type["Handler"]) -> "Handler":
        """
        Transfers control to another handler while preserving chain continuity.

        The newly created handler instance receives:

        - the **same user's initial message**
        - the **previous message sent by the current chain**, allowing editing

        This enables seamless navigation between handlers:

        ```
        self.chain.set_inline_keyboard(
            {
                "Start Page »": self.handoff(StartHandler).handle
            }
        )
        ```

        The target handler can be provided either as:

        - **string name** - resolved via the handler registry (`handlers_dict`)
        - **handler class** - instantiated directly

        >>> self.handoff("StartHandler").handle()
        >>> self.handoff(StartHandler).handle()

        :param handler: Target handler name or `Handler` subclass to transfer control to.
        :type handler: `str` | `type[Handler]`

        :return: A newly created handler instance.

        :raises NameError: If a string name is provided but no registered handler exists.
        :raises TypeError: If the provided value is not a `Handler` subclass.
        :rtype: `Handler`
        """
        if isinstance(handler, str):
            if handler in self.handlers_dict:
                handler = self.handlers_dict[handler]
            else:
                raise NameError(f"{type(self).__name__}().handoff(\"{handler}\") <- Handler does not exist")

        if not (isinstance(handler, type) and issubclass(handler, Handler)):
            raise TypeError(f"{type(self).__name__}().handoff(HERE) <- Expected `Handler` type")
        
        handler_instance = handler(self.message)
        handler_instance.chain._set_previous_message(self.chain.get_previous_message())
        
        return handler_instance
    
    def freeze(self, func, *args):
        """
        Return a zero-argument callback that invokes the given function
        with the provided arguments.

        Args:
            func (Callable): The function to be executed when the callback is triggered.
            *args: Arguments that will be passed to the function upon execution.

        Returns:
            Callable: A wrapper function that calls `func(*args)` when invoked.

        Example:
            >>> btn = self.freeze((lambda a, b: a + b), 2, 3)
            >>> btn() # 5
        """
        def wrapper():
            func(*args)

        return wrapper

# def accepts_parameter(func: Callable) -> bool:
#     """
#     Checks if the function accepts at least one parameter,
#     ignoring 'self' for class methods.
#     """
#     sig = inspect.signature(func)
#     params = list(sig.parameters.values())

#     if params and params[0].name == "cls":
#         params = params[1:]

#     return len(params) > 0
