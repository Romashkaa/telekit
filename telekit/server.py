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
from typing import Optional

from . import _init, _state
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
    def __init__(
        self, 
        bot: telebot.TeleBot | str, 
        *, 
        auto_restart: bool=True, 
        debug: bool = False
    ):
        
        self._auto_restart = auto_restart
        _state.TelekitState.DEBUG = debug

        if isinstance(bot, str):
            bot = telebot.TeleBot(bot)
        
        self._bot = bot
        _init.init(bot)

    def infinity_polling(
            self, 
            *, 
            timeout: Optional[int]=20, 
            skip_pending: Optional[bool]=False, 
            long_polling_timeout: Optional[int]=20, 
            allowed_updates: Optional[list[str]]=None,
            restart_on_change: Optional[bool]=False, 
            path_to_watch: Optional[str]=None, 
            **kwargs
        ):
        """
        Wrap polling with infinite loop and exception handling to avoid bot stops polling.

        .. note::

            Install watchdog and psutil before using restart_on_change option.

        :param timeout: Request connection timeout.
        :type timeout: :obj:`int`

        :param long_polling_timeout: Timeout in seconds for long polling (see API docs)
        :type long_polling_timeout: :obj:`int`

        :param skip_pending: skip old updates
        :type skip_pending: :obj:`bool`

        :param logger_level: Custom (different from logger itself) logging level for infinity_polling logging.
            Use logger levels from logging as a value. None/NOTSET = no error logging
        :type logger_level: :obj:`int`.

        :param allowed_updates: A list of the update types you want your bot to receive.
            For example, specify [“message”, “edited_channel_post”, “callback_query”] to only receive updates of these types.
            See util.update_types for a complete list of available update types.
            Specify an empty list to receive all update types except chat_member (default).
            If not specified, the previous setting will be used.
            Please note that this parameter doesn't affect updates created before the call to the get_updates,
            so unwanted updates may be received for a short period of time.
        :type allowed_updates: :obj:`list` of :obj:`str`

        :param restart_on_change: Restart a file on file(s) change. Defaults to False
        :type restart_on_change: :obj:`bool`

        :param path_to_watch: Path to watch for changes. Defaults to current directory
        :type path_to_watch: :obj:`str`

        :return:
        """
        self._bot.infinity_polling(
            timeout = timeout,
            skip_pending = skip_pending,
            long_polling_timeout = long_polling_timeout,
            allowed_updates = allowed_updates,
            restart_on_change = restart_on_change,
            path_to_watch = path_to_watch,
            **kwargs
        )

    def polling(self):
        """Standard `bot.polling(none_stop=True)` polling"""
        while True:
            server_logger.info("Telekit server is polling...")
            print("Telekit server has started polling...")

            try:
                self._bot.polling(none_stop=True)
            except Exception as exception:
                if self._auto_restart:
                    server_logger.critical(f"Polling cycle error [auto_restart={self._auto_restart}] : {exception}")
                    print_exception_message(exception)
                else:
                    server_logger.fatal(f"[server dead] Polling cycle error [auto_restart={self._auto_restart}] : {exception}")
                    raise exception
            finally:
                time.sleep(10)

    def long_polling(self, *, timeout: int = 60):
        """Long `bot.polling(none_stop=True, timeout=timeout)` polling with custom timeout"""
        while True:
            server_logger.info("Telekit server is long polling...")
            print(f"Telekit server started long polling with timeout={timeout}...")
            try:
                self._bot.polling(none_stop=True, timeout=timeout)
            except Exception as exception:
                if self._auto_restart:
                    server_logger.critical(f"Long polling error [auto_restart={self._auto_restart}]: {exception}")
                    print_exception_message(exception)
                else:
                    server_logger.fatal(f"[server dead] Long polling error [auto_restart={self._auto_restart}]: {exception}")
                    raise exception
            finally:
                time.sleep(5)


# Example

def example(token: str):
    import telekit.example as example

    example.example_server.run_example(token)