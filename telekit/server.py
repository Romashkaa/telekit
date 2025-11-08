# -*- encoding:utf-8 -*-
import time
import traceback
import sys

from . import init
import telebot # type: ignore

from . import logger
server_logger = logger.logger.server
    
def print_exception_message(ex: Exception) -> None:
    tb_str = ''.join(traceback.format_exception(*sys.exc_info()))
    server_logger.critical(f"Polling cycle error : {ex}. Traceback : {tb_str}")
    print(f"- Polling cycle error: {ex}.", tb_str, sep="\n\n")

# ------------------------------------------
# Server
# ------------------------------------------

__all__ = ["Server"]

class Server:
    def __init__(self, bot: telebot.TeleBot, catch_exceptions: bool=True):
        self.catch_exceptions = catch_exceptions
        
        self.bot = bot
        init.init(bot)

    def polling(self):
        while True:
            server_logger.info("Telekit server is polling...")
            print("Telekit server is starting polling...")

            try:
                self.bot.polling(none_stop=True)
            except Exception as exception:
                if self.catch_exceptions:
                    print_exception_message(exception)
                else:
                    server_logger.critical(f"Polling cycle error [catch_exceptions=False] : {exception}")
                    raise exception
            finally:
                time.sleep(10)

# Example

def example(token: str):
    import telekit.example as example

    example.example_server.run_example(token)