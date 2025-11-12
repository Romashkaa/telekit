# -*- encoding:utf-8 -*-
# Copyright (c) 2025 Ving Studio, Romashka
# Licensed under the MIT License. See LICENSE file for full terms.

import time
import traceback
import sys

from . import init
import telebot # type: ignore

from .logger import logger
server_logger = logger.server
    
def print_exception_message(ex: Exception) -> None:
    tb_str = ''.join(traceback.format_exception(*sys.exc_info()))
    server_logger.critical(f"Polling cycle error : {ex}. Traceback : {tb_str}")
    print(f"- Polling cycle error: {ex}.", tb_str, sep="\n\n")

# ------------------------------------------
# Server
# ------------------------------------------

__all__ = ["Server"]

class Server:
    def __init__(self, bot: telebot.TeleBot | str, catch_exceptions: bool=True):
        self.catch_exceptions = catch_exceptions

        if isinstance(bot, str):
            bot = telebot.TeleBot(bot)
        
        self.bot = bot
        init.init(bot)

    def polling(self):
        """Standard `self.bot.polling(none_stop=True)` polling"""
        while True:
            server_logger.info("Telekit server is polling...")
            print("Telekit server is starting polling...")

            try:
                self.bot.polling(none_stop=True)
            except Exception as exception:
                if self.catch_exceptions:
                    server_logger.critical(f"Polling cycle error [catch_exceptions=False] : {exception}")
                    print_exception_message(exception)
                else:
                    server_logger.fatal(f"[server dead] Polling cycle error [catch_exceptions=False] : {exception}")
                    raise exception
            finally:
                time.sleep(10)

    def long_polling(self, timeout: int = 60):
        """Long `self.bot.polling(none_stop=True, timeout=timeout)` polling with custom timeout"""
        while True:
            server_logger.info("Telekit server is long polling...")
            print(f"Telekit server is long polling with timeout={timeout}...")
            try:
                self.bot.polling(none_stop=True, timeout=timeout)
            except Exception as exception:
                if self.catch_exceptions:
                    server_logger.critical(f"Long polling error [catch_exceptions=False]: {exception}")
                    print_exception_message(exception)
                else:
                    server_logger.fatal(f"[server dead] Long polling error [catch_exceptions=False]: {exception}")
                    raise exception
            finally:
                time.sleep(5)


# Example

def example(token: str):
    import telekit.example as example

    example.example_server.run_example(token)