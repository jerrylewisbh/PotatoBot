import logging

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


def pad_string(text, padding):
    """ Add whitespaces to a string to make different texts the same length for pre-formatted texts """
    if not text:
        text = '\u00A0' * padding  # Format with hard spaces...

    while len(text) <= padding:
        text += " "

    return text


@run_async
def send_async(bot: MQBot, *args, **kwargs):
    return bot.send_message(*args, **kwargs)
