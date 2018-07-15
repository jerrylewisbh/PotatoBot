from telegram import Update

from core.bot import MQBot
from core.decorators import command_handler
from core.texts import *
from core.db import Session
from core.enums import AdminType
from core.model import User
from core.utils import send_async, update_group

Session()

@command_handler(
    min_permission=AdminType.GROUP,
    allow_group=True,
    allow_private=False,
)
def pin(bot: MQBot, update: Update, user: User):
    bot.pin_chat_message(
        chat_id=update.message.reply_to_message.chat.id,
        message_id=update.message.reply_to_message.message_id,
        disable_notification=False
    )


@command_handler(
    min_permission=AdminType.GROUP,
    allow_group=True,
    allow_private=False,
)
def silent_pin(bot: MQBot, update: Update, user: User):
    bot.pin_chat_message(
        chat_id=update.message.reply_to_message.chat.id,
        message_id=update.message.reply_to_message.message_id,
        disable_notification=True
    )


@command_handler(
    min_permission=AdminType.GROUP,
    allow_group=True,
    allow_private=False
)
def pin_all(bot: MQBot, update: Update, user: User):
    group = update_group(update.message.chat)
    if not group.allow_pin_all:
        group.allow_pin_all = True
        Session.add(group)
        Session.commit()
    send_async(bot, chat_id=update.message.chat.id, text=MSG_PIN_ALL_ENABLED)


@command_handler(
    min_permission=AdminType.GROUP,
    allow_group=True,
    allow_private=False,
)
def not_pin_all(bot: MQBot, update: Update, user: User):
    group = update_group(update.message.chat)
    if group.allow_pin_all:
        group.allow_pin_all = False
        Session.add(group)
        Session.commit()
    send_async(bot, chat_id=update.message.chat.id, text=MSG_PIN_ALL_DISABLED)
