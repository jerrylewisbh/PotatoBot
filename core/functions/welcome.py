import logging
from config import ACADEM_CHAT_ID, CASTLE, CASTLE_CHAT_ID
from time import time

from core.functions.newbies import newbie
from core.template import fill_template
from core.texts import *
from core.types import (Admin, AdminType, WelcomeMsg, Wellcomed, Session)
from core.decorators import admin_allowed, user_allowed
from core.utils import add_user, send_async, update_group
from telegram import Bot, Update

last_welcome = 0

Session()

@user_allowed(False)
def welcome(bot: Bot, update: Update):
    #newbie(bot, update)
    global last_welcome
    logging.debug("Welcome")
    if update.message.chat.type in ['group', 'supergroup']:
        group = update_group(update.message.chat)
        for new_chat_member in update.message.new_chat_members:
            user = add_user(new_chat_member)
            logging.debug("Welcome: user=%s", user)
            administrator = Session.query(Admin).filter_by(user_id=user.id).all()
            allow_anywhere = False
            for adm in administrator:
                if adm.admin_type == AdminType.FULL.value:
                    allow_anywhere = True
                    break
            logging.debug("Welcome: chat_id=%s", update.message.chat.id)
            logging.debug(
                "Welcome: castle_chat_id==update.message.chat.id = %s",
                CASTLE_CHAT_ID == update.message.chat.id)
            if str(update.message.chat.id) == CASTLE_CHAT_ID or str(update.message.chat.id) == ACADEM_CHAT_ID:
                logging.debug("Welcome: equal")
                if group.welcome_enabled:
                    logging.debug("Welcome: enable")
                    welcome_msg = Session.query(WelcomeMsg).filter_by(chat_id=group.id).first()
                    send_async(bot, chat_id=update.message.chat.id, text=fill_template(welcome_msg.message, user))

            elif (user is None or user.character is None or user.character.castle != CASTLE or user.member is None and not allow_anywhere and user.id != bot.id):
                send_async(bot, chat_id=update.message.chat.id, vtext=MSG_THORNS.format("SPY"))
                bot.restrictChatMember(update.message.chat.id, new_chat_member.id)
                bot.kickChatMember(update.message.chat.id, new_chat_member.id)
            elif len(group.squad) == 1 and group.squad[0].thorns_enabled and user.id != bot.id and \
                    (user.member and user.member not in group.squad[0].members) and not allow_anywhere:
                send_async(bot, chat_id=update.message.chat.id,
                           text=MSG_THORNS.format(str(user)))
                bot.restrictChatMember(update.message.chat.id, new_chat_member.id)
                bot.kickChatMember(update.message.chat.id, new_chat_member.id)
            else:
                if group.welcome_enabled:
                    welcome_msg = Session.query(WelcomeMsg).filter_by(chat_id=group.id).first()
                    if welcome_msg is None:
                        welcome_msg = WelcomeMsg(chat_id=group.id, message=MSG_WELCOME_DEFAULT)
                        Session.add(welcome_msg)

                    welcomed = Session.query(Wellcomed).filter_by(user_id=new_chat_member.id,
                                                                  chat_id=update.message.chat.id).first()
                    if welcomed is None:
                        if time() - last_welcome > 30:
                            send_async(bot, chat_id=update.message.chat.id,
                                       text=fill_template(welcome_msg.message, user))
                            last_welcome = time()
                        welcomed = Wellcomed(user_id=new_chat_member.id, chat_id=update.message.chat.id)
                        Session.add(welcomed)
                    Session.commit()


@admin_allowed(adm_type=AdminType.GROUP)
def set_welcome(bot: Bot, update: Update):
    if update.message.chat.type in ['group', 'supergroup']:
        group = update_group(update.message.chat)
        welcome_msg = Session.query(WelcomeMsg).filter_by(chat_id=group.id).first()
        if welcome_msg is None:
            welcome_msg = WelcomeMsg(chat_id=group.id, message=update.message.text.split(' ', 1)[1])
        else:
            welcome_msg.message = update.message.text.split(' ', 1)[1]
        Session.add(welcome_msg)
        Session.commit()
        send_async(bot, chat_id=update.message.chat.id, text=MSG_WELCOME_SET)


@admin_allowed(adm_type=AdminType.GROUP)
def enable_welcome(bot: Bot, update: Update):
    if update.message.chat.type in ['group', 'supergroup']:
        group = update_group(update.message.chat)
        group.welcome_enabled = True
        Session.add(group)
        Session.commit()
        send_async(bot, chat_id=update.message.chat.id, text=MSG_WELCOME_ENABLED)


@admin_allowed(adm_type=AdminType.GROUP)
def disable_welcome(bot: Bot, update: Update):
    if update.message.chat.type in ['group', 'supergroup']:
        group = update_group(update.message.chat)
        group.welcome_enabled = False
        Session.add(group)
        Session.commit()
        send_async(bot, chat_id=update.message.chat.id, text=MSG_WELCOME_DISABLED)


@admin_allowed(adm_type=AdminType.GROUP)
def show_welcome(bot: Bot, update):
    if update.message.chat.type in ['group', 'supergroup']:
        group = update_group(update.message.chat)
        welcome_msg = Session.query(WelcomeMsg).filter_by(chat_id=group.id).first()
        if welcome_msg is None:
            welcome_msg = WelcomeMsg(chat_id=group.id, message=MSG_WELCOME_DEFAULT)
            Session.add(welcome_msg)
            Session.commit()
        send_async(bot, chat_id=group.id, text=welcome_msg.message)
