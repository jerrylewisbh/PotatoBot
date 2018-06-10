import logging
from datetime import datetime

from core.texts import (MSG_ALREADY_BANNED, MSG_BAN_COMPLETE, MSG_NO_REASON,
                        MSG_REASON_TRAITOR, MSG_USER_BANNED,
                        MSG_USER_BANNED_TRAITOR, MSG_USER_NOT_BANNED,
                        MSG_USER_UNBANNED, MSG_USER_UNKNOWN, MSG_YOU_BANNED,
                        MSG_YOU_UNBANNED)
from core.types import Admin, Ban, Squad, SquadMember, User, Session
from core.decorators import admin_allowed
from core.utils import send_async
from telegram import Bot, TelegramError, Update

Session()

@admin_allowed()
def ban(bot: Bot, update: Update):
    username, reason = update.message.text.split(' ', 2)[1:]
    username = username.replace('@', '')
    user = Session.query(User).filter_by(username=username).first()
    if user:
        banned = Session.query(Ban).filter_by(user_id=user.id).first()
        if banned:
            send_async(bot, chat_id=update.message.chat.id,
                       text=MSG_ALREADY_BANNED.format(banned.to_date, banned.reason))
        else:
            banned = Ban()
            banned.user_id = user.id
            banned.from_date = datetime.now()
            banned.to_date = datetime.max
            banned.reason = reason or MSG_NO_REASON
            member = Session.query(SquadMember).filter_by(user_id=user.id).first()
            if member:
                Session.delete(member)
            admins = Session.query(Admin).filter_by(user_id=user.id).all()
            for admin in admins:
                Session.delete(admin)
            Session.add(banned)
            Session.commit()
            squads = Session.query(Squad).all()
            for squad in squads:
                send_async(bot, chat_id=squad.chat_id, text=MSG_USER_BANNED.format('@' + username))
            send_async(bot, chat_id=user.id, text=MSG_YOU_BANNED.format(banned.reason))
            send_async(bot, chat_id=update.message.chat.id, text=MSG_BAN_COMPLETE)
    else:
        send_async(bot, chat_id=update.message.chat.id, text=MSG_USER_UNKNOWN)


def ban_traitor(bot: Bot, user_id):
    user = Session.query(User).filter_by(id=user_id).first()
    if user:
        logging.warning("Banning %s", user.id)
        banned = Ban()
        banned.user_id = user.id
        banned.from_date = datetime.now()
        banned.to_date = datetime.max
        banned.reason = MSG_REASON_TRAITOR
        member = Session.query(SquadMember).filter_by(user_id=user.id).first()
        if member:
            Session.delete(member)
            try:
                bot.restrictChatMember(member.squad_id, member.user_id)
                bot.kickChatMember(member.squad_id, member.user_id)
            except TelegramError as err:
                bot.logger.error(err.message)
        admins = Session.query(Admin).filter_by(user_id=user.id).all()
        # for admin in admins:
        # Session.delete(admin)
        Session.add(banned)
        Session.commit()
        squads = Session.query(Squad).all()
        #for squad in squads:
        #    send_async(bot, chat_id=squad.chat_id, text=MSG_USER_BANNED_TRAITOR.format('@' + user.username))


@admin_allowed()
def unban(bot: Bot, update: Update):
    username = update.message.text.split(' ', 1)[1]
    username = username.replace('@', '')
    user = Session.query(User).filter_by(username=username).first()
    if user:
        banned = Session.query(Ban).filter_by(user_id=user.id).first()
        if banned:
            Session.delete(banned)
            Session.commit()
            send_async(bot, chat_id=user.id, text=MSG_YOU_UNBANNED)
            send_async(bot, chat_id=update.message.chat.id, text=MSG_USER_UNBANNED.format('@' + user.username))
        else:
            send_async(bot, chat_id=update.message.chat.id, text=MSG_USER_NOT_BANNED)
    else:
        send_async(bot, chat_id=update.message.chat.id, text=MSG_USER_UNKNOWN)
