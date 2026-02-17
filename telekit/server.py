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

import time
import traceback
import sys

from . import _init
import telebot

from ._logger import logger
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
        _init.init(bot)

    def polling(self):
        """Standard `self.bot.polling(none_stop=True)` polling"""
        while True:
            server_logger.info("Telekit server is polling...")
            print("Telekit server has started polling...")

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
            print(f"Telekit server started long polling with timeout={timeout}...")
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