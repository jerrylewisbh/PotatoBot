import logging
from datetime import datetime

from telegram import Bot, ParseMode, Update, InlineKeyboardButton, InlineKeyboardMarkup

from config import WAITING_ROOM_LINK, MINIMUM_SQUAD_MEMBER_LEVEL
from core.bot import MQBot
from core.decorators import command_handler
from core.handler.callback import CallbackAction
from core.handler.callback.util import create_callback, get_callback_action
from core.texts import *
from core.texts import MSG_SQUAD_LEAVE_DECLINE, BTN_YES, BTN_NO, MSG_SQUAD_REQUESTED, MSG_SQUAD_REQUEST_NEW, \
    MSG_SQUAD_REQUEST_EXISTS, MSG_GO_AWAY, MSG_SQUAD_REQUEST_DECLINED, MSG_SQUAD_ADD_ACCEPTED
from core.types import (Admin, Session,
                        SquadMember, User, Squad)
from core.utils import send_async

from functions.squad.util import __remove
from functions.reply_markup import generate_squad_markup

Session()


@command_handler()
def squad_about(bot: Bot, update: Update, user: User):
    admin = Session.query(Admin).filter(
        Admin.user_id == update.effective_user.id,
        Admin.group_id.isnot(None)
    ).first()

    markup = generate_squad_markup(is_group_admin=admin is not None, in_squad=True if user.is_squadmember else False)
    if user.is_squadmember:
        squad_text = MSG_SQUAD_ABOUT.format(user.member.squad.squad_name)
    elif user.member and not user.member.approved:
        squad_text = MSG_SQUAD_REQUESTED.format(user.member.squad.squad_name, WAITING_ROOM_LINK)
    else:
        squad_text = MSG_SQUAD_NONE

    send_async(
        bot,
        chat_id=user.id,
        text=squad_text,
        reply_markup=markup
    )


@command_handler()
def leave_squad_request(bot: Bot, update: Update, user: User):
    if update.callback_query:
        action = get_callback_action(update.callback_query.data, update.effective_user.id)
        if 'leave' in action.data and action.data['leave']:
            remove_user = Session.query(User).filter(User.id == action.data['leave_user_id']).first()
            old_squad_name = __remove(bot, user, remove_user)
            bot.edit_message_text(
                MSG_SQUAD_LEFT.format(remove_user.character.name, old_squad_name),
                update.callback_query.message.chat.id,
                update.callback_query.message.message_id,
            )
            squad_about(bot, update, user)
        elif 'leave' in action.data:
            bot.edit_message_text(
                MSG_SQUAD_LEAVE_DECLINE,
                update.callback_query.message.chat.id,
                update.callback_query.message.message_id
            )
    else:
        member = user.member
        if member:
            squad = member.squad
            markup = __get_keyboard_leave(user, user.id)
            send_async(
                bot,
                chat_id=member.user_id,
                text=MSG_SQUAD_LEAVE_ASK.format(user.character.name, squad.squad_name),
                parse_mode=ParseMode.HTML,
                reply_markup=markup,
            )
        else:
            send_async(
                bot,
                chat_id=user.id,
                text=MSG_SQUAD_NONE,
                parse_mode=ParseMode.HTML
            )


def __get_keyboard_leave(user, leave_user_id):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                BTN_YES,
                callback_data=create_callback(
                    CallbackAction.SQUAD_LEAVE,
                    user.id,
                    leave=True,
                    leave_user_id=leave_user_id
                )
            ),
            InlineKeyboardButton(
                BTN_NO,
                callback_data=create_callback(
                    CallbackAction.SQUAD_LEAVE,
                    user.id,
                    leave=False,
                    leave_user_id=leave_user_id
                )
            )
        ]
    ])


