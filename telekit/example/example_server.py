# -*- encoding:utf-8 -*-
#
# Copyright (c) 2025 Ving Studio, Romashka
# Licensed under the MIT License. See LICENSE file for full terms.
#

import telebot
import telekit

from . import example_handlers

# telekit.GuideKit("telekit/guidekit/example_guide.txt", ["faq"]).register()

def run_example(token: str):
    print(
"""
Hey! Welcome to the Telekit family.

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