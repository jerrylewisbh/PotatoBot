import logging
from telegram import constants

from telegram.ext import run_async

from core.bot import MQBot
from core.db import Session
from core.model import Group

Session()

def disable_group(group: Group):
    if group:
        logging.info("Updating group: '%s'", group.id)
        group.bot_in_group = False
        Session.add(group)
        Session.commit()
        return group

    return None

def update_group(grp):
    if grp.type in ['group', 'supergroup', 'channel']:
        group = Session.query(Group).filter_by(id=grp.id).first()
        if not group:
            logging.info("Creating new group: title='%s', id='%s', name='%s'", grp.title, grp.id, grp.username)
            group = Group(id=grp.id, title=grp.title, username=grp.username)
            Session.add(group)
        else:
            updated = False
            if group.username != grp.username:
                group.username = grp.username
                updated = True
            if group.title != grp.title:
                group.title = grp.title
                updated = True
            if not group.bot_in_group:
                group.bot_in_group = True
                updated = True
            if updated:
                logging.info("Updating group: title='%s', id='%s', name='%s'", grp.title, grp.id, grp.username)
                Session.add(group)

        Session.commit()
        return group
    return None

@run_async
def send_async(bot: MQBot, *args, **kwargs):
    return bot.send_message(*args, **kwargs)


def send_long_message(bot, chat_id, text: str, **kwargs):
    if len(text) <= constants.MAX_MESSAGE_LENGTH:
        return bot.send_message(chat_id, text, **kwargs)

    parts = []
    while len(text) > 0:
        if len(text) > constants.MAX_MESSAGE_LENGTH:
            part = text[:constants.MAX_MESSAGE_LENGTH]
            first_lnbr = part.rfind('\n')
            if first_lnbr != -1:
                parts.append(part[:first_lnbr])
                text = text[first_lnbr:]
            else:
                parts.append(part)
                text = text[constants.MAX_MESSAGE_LENGTH:]
        else:
            parts.append(text)
            break

    msg = None
    for part in parts:
        msg = bot.send_message(chat_id, part, **kwargs)
    return msg  # return only the last message