@command_handler()
def join_squad_request(bot: Bot, update: Update, user: User):
    # Already a join in progress...
    if update.callback_query:
        action = get_callback_action(update.callback_query.data, update.effective_user.id)

        if user.is_squadmember or (user.member and not user.member.approved):
            bot.edit_message_text(
                MSG_SQUAD_REQUEST_EXISTS,
                update.callback_query.message.chat.id,
                update.callback_query.message.message_id,
                reply_markup=__get_keyboard_leave(user)
            )
            return

        # Join him...
        member = SquadMember()
        member.user_id = update.callback_query.from_user.id
        member.squad_id = action.data['squad_id']
        Session.add(member)
        Session.commit()

        bot.edit_message_text(
            MSG_SQUAD_REQUESTED.format(
                member.squad.squad_name,
                WAITING_ROOM_LINK
            ),
            update.callback_query.message.chat.id,
            update.callback_query.message.message_id,
            parse_mode=ParseMode.HTML
        )

        # Notify Admins
        admins = Session.query(Admin).filter_by(group_id=member.squad.chat_id).all()
        for adm in admins:
            send_async(bot, chat_id=adm.user_id, text=MSG_SQUAD_REQUEST_NEW)
    else:
        # Do some checks, abort if user does not meet requirements!
        if not user.username:
            send_async(bot, chat_id=update.message.chat.id, text=MSG_NO_USERNAME)
            return
        if not user.character:
            send_async(bot, chat_id=update.message.chat.id, text=MSG_NO_PROFILE_IN_BOT)
            return
        if user.is_squadmember or (user.member and not user.member.approved):
            send_async(bot, chat_id=update.message.chat.id, text=MSG_SQUAD_REQUEST_EXISTS,
                       reply_markup=__get_keyboard_leave(user))
            return
        if user.character.level < MINIMUM_SQUAD_MEMBER_LEVEL:
            send_async(
                bot, chat_id=update.message.chat.id,
                text=MSG_SQUAD_LEVEL_TOO_LOW.format(MINIMUM_SQUAD_MEMBER_LEVEL)
            )
            return

        # OK, lets do this....
        inline_keys = []
        for squad in Session.query(Squad).filter(Squad.hiring.is_(True)).all():
            inline_keys.append([InlineKeyboardButton(
                squad.squad_name,
                callback_data=create_callback(
                    CallbackAction.SQUAD_JOIN,
                    user.id,
                    squad_id=squad.chat_id
                )
            )])
        send_async(
            bot,
            chat_id=update.message.chat.id,
            text=MSG_SQUAD_REQUEST,
            reply_markup=InlineKeyboardMarkup(inline_keys)
        )


@command_handler(
    allow_private=False,
    allow_group=True
)
def squad_invite(bot: MQBot, update: Update, user: User):
    if not update.callback_query:
        logging.warning("squad_invite_answer without callback_query called")
        return

    action = get_callback_action(update.callback_query.data, update.effective_user.id)
    if action.data['invited_user_id'] != update.callback_query.from_user.id:
        update.callback_query.answer(text=MSG_GO_AWAY)
        return

    invited_user = Session.query(User).filter(User.id == action.data['invited_user_id']).first()
    if action.data['sub_action'] == "invite_decline":
        __invite_decline(bot, update, invited_user)
    elif action.data['sub_action'] == "invite_accept":
        __invite_accept(bot, update, invited_user, action.data['squad_id'])


def __invite_decline(bot: Bot, update: Update, invited_user: User):
    bot.edit_message_text(
        MSG_SQUAD_ADD_DECLINED.format('@' + invited_user.username),
        update.callback_query.message.chat.id,
        update.callback_query.message.message_id
    )


def __invite_accept(bot: Bot, update: Update, invited_user: User, squad_id: int):
    member = Session.query(SquadMember).filter_by(user_id=invited_user.id).first()
    if not member:
        member = SquadMember()
        member.user_id = invited_user.id
        member.squad_id = squad_id
        member.approved = True
        Session.add(member)
        Session.commit()

        bot.edit_message_text(
            MSG_SQUAD_ADD_ACCEPTED.format('@' + invited_user.username),
            update.callback_query.message.chat.id,
            update.callback_query.message.message_id
        )
