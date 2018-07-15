from telegram import Update

from core.bot import MQBot
from core.db import Session
from core.decorators import command_handler
from core.enums import AdminType
from core.model import User, Group
from core.texts import *
from core.utils import send_async


@command_handler(
    min_permission=AdminType.GROUP,
    allow_private=False,
    allow_group=True
)
def enable_thorns(bot: MQBot, update: Update, _user: User):
    group = Session.query(Group).filter_by(id=update.message.chat.id).first()
    if group and len(group.squad) == 1:
        group.thorns_enabled = True
        Session.add(group)
        Session.commit()
        send_async(bot, chat_id=update.message.chat.id, text=MSG_GROUP_THORNS_ENABLED)


@command_handler(
    min_permission=AdminType.GROUP,
    allow_private=False,
    allow_group=True
)
def enable_reminders(bot: MQBot, update: Update, user: User):
    group = Session.query(Group).filter_by(id=update.message.chat.id).first()
    if group:
        group.reminders_enabled = True
        Session.add(group)
        Session.commit()
        send_async(bot, chat_id=update.message.chat.id, text=MSG_GROUP_REMINDERS_ENABLED)


@command_handler(
    min_permission=AdminType.GROUP,
    allow_private=False,
    allow_group=True
)
def enable_silence(bot: MQBot, update: Update, user: User):
    group = Session.query(Group).filter_by(id=update.message.chat.id).first()
    if group:
        group.silence_enabled = True
        Session.add(group)
        Session.commit()
        send_async(bot, chat_id=update.message.chat.id, text=MSG_GROUP_SILENCE_ENABLED)


@command_handler(
    min_permission=AdminType.GROUP,
    allow_private=False,
    allow_group=True
)
def disable_thorns(bot: MQBot, update: Update, user: User):
    group = Session.query(Group).filter_by(id=update.message.chat.id).first()
    if group:
        group.thorns_enabled = False
        Session.add(group)
        Session.commit()
        send_async(bot, chat_id=update.message.chat.id, text=MSG_GROUP_THORNS_DISABLED)


@command_handler(
    min_permission=AdminType.GROUP,
    allow_private=False,
    allow_group=True
)
def disable_silence(bot: MQBot, update: Update, user: User):
    group = Session.query(Group).filter_by(id=update.message.chat.id).first()
    if group:
        Session.add(group)
        Session.commit()
        send_async(bot, chat_id=update.message.chat.id, text=MSG_GROUP_SILENCE_DISABLED)


@command_handler(
    min_permission=AdminType.GROUP,
    allow_private=False,
    allow_group=True
)
def disable_reminders(bot: MQBot, update: Update, user: User):
    group = Session.query(Group).filter_by(id=update.message.chat.id).first()
    if group:
        group.reminders_enabled = False
        Session.add(group)
        Session.commit()
        send_async(bot, chat_id=update.message.chat.id, text=MSG_GROUP_REMINDERS_DISABLED)

@command_handler(
    min_permission=AdminType.GROUP,
    allow_private=False,
    allow_group=True
)
def deny_bots(bot: MQBot, update: Update, user: User):
    group = Session.query(Group).filter_by(id=update.message.chat.id).first()
    if group:
        group.allow_bots = False
        Session.add(group)
        Session.commit()
        send_async(bot, chat_id=update.message.chat.id, text=MSG_GROUP_BOTS_DENIED)


@command_handler(
    min_permission=AdminType.GROUP,
    allow_private=False,
    allow_group=True
)
def allow_bots(bot: MQBot, update: Update, user: User):
    group = Session.query(Group).filter_by(id=update.message.chat.id).first()
    if group:
        group.allow_bots = True
        Session.add(group)
        Session.commit()
        send_async(bot, chat_id=update.message.chat.id, text=MSG_GROUP_BOTS_ALLOWED)
