from telegram.ext import run_async

from core.bot import MQBot
from core.db import Session
from core.model import Group

Session()

def update_group(grp, in_group=True):
    if grp.type in ['group', 'supergroup', 'channel']:
        group = Session.query(Group).filter_by(id=grp.id).first()
        if group is None:
            group = Group(id=grp.id, title=grp.title,
                          username=grp.username)
            Session.add(group)

        else:
            updated = False
            if group.username != grp.username:
                group.username = grp.username
                updated = True
            if group.title != grp.title:
                group.title = grp.title
                updated = True
            if group.bot_in_group != in_group:
                group.bot_in_group = in_group
                updated = True
            if updated:
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
