from telegram import Update

from core.bot import MQBot
from core.utils import send_async
from core.db import Session
from core.decorators import command_handler
from core.enums import AdminType
from core.model import User, Group
from core.texts import *


@command_handler(
    min_permission=AdminType.GROUP,
    allow_private=False,
    allow_group=True
)
def enable_thorns(bot: MQBot, update: Update, _user: User):
    group = Session.query(Group).filter_by(id=update.message.chat.id).first()
    if group:
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
)
def list_aliens(bot: MQBot, update: Update, user: User):
    """ Get some info about the people currently in a given group """
    no_user = []
    no_char = []
    banned = []
    not_in_squad = []

    chat_id = None
    group = None

    for row in update.message.text.splitlines():
        if row.startswith("👽"):
            chat_id = row.replace("👽", "")
            group = Session.query(Group).filter_by(id=chat_id).first()
            continue

        split_row = row.split(";", maxsplit=1)
        user_id = split_row[0]
        username = split_row[1] if len(split_row) > 1 else None

        user_account = Session.query(User).filter(User.id == user_id).first()
        if not user_account:
            no_user.append((user_id, username))
        else:
            if user.is_banned:
                banned.append((user_id, username))
            elif not user.character:
                no_char.append((user_id, username))
            elif group.squad and user.is_squadmember and user.member.squad.chat_id != group.id:
                not_in_squad.append((user_id, username))

    text = "Results:\n"
    for acc in banned:
        text += "⚱️{}\n".format("@{}".format(acc[1]) if acc[1] else acc[0])
    for acc in no_user:
        text += "👤{}\n".format("@{}".format(acc[1]) if acc[1] else acc[0])
    for acc in no_char:
        text += "🏛{}\n".format("@{}".format(acc[1]) if acc[1] else acc[0])
    for acc in not_in_squad:
        text += "️{}\n".format("@{}".format(acc[1]) if acc[1] else acc[0])

    send_async(bot, chat_id=update.message.chat.id, text=text)


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
