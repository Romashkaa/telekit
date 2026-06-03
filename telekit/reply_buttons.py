from dataclasses import dataclass
from typing import Any

from telebot.types import (
    KeyboardButton,
    WebAppInfo,
    KeyboardButtonRequestUser,
    KeyboardButtonRequestChat,
    KeyboardButtonPollType,
)

__all__ = [
    "ReplyButton",
    "TextButton",
    "ContactButton",
    "LocationButton",
    "PollButton",
    "WebAppReplyButton",
    "RequestUserButton",
    "RequestChatButton",
]


class ReplyButton:
    """Base class for all reply keyboard buttons."""

    def to_button(self, text: str) -> KeyboardButton:
        """
        Convert this button descriptor into a :class:`telebot.types.KeyboardButton`.

        :param text: Label displayed on the button.
        :type text: str
        :raises NotImplementedError: Must be implemented by subclasses.
        :rtype: :class:`telebot.types.KeyboardButton`
        """
        raise NotImplementedError


class TextButton(ReplyButton):
    """
    A plain text button.

    When pressed, sends the button label as a regular message.

    .. note::
        This is a **reply** keyboard button, intended to be used exclusively with :class:`ReplyKeyboard`.
    """

    def to_button(self, text: str) -> KeyboardButton:
        """
        :param text: Label displayed on the button.
        :type text: str
        :rtype: :class:`telebot.types.KeyboardButton`
        """
        return KeyboardButton(text)


class ContactButton(ReplyButton):
    """
    A button that requests the user's phone number.

    Telegram will prompt the user to share their contact.
    Only works in private chats.

    .. note::
        This is a **reply** keyboard button, intended to be used exclusively with :class:`ReplyKeyboard`.
    """

    def to_button(self, text: str) -> KeyboardButton:
        """
        :param text: Label displayed on the button.
        :type text: str
        :rtype: :class:`telebot.types.KeyboardButton`
        """
        return KeyboardButton(text, request_contact=True)


class LocationButton(ReplyButton):
    """
    A button that requests the user's current location.

    Telegram will prompt the user to share their geolocation.
    Only works in private chats.
    
    .. note::
        This is a **reply** keyboard button, intended to be used exclusively with :class:`ReplyKeyboard`.
    """

    def to_button(self, text: str) -> KeyboardButton:
        """
        :param text: Label displayed on the button.
        :type text: str
        :rtype: :class:`telebot.types.KeyboardButton`
        """
        return KeyboardButton(text, request_location=True)

class _FixedKeyboardButtonPollType(KeyboardButtonPollType):
    def to_dict(self):
        # FIX: Bad Request: can't parse keyboard button: Field "type" must be of type String.
        # self.type: str | None
        if self.type is not None:
            return {'type': self.type}
        return {}

@dataclass
class PollButton(ReplyButton):
    """
    A button that prompts the user to create a poll.

    :param poll_type: Type of poll to create.
        Accepted values: ``"quiz"``, ``"regular"``, or ``None`` (any type).
    :type poll_type: str or None
    
    .. note::
        This is a **reply** keyboard button, intended to be used exclusively with :class:`ReplyKeyboard`.
    """

    poll_type: str | None = None

    def to_button(self, text: str) -> KeyboardButton:
        """
        :param text: Label displayed on the button.
        :type text: str
        :rtype: :class:`telebot.types.KeyboardButton`
        """
        print(f"{self.poll_type=}")
        return KeyboardButton(
            text,
            request_poll=_FixedKeyboardButtonPollType(type=self.poll_type),
        )


@dataclass
class WebAppReplyButton(ReplyButton):
    """
    A button that opens a Telegram Mini App (Web App).
    
    .. note::
        This is a **reply** keyboard button, intended to be used exclusively with :class:`ReplyKeyboard`.

    :param url: HTTPS URL of the Web App to open.
    :type url: str
    """

    url: str

    def to_button(self, text: str) -> KeyboardButton:
        """
        :param text: Label displayed on the button.
        :type text: str
        :rtype: :class:`telebot.types.KeyboardButton`
        """
        return KeyboardButton(text, web_app=WebAppInfo(url=self.url))


@dataclass
class RequestUserButton(ReplyButton):
    """
    A button that prompts the user to select another Telegram user.
    
    .. note::
        This is a **reply** keyboard button, intended to be used exclusively with :class:`ReplyKeyboard`.

    :param request_id: Signed 32-bit identifier of the request.
        Must be unique within the message.
    :type request_id: int
    :param user_is_bot: If ``True``, only bots are shown.
        If ``False``, only regular users are shown.
        If ``None``, no filter is applied.
    :type user_is_bot: bool or None
    :param user_is_premium: If ``True``, only Premium users are shown.
        If ``False``, only non-Premium users are shown.
        If ``None``, no filter is applied.
    :type user_is_premium: bool or None
    """

    request_id: int
    user_is_bot: bool | None = None
    user_is_premium: bool | None = None

    def to_button(self, text: str) -> KeyboardButton:
        """
        :param text: Label displayed on the button.
        :type text: str
        :rtype: :class:`telebot.types.KeyboardButton`
        """
        return KeyboardButton(
            text,
            request_user=KeyboardButtonRequestUser(
                request_id=self.request_id,
                user_is_bot=self.user_is_bot,
                user_is_premium=self.user_is_premium,
            ),
        )


@dataclass
class RequestChatButton(ReplyButton):
    """
    A button that prompts the user to select a chat. The identifier of the selected chat will be shared with the bot when the corresponding button is pressed.
    
    .. note::
        This is a **reply** keyboard button, intended to be used exclusively with :class:`ReplyKeyboard`.

    :param request_id: Signed 32-bit identifier of the request.
        Must be unique within the message.
    :type request_id: int
    :param chat_is_channel: If ``True``, only channels are shown.
        If ``False``, only groups and supergroups are shown.
    :type chat_is_channel: bool
    :param chat_is_forum: If ``True``, only forum supergroups are shown.
    :type chat_is_forum: bool or None
    :param chat_has_username: If ``True``, only public chats are shown.
    :type chat_has_username: bool or None
    :param chat_is_created: If ``True``, only chats created by the user are shown.
    :type chat_is_created: bool or None
    :param user_administrator_rights: Required administrator rights of the user
        in the selected chat.
    :type user_administrator_rights: :class:`telebot.types.ChatAdministratorRights` or None
    :param bot_administrator_rights: Required administrator rights of the bot
        in the selected chat.
    :type bot_administrator_rights: :class:`telebot.types.ChatAdministratorRights` or None
    :param bot_is_member: If ``True``, the bot must already be a member of the selected chat.
    :type bot_is_member: bool or None
    """

    request_id: int
    chat_is_channel: bool = False
    chat_is_forum: bool | None = None
    chat_has_username: bool | None = None
    chat_is_created: bool | None = None
    user_administrator_rights: Any | None = None
    bot_administrator_rights: Any | None = None
    bot_is_member: bool | None = None

    def to_button(self, text: str) -> KeyboardButton:
        """
        :param text: Label displayed on the button.
        :type text: str
        :rtype: :class:`telebot.types.KeyboardButton`
        """
        return KeyboardButton(
            text,
            request_chat=KeyboardButtonRequestChat(
                request_id=self.request_id,
                chat_is_channel=self.chat_is_channel,
                chat_is_forum=self.chat_is_forum,
                chat_has_username=self.chat_has_username,
                chat_is_created=self.chat_is_created,
                user_administrator_rights=self.user_administrator_rights,
                bot_administrator_rights=self.bot_administrator_rights,
                bot_is_member=self.bot_is_member,
            ),
        )