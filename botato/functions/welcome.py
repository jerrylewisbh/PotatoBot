from time import time

import logging
from telegram import Update

from config import ACADEM_CHAT_ID, CASTLE, CASTLE_CHAT_ID
from core.bot import MQBot
from core.decorators import command_handler, create_or_update_user
from core.template import fill_template
from core.texts import *
from core.db import Session, check_permission
from core.enums import AdminType
from core.model import User, WelcomeMsg, Wellcomed, Admin
from core.utils import send_async, update_group

last_welcome = 0

Session()


def welcome(bot: MQBot, update: Update):
    # newbie(bot, update)
    global last_welcome
    logging.debug("Welcome")

    if update.message.chat.type in ['group', 'supergroup']:
        group = update_group(update.message.chat)

        for new_chat_member in update.message.new_chat_members:
            user = create_or_update_user(new_chat_member)

            if not __is_allowed_to_join(bot, group, new_chat_member, update, user):
                __kick_and_restrict(bot, new_chat_member, update)
            elif group.welcome_enabled:
                welcome_msg = Session.query(WelcomeMsg).filter_by(chat_id=group.id).first()

                if not welcome_msg:
                    welcome_msg = WelcomeMsg(chat_id=group.id, message=MSG_WELCOME_DEFAULT)
                    Session.add(welcome_msg)

                welcomed = Session.query(Wellcomed).filter(
                    User.id == user.id,
                    chat_id=update.message.chat.id
                ).first()

                if not welcomed:
                    if time() - last_welcome > 30:
                        send_async(
                            bot, chat_id=update.message.chat.id,
                            text=fill_template(welcome_msg.message, user)
                        )
                        last_welcome = time()

                    welcomed = Wellcomed(user_id=new_chat_member.id, chat_id=update.message.chat.id)
                    Session.add(welcomed)
                    
                Session.commit()


def __is_allowed_to_join(bot, group, new_chat_member, update, user):
    """ Check if a user is allowed to join a group/supergroup. """

    # Full-Admins are allowed anywhere except when they are banned
    allow_anywhere = check_permission(user, update, AdminType.FULL)
    if allow_anywhere and user.is_banned:
        allow_anywhere = False

    logging.debug(
        "[Welcome] user_id='%s', chat_id='%s', allow_anywhere='%s', is_castle_chat='%s'",
        user.id,
        update.effective_chat.id,
        allow_anywhere,
        CASTLE_CHAT_ID == update.message.chat.id
    )

    if update.effective_chat.id in [CASTLE_CHAT_ID, ACADEM_CHAT_ID]:
        # Castle and Academy are excempted from thorns, etc.
        logging.debug("[Welcome] user_id='%s' joined Castle/Academy", user.id)
        return True
    elif user.id != bot.id:
        return True
    elif allow_anywhere:
        # Allow these users acces...
        logging.debug("[Welcome] user_id='%s' has allow_anywhere='%s'", user.id, allow_anywhere)
        return True
    elif group.thorns_enabled:
        # If a user joins a squad remove him if it is not his squad...
        if group.squad and group.id == update.effective_chat.id and \
            user.is_squadmember and user.member.squad.chat_id != update.effective_chat.id:
            logging.info(
                "[Welcome] user_id='%s' is not a member of squad '%s'", user.id, user.member.squad.chat_id
            )
            return False
        # Remove banned users and the ones without a character from normal groups...
        elif user.is_banned:
            logging.info(
                "[Welcome] user_id='%s' is banned!",
                user.id,
            )
            return False
        elif not user.character:
            # Kick banned users and the ones without a character in Botato...
            logging.info(
                "[Welcome] user_id='%s' has not send in character, kicking from '%s'",
                user.id, update.effective_chat.id
            )
            return False

    # In any other case, deny access!
    return False


@command_handler(
    allow_group=True,
    min_permission=AdminType.GROUP
)


def __kick_and_restrict(bot, new_chat_member, update):
    text = MSG_THORNS if not update.effective_user.username else MSG_THORNS_NAME.format(update.effective_user.username)
    send_async(
        bot,
        chat_id=update.message.chat.id,
        text=text
    )
    bot.restrict_chat_member(
        update.message.chat.id,
        new_chat_member.id
    )
    bot.kick_chat_member(
        update.message.chat.id,
        new_chat_member.id
    )


def set_welcome(bot: MQBot, update: Update, user: User):
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


@command_handler(
    allow_group=True,
    min_permission=AdminType.GROUP
)
def enable_welcome(bot: MQBot, update: Update, user: User):
    if update.message.chat.type in ['group', 'supergroup']:
        group = update_group(update.message.chat)
        group.welcome_enabled = True
        Session.add(group)
        Session.commit()
        send_async(bot, chat_id=update.message.chat.id, text=MSG_WELCOME_ENABLED)


@command_handler(
    allow_group=True,
    min_permission=AdminType.GROUP
)
def disable_welcome(bot: MQBot, update: Update, user: User):
    if update.message.chat.type in ['group', 'supergroup']:
        group = update_group(update.message.chat)
        group.welcome_enabled = False
        Session.add(group)
        Session.commit()
        send_async(bot, chat_id=update.message.chat.id, text=MSG_WELCOME_DISABLED)


@command_handler(
    allow_group=True,
    min_permission=AdminType.GROUP
)
def show_welcome(bot: MQBot, update: Update, user: User):
    if update.message.chat.type in ['group', 'supergroup']:
        group = update_group(update.message.chat)
        welcome_msg = Session.query(WelcomeMsg).filter_by(chat_id=group.id).first()
        if welcome_msg is None:
            welcome_msg = WelcomeMsg(chat_id=group.id, message=MSG_WELCOME_DEFAULT)
            Session.add(welcome_msg)
            Session.commit()
        send_async(bot, chat_id=group.id, text=welcome_msg.message)
