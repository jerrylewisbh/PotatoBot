from core.functions.triggers import trigger_decorator
from core.types import Session
from core.utils import send_async, update_group
from telegram import Bot, Update

Session()

@trigger_decorator
def boss_leader(bot: Bot, update: Update):
    group = update_group(update.message.chat)
    if len(group.squad) == 1:
        members = []
        for member in group.squad[0].members:
            char = member.user.character
            if 15 <= char.level <= 25:
                members.append('@' + member.user.username)
        msg = ' '.join(members)
        send_async(bot, chat_id=update.message.chat.id, text=msg)


@trigger_decorator
def boss_zhalo(bot: Bot, update: Update):
    group = update_group(update.message.chat)
    if len(group.squad) == 1:
        members = []
        for member in group.squad[0].members:
            char = member.user.character
            if 26 <= char.level <= 35:
                members.append('@' + member.user.username)
        msg = ' '.join(members)
        send_async(bot, chat_id=update.message.chat.id, text=msg)


@trigger_decorator
def boss_monoeye(bot: Bot, update: Update):
    group = update_group(update.message.chat)
    if len(group.squad) == 1:
        members = []
        for member in group.squad[0].members:
            char = member.user.character
            if 36 <= char.level <= 45:
                members.append('@' + member.user.username)
        msg = ' '.join(members)
        send_async(bot, chat_id=update.message.chat.id, text=msg)


@trigger_decorator
def boss_hydra(bot: Bot, update: Update):
    group = update_group(update.message.chat, session)
    if len(group.squad) == 1:
        members = []
        for member in group.squad[0].members:
            char = member.user.character
            if 46 <= char.level:
                members.append('@' + member.user.username)
        msg = ' '.join(members)
        send_async(bot, chat_id=update.message.chat.id, text=msg)
