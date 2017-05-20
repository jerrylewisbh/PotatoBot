from telegram import Bot, Chat
from telegram.ext.dispatcher import run_async
from core.types import session, User, Group
from telegram.error import ChatMigrated
import json


@run_async
def send_async(bot: Bot, *args, **kwargs):
    try:
        bot.sendMessage(*args, **kwargs)
    except ChatMigrated as e:
        group = session.query(Group).filter_by(id=kwargs['chat_id']).first()
        if group is not None:
            group.bot_in_group = False
            session.add(group)
            session.commit()
        kwargs['chat_id'] = e.new_chat_id
        bot.sendMessage(*args, **kwargs)


def send_pin_async(bot: Bot, *args, **kwargs):
    try:
        msg = bot.sendMessage(*args, **kwargs)
    except ChatMigrated as e:
        kwargs['chat_id'] = e.new_chat_id
        msg = bot.sendMessage(*args, **kwargs)
    import http.client
    conn = http.client.HTTPConnection("127.0.0.1")
    conn.request("GET", "/{}/{}/".format(msg.message_id, msg.chat.id))


def add_user(tg_user):
    user = session.query(User).filter_by(id=tg_user.id).first()
    if user is None:
        user = User(id=tg_user.id, username=tg_user.username or '',
                    first_name=tg_user.first_name or '',
                    last_name=tg_user.last_name or '')
        session.add(user)
    else:
        updated = False
        if user.username != tg_user.username:
            user.username = tg_user.username
            updated = True
        if user.first_name != tg_user.first_name:
            user.first_name = tg_user.first_name
            updated = True
        if user.last_name != tg_user.last_name:
            user.last_name = tg_user.last_name
            updated = True
        if updated:
            session.add(user)
    session.commit()
    return user


def update_group(grp):
    if grp.type in ['group', 'supergroup', 'channel']:
        group = session.query(Group).filter_by(id=grp.id).first()
        if group is None:
            group = Group(id=grp.id, title=grp.title,
                          username=grp.username)
            session.add(group)
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
                session.add(group)
        session.commit()
        return group
    return None
