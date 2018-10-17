from time import time

import logging

import telegram
from datetime import datetime, timedelta
from telegram import Update, ParseMode

from config import CASTLE_CHAT_ID
from core.bot import MQBot
from core.decorators import command_handler, create_or_update_user
from core.template import fill_template
from core.texts import *
from core.db import Session, check_permission
from core.enums import AdminType
from core.model import User, WelcomeMsg, Wellcomed, Admin, Group, Ban
from core.utils import update_group, send_async
from functions.admin import __kickban_from_chat

Session()

@command_handler(
    allow_group=True,
    allow_banned=True, # Allowed because we handle this directly in code..
)
def welcome(bot: MQBot, update: Update, user: User):
    if update.message.chat.type not in ['group', 'supergroup']:
        return

    group = update_group(update.message.chat)
    for new_chat_member in update.message.new_chat_members:
        user_allowed, joined_user = __is_allowed_to_join(bot, update, new_chat_member, group)
        if not user_allowed:
            __kickban_from_chat(bot, joined_user, group)
        elif joined_user.id == bot.id:
            # Bot may only be added by admins of that channel or global admins...
            logging.info("Bot was added to new channel")

            bot_added_by_user = create_or_update_user(update.effective_user)
            if not check_permission(bot_added_by_user, update, min_permission=AdminType.GROUP):
                msg_send = bot.send_message(
                    chat_id=update.message.chat.id,
                    text=MSG_NO_PERMISSION_TO_ADD_BOT,
                    parse_mode=ParseMode.MARKDOWN
                )
                msg_result = msg_send.result()
                if msg_result:
                    bot.leave_chat(chat_id=update.message.chat.id)
        elif group.welcome_enabled:
            welcome_msg = Session.query(WelcomeMsg).filter_by(chat_id=group.id).first()
            if not welcome_msg:
                welcome_msg = WelcomeMsg(chat_id=group.id, message=MSG_WELCOME_DEFAULT)
                Session.add(welcome_msg)

            logging.info("[Welcome] message='%s', chat_id='%s'", welcome_msg.message, welcome_msg.chat_id)
            send_async(
                bot, chat_id=update.message.chat.id,
                text=fill_template(welcome_msg.message, joined_user)
            )

def __is_allowed_to_join(bot: MQBot, update: Update, new_chat_member: telegram.User, group: Group):
    """ Check if a user is allowed to join a group/supergroup and return that state and the effective user joined...

    :returns tuple(allowed_to_join: bool, effective_user_id: int)
    """

    """
    Notes:
    - update.effective_user contains the user who added a new user if he is invited by someone!
    - I try to list every condition here to get debug logging in place
     
    """
    joined_user = create_or_update_user(new_chat_member)

    # Full-Admins are allowed anywhere except when they are banned
    allow_anywhere = check_permission(joined_user, update, AdminType.FULL)
    if allow_anywhere and joined_user.is_banned:
        allow_anywhere = False

    logging.info(
        "[Welcome] user_id='%s', chat_id='%s', allow_anywhere='%s', is_castle_chat='%s'",
        joined_user,
        update.effective_chat.id,
        allow_anywhere,
        CASTLE_CHAT_ID == update.message.chat.id
    )

    if group.id == CASTLE_CHAT_ID:
        # Castle and Academy are excempted from thorns, etc.
        logging.info("[Welcome] user_id='%s' joined Castle/Academy", joined_user.id)
        return (True, joined_user)
    elif joined_user.id == bot.id:
        logging.info("[Welcome] user_id matches bot_id -> Bot joined this channel")
        return (True, joined_user)
    elif new_chat_member.is_bot:
        if group.allow_bots:
            logging.info("[Welcome] user_id='%s' is a bot, they are allowed in this chat.", joined_user.id)
            return (True, joined_user)
        else:
            logging.info("[Welcome] user_id='%s' is a bot, bot not allwed here!", joined_user.id)
            return (False, joined_user)
    elif allow_anywhere:
        # Allow these users acces...
        logging.info("[Welcome] user_id='%s' has allow_anywhere='%s'", joined_user.id, allow_anywhere)
        return (True, joined_user)
    elif joined_user.is_banned:
        logging.info("[Welcome] user_id='%s' is banned!", joined_user.id)
        return (False, joined_user)
    elif group.thorns_enabled:
        if not joined_user.character:
            # Users without character in Botato will get kicked...
            logging.info(
                "[Welcome] user_id='%s' has not send in character, kicking from '%s'",
                joined_user.id, update.effective_chat.id
            )
            return (False, joined_user)
        elif group.squad and joined_user.is_squadmember and joined_user.member.squad.chat_id == group.id:
            # If a user joins a squad, allow him in if it is his own...
            logging.info(
                "[Welcome] user_id='%s' is a member of squad '%s'", joined_user.id, joined_user.member.squad.chat_id
            )
            return (True, joined_user)
        elif group.squad and joined_user.is_squadmember and joined_user.member.squad.chat_id != group.id:
            # If a user joins a squad, allow him in if it is his own...
            logging.info(
                "[Welcome] user_id='%s' is not a member of THIS squad", joined_user.id
            )
            return (False, joined_user)
        elif group.squad and not joined_user.is_squadmember:
            # If a user joins a squad, allow him in if it is his own...
            logging.info(
                "[Welcome] user_id='%s' is not a member of any squad", joined_user.id
            )
            return (False, joined_user)
        elif not group.squad:
            # Juser joined a group (NOT squad) 
            logging.info(
                "[Welcome] user_id='%s' is a Potato joining a group. Letting him in", joined_user.id
            )
            return (True, joined_user)
        else:
            logging.warning(
                "[Welcome] Thorns enabled and user_id='%s' does not match given criteria",
                joined_user.id
            )
            return (False, joined_user)
    elif not group.thorns_enabled:
        if not joined_user.character:
            logging.info(
                "[Welcome] user_id='%s' has not send in character, but thorns are not enabled. Allowing him in!'%s'",
                joined_user.id, update.effective_chat.id
            )
            return (True, joined_user)
        else:
            logging.info(
                "[Welcome] user_id='%s' has joined. Allowed because no thorns enabled!'",
                joined_user.id
            )
            return (True, joined_user)

    logging.warning("user_id='%s' does not meet any specific criteria for joining. Access denied!", joined_user.id)
    # In any other case, deny access!
    return (False, joined_user)

@command_handler(
    allow_group=True,
    min_permission=AdminType.GROUP,
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
