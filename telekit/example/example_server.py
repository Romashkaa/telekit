# -*- encoding:utf-8 -*-
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

# Example message handlers:
"Name: {name}. Age: {age}"
"My name is {name} and I am {age} years old"
"My name is {name}"
"I'm {age} years old"
"""
    )
    bot = telebot.TeleBot(token)
    telekit.Server(bot).polling()