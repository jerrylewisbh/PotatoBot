import json
from datetime import datetime, timedelta

from sqlalchemy import func, tuple_, collate
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode

from config import CASTLE
from core.commands import *
from core.decorators import command_handler
from core.handler.callback import CallbackAction, get_callback_action
from core.handler.callback.util import create_callback
from core.texts import MSG_TOP_WEEK_WARRIORS, MSG_TOP_ATTACK, MSG_TOP_DEFENCE, MSG_TOP_EXPERIENCE, \
    BTN_WEEK, BTN_ALL_TIME
from core.types import User, Session, Character, Report
from core.utils import send_async
from functions.top import get_top, gen_top_msg


def __get_top_attendance(user: User, date_filter):
    actual_profiles = Session.query(Character.user_id, func.max(Character.date)).group_by(Character.user_id)
    actual_profiles = actual_profiles.all()

    battles = Session.query(
        Character,
        func.count(Report.user_id)
    ).filter(
        tuple_(Character.user_id, Character.date).in_([(a[0], a[1]) for a in actual_profiles]),
        Character.date > datetime.now() - timedelta(days=7)
    ).outerjoin(
        Report, Report.user_id == Character.user_id
    ).filter(
        date_filter
    ).filter(
        Report.earned_exp > 0
    ).group_by(
        Character
    ).order_by(
        func.count(Report.user_id).desc()
    ).filter(
        Character.castle == collate(CASTLE, 'utf8mb4_unicode_520_ci')
    ).all()

    text = gen_top_msg(battles, user.id, MSG_TOP_WEEK_WARRIORS, '⛳️')
    additional_markup = [
        InlineKeyboardButton(
            TOP_COMMAND_BATTLES_WEEK,
            callback_data=create_callback(
                CallbackAction.TOP | CallbackAction.TOP_ATT | CallbackAction.TOP_FILTER_WEEK,
                user.id
            )
        ),
        InlineKeyboardButton(
            TOP_COMMAND_BATTLES_MONTH,
            callback_data=create_callback(
                CallbackAction.TOP | CallbackAction.TOP_ATT | CallbackAction.TOP_FILTER_MONTH,
                user.id
            )
        ),
        InlineKeyboardButton(
            TOP_COMMAND_BATTLES_ALL,
            callback_data=create_callback(
                CallbackAction.TOP | CallbackAction.TOP_ATT | CallbackAction.TOP_FILTER_ALL,
                user.id
            )
        ),
    ]
    return text, additional_markup


@command_handler()
def top(bot: Bot, update: Update, user: User):
    text = ""
    keys = [
        [
            InlineKeyboardButton(
                TOP_COMMAND_ATTACK,
                callback_data=create_callback(
                    CallbackAction.TOP | CallbackAction.TOP_ATK,
                    user.id
                )
            ),
            InlineKeyboardButton(
                TOP_COMMAND_DEFENCE,
                callback_data=create_callback(
                    CallbackAction.TOP | CallbackAction.TOP_DEF,
                    user.id
                )
            ),
            InlineKeyboardButton(
                TOP_COMMAND_EXP,
                callback_data=create_callback(
                    CallbackAction.TOP | CallbackAction.TOP_EXP,
                    user.id
                )
            ),
            InlineKeyboardButton(
                TOP_COMMAND_BATTLES,
                callback_data=create_callback(
                    CallbackAction.TOP | CallbackAction.TOP_ATT,
                    user.id
                )
            )
        ]
    ]

    if not update.callback_query:
        # Initial call...
        text = get_top(Character.attack.desc(), MSG_TOP_ATTACK, 'attack', '⚔', user)
        send_async(
            bot,
            chat_id=user.id,
            text=text,
            reply_markup=InlineKeyboardMarkup(keys),
            parse_mode=ParseMode.HTML,
        )
    else:
        # Call with callback_query
        action = get_callback_action(update.callback_query.data, user.id)
        if CallbackAction.TOP_ATK in action.action:
            text = get_top(Character.attack.desc(), MSG_TOP_ATTACK, 'attack', '⚔', user)
        elif CallbackAction.TOP_DEF in action.action:
            text = get_top(Character.defence.desc(), MSG_TOP_DEFENCE, 'defence', '🛡', user)
        elif CallbackAction.TOP_EXP in action.action:
            text = get_top(Character.exp.desc(), MSG_TOP_EXPERIENCE, 'exp', '🔥', user)
        elif CallbackAction.TOP_ATT in action.action:
            if CallbackAction.TOP_FILTER_MONTH in action.action:
                text, additional_keyboard = __get_top_attendance(
                    user,
                    date_filter=Report.date > datetime(2017, 12, 11)
                )
            elif CallbackAction.TOP_FILTER_ALL in action.action:
                text, additional_keyboard = __get_top_attendance(
                    user,
                    Report.date >= datetime.today().replace(day=1, hour=0, minute=0, second=0)
                )
            else:
                # By default show week
                text, additional_keyboard = __get_top_attendance(
                    user,
                    Report.date > datetime.today().date() - timedelta(days=datetime.today().date().weekday())
                )
            keys.append(additional_keyboard)

        bot.edit_message_text(
            chat_id=user.id,
            message_id=update.callback_query.message.message_id,
            text=text,
            reply_markup=InlineKeyboardMarkup(keys),
            parse_mode=ParseMode.HTML,
        )
