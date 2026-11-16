# Tutorial v2

## Introduction

What if developing a complex conversational Telegram bot didn't require bulky finite state machines (FSM), tangled state containers, or hundreds of lines of duplicated code?

Welcome to the world of Telekit, a modern, declarative Python framework that makes bot development clear, elegant, and logical. This is the official guide from the developer, and it's suitable even if you've never worked with Telegram bots before.

By the end of this tutorial, you will be able to:

- Master the core architecture of Telekit: the server, Handlers, the Sender system, and Chain management.
- Configure precise message triggers and typed command parameters for Deep Linking.
- Design multi-step dialogs without FSM using the Entries mechanism.
- Build flexible Inline and Reply keyboards, implement seamless control transfer between handlers (Handoff), and apply modular Traits.

> I recommend reading the full material to avoid missing any important details.
> If you have questions or run into difficulties while learning, reach out to the [Telekit community](https://t.me/+wu-dFrOBFIwyNzc0), where community members are always ready to help.

## Contents

- Getting started:
    - [Getting started](1_getting_started.md)
    - [Basic handler](2_basic_handler.md)
- [Triggers](3_triggers.md)
    - [Command Parameters & Deep Linking](./command_trigger_parameters.md)
    - [Text Templates](./text_trigger_parameters.md)
    - [Func Parameters](./func_trigger_parameters.md)
- [Sender](5_senders.md)
    - [Styles](6_styles.md)
    - TextBuilder
- Chain
    - [Inline Keyboard](7_inline_keyboards.md)
        - [Inline Button Types](./7_2_inline_buttons.md)
    - [Reply Keyboard](./7_3_reply_keyboard.md)
        - [Reply Button Types](./7_4_reply_buttons.md)
    - [Entries](8_entries.md)
    - [Timeouts](./9_timeouts.md)
    - Chain Summary
- Handler
    - [Handoff](./11_handoff.md)
    - [Traits](./10_traits.md)
        - [Creating Traits](./10_2_creating_traits.md)
    - User
    - Chat
    - Handler Summary
- Scheduler
- Utils
    - Environment Utils
    - Inline Keyboard Utils
- Debugging
- Telekit DSL:
    - [Introduction](../tutorial/11_telekit_dsl.md)
    - [Learn Syntax](../tutorial/13_telekit_dsl_syntax.md)

[Examples](../examples/examples.md) [Changelog](../../CHANGELOG.md)