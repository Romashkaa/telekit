# Handler

The `Handler` class in Telekit serves as the base for all bot message handlers.  
It provides a structured way to manage incoming messages, commands, and user interactions.  

Each subclass of `Handler` should implement its own logic by overriding `init_handler(cls)` to register triggers and defining instance methods to handle the responses.  

Below is a concise overview of the main attributes and methods available in the `Handler` class:

- `bot` - class attribute, instance of `telebot.TeleBot` used to interact with the Telegram API
- `on` - class attribute, instance of `On` for registering message handlers  
- `user` - instance attribute, `User` object representing the user who sent the message  
- `chain` - instance attribute, `Chain` object used to build and send messages  
- `message` - instance attribute, `Message` object from Telegram
- `handlers` - list of all subclasses of `Handler` that have been created (All your Handlers)
- `init_handler(cls)` - class method that should be overridden to register message handlers  
- `simulate_user_message(self, message_text: str)` - simulates a user sending a message for testing or triggering handlers programmatically
- `delete_user_initial_message(self)` - deletes the user's original message that started the chain  
- `new_chain(self)` - creates a new `Chain` object for the current chat, assigns it to `self.chain` of the handler, does not return anything  
- `get_local_chain(self) -> Chain` - creates a new `Chain` object for the current chat and returns it without modifying `self.chain` 
- `__init__(self, message: Message)` - initializes the handler instance with a message, creates a `User` object and a `Chain`

[Back to tutorial](../tutorial/5_handler.md)
