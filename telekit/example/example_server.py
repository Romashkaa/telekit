# -*- encoding:utf-8 -*-
import telebot # type: ignore
import telekit

from . import example_handlers # type: ignore

def run_example(token: str):
    bot = telebot.TeleBot(token)
    telekit.Server(bot).polling()