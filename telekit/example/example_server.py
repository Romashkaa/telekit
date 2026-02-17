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

import telebot
import telekit

from . import example_handlers

def run_example(token: str):
    print(
"""
Welcome to the Telekit family!

# Example commands:
/start - simple counter
/entry - sequence for collecting user data + using Vault as a DB
/help  - custom help implementation + scanning files using `chapters`
/faq   - extended help page written in Telekit DSL for FAQ pages

# Example message handlers (+ styles example):
"Name: {name}. Age: {age}"
"My name is {name} and I am {age} years old"
"My name is {name}"
"I'm {age} years old"
"""
    )
    bot = telebot.TeleBot(token)
    telekit.Server(bot).polling()