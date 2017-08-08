from telegram import Update, Bot
from core.functions.triggers import trigger_decorator
from core.types import User, AdminType, Admin, admin, session, OrderGroup, Group, Squad
from core.utils import send_async, update_group
from core.functions.inline_keyboard_handling import generate_groups_manage, generate_group_manage
from core.texts import *


@trigger_decorator
def boss_leader(bot: Bot, update: Update):
    group = update_group(update.message.chat)
    if len(group.squad) == 1:
        members = []
        for member in group.squad[0].members:
            char = sorted(member.user.character, key=lambda x: x.date, reverse=True)[0]
            if 15 <= char.level <= 25:
                members.append(repr(member.user))
        msg = '\n'.join(members)
        send_async(bot, chat_id=update.message.chat.id, text=msg)


@trigger_decorator
def boss_zhalo(bot: Bot, update: Update):
    group = update_group(update.message.chat)
    if len(group.squad) == 1:
        members = []
        for member in group.squad[0].members:
            char = sorted(member.user.character, key=lambda x: x.date, reverse=True)[0]
            if 26 <= char.level <= 35:
                members.append(repr(member.user))
        msg = '\n'.join(members)
        send_async(bot, chat_id=update.message.chat.id, text=msg)


@trigger_decorator
def boss_monoeye(bot: Bot, update: Update):
    group = update_group(update.message.chat)
    if len(group.squad) == 1:
        members = []
        for member in group.squad[0].members:
            char = sorted(member.user.character, key=lambda x: x.date, reverse=True)[0]
            if 36 <= char.level <= 45:
                members.append(repr(member.user))
        msg = '\n'.join(members)
        send_async(bot, chat_id=update.message.chat.id, text=msg)


@trigger_decorator
def boss_hydra(bot: Bot, update: Update):
    group = update_group(update.message.chat)
    if len(group.squad) == 1:
        members = []
        for member in group.squad[0].members:
            char = sorted(member.user.character, key=lambda x: x.date, reverse=True)[0]
            if 46 <= char.level:
                members.append(repr(member.user))
        msg = '\n'.join(members)
        send_async(bot, chat_id=update.message.chat.id, text=msg)
