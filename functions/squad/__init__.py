from datetime import datetime

from telegram import Bot, ParseMode, Update, InlineKeyboardButton, InlineKeyboardMarkup

from config import WAITING_ROOM_LINK, MINIMUM_SQUAD_MEMBER_LEVEL
from core.decorators import command_handler
from core.handler.callback import CallbackAction
from core.handler.callback.util import create_callback, get_callback_action
from core.texts import *
from core.texts import MSG_SQUAD_LEAVE_DECLINE, BTN_YES, BTN_NO, MSG_SQUAD_REQUESTED, MSG_SQUAD_REQUEST_NEW, \
    MSG_SQUAD_REQUEST_EXISTS
from core.types import (Admin, Session,
                        SquadMember, User, Squad)
from core.utils import send_async

from functions.squad.admin import generate_fire_up, generate_squad_invite_answer, generate_leave_squad
from functions.squad.util import __remove
from functions.reply_markup import generate_squad_markup

Session()


@command_handler()
def squad_about(bot: Bot, update: Update, user: User):
    admin = Session.query(Admin).filter(
        Admin.user_id == update.effective_user.id,
        Admin.admin_group != 0
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
            old_squad_name = __remove(bot, user)
            bot.edit_message_text(
                MSG_SQUAD_LEFT.format(user.character.name, old_squad_name),
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
        member = Session.query(SquadMember).filter_by(user_id=update.message.from_user.id).first()
        if member:
            squad = member.squad
            markup = __get_keyboard_leave(user)
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


def __get_keyboard_leave(user):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                BTN_YES,
                callback_data=create_callback(
                    CallbackAction.SQUAD_LEAVE,
                    user.id,
                    leave=True
                )
            ),
            InlineKeyboardButton(
                BTN_NO,
                callback_data=create_callback(
                    CallbackAction.SQUAD_LEAVE,
                    user.id,
                    leave=False
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
        admins = Session.query(Admin).filter_by(admin_group=member.squad.chat_id).all()
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
        for squad in Session.query(Squad).filter(Squad.hiring == True).all():
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
