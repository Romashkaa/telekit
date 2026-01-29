# Getting Started

Telekit makes building Telegram bots fast and clean.  
Even if you’ve never written one before, this guide will take you from zero to a working bot in minutes.

## Installation

Telekit is published in [PyPI](https://pypi.org/project/telekit/), so it can be installed with command:

```
pip install telekit
```

## Getting a Bot Token

First, get your bot token from [BotFather](https://t.me/BotFather). 
After that, you can run the example bot to explore Telekit’s basic features:

```py
import telekit # import library

telekit.example(BOT_TOKEN) # run the example bot
```

## Basic Setup

To create your own bot server, replace `example` with the `Server` class and call `polling()` to start listening for updates:

```python
import telekit

telekit.Server(BOT_TOKEN).polling() # here
```

That’s it — your bot is connected.

However, the bot doesn’t do anything yet. Let’s fix that by adding our first message handler.

[Next: Create Basic Handler »](2_basic_handler.md)