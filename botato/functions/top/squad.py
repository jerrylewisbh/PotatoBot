from datetime import datetime, timedelta
from sqlalchemy import func, collate, tuple_
from telegram import Update, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup

from config import CASTLE
from core.bot import MQBot
from core.utils import send_async
from core.commands import *
from core.decorators import command_handler
from core.handler.callback import CallbackAction, get_callback_action
from core.handler.callback.util import create_callback
from core.texts import *
from core.db import Session
from core.model import User, Character, Report, Squad, SquadMember
from functions.top import get_top, __gen_top_msg


def gen_squad_top_msg(data, counts, header, icon):
    text = header
    str_format = MSG_SQUAD_TOP_FORMAT
    for i in range(min(10, len(data))):
        squad_count = 1
        for squad, count in counts:
            if squad.chat_id == data[i][0].chat_id:
                squad_count = count
                break
        text += str_format.format(i + 1, data[i][0].squad_name, squad_count,
                                  data[i][1], icon, round(data[i][1] / squad_count, 2), icon)
    return text


def __get_top_attendance(user: User, date_filter, date_desc):
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
    ).join(User).join(SquadMember).join(Squad).filter(
        date_filter,
        Squad.chat_id == user.member.squad.chat_id,
        SquadMember.approved.is_(True),
    ).filter(
        Report.earned_exp > 0,
        Report.preliminary_report.is_(False),
    ).group_by(
        Character
    ).order_by(
        func.count(Report.user_id).desc()
    ).filter(
        Character.castle == collate(CASTLE, 'utf8mb4_unicode_520_ci')
    ).all()

    text = __gen_top_msg(battles, user.id, MSG_TOP_WEEK_WARRIORS_SQUAD.format(user.member.squad.squad_name, date_desc), '⛳️')
    additional_markup = [
        InlineKeyboardButton(
            TOP_COMMAND_BATTLES_WEEK,
            callback_data=create_callback(
                CallbackAction.TOP | CallbackAction.TOP_FILTER_SQUAD | CallbackAction.TOP_ATT | CallbackAction.TOP_FILTER_WEEK,
                user.id
            )
        ),
        InlineKeyboardButton(
            TOP_COMMAND_BATTLES_MONTH,
            callback_data=create_callback(
                CallbackAction.TOP | CallbackAction.TOP_FILTER_SQUAD | CallbackAction.TOP_ATT | CallbackAction.TOP_FILTER_MONTH,
                user.id
            )
        ),
        InlineKeyboardButton(
            TOP_COMMAND_BATTLES_ALL,
            callback_data=create_callback(
                CallbackAction.TOP | CallbackAction.TOP_FILTER_SQUAD | CallbackAction.TOP_ATT | CallbackAction.TOP_FILTER_ALL,
                user.id
            )
        ),
    ]
    return text, additional_markup


@command_handler()
def top(bot: MQBot, update: Update, user: User):
    text = ""
    keys = [
        [
            InlineKeyboardButton(
                TOP_COMMAND_ATTACK,
                callback_data=create_callback(
                    CallbackAction.TOP | CallbackAction.TOP_ATK | CallbackAction.TOP_FILTER_SQUAD,
                    user.id
                )
            ),
            InlineKeyboardButton(
                TOP_COMMAND_DEFENCE,
                callback_data=create_callback(
                    CallbackAction.TOP | CallbackAction.TOP_DEF | CallbackAction.TOP_FILTER_SQUAD,
                    user.id
                )
            ),
            InlineKeyboardButton(
                TOP_COMMAND_EXP,
                callback_data=create_callback(
                    CallbackAction.TOP | CallbackAction.TOP_EXP | CallbackAction.TOP_FILTER_SQUAD,
                    user.id
                )
            ),
            InlineKeyboardButton(
                TOP_COMMAND_BATTLES,
                callback_data=create_callback(
                    CallbackAction.TOP | CallbackAction.TOP_ATT | CallbackAction.TOP_FILTER_SQUAD,
                    user.id
                )
            )
        ]
    ]

    if not update.callback_query:
        # Initial call...
        text = get_top(
            Character.attack.desc(),
            MSG_TOP_ATTACK_SQUAD.format(user.member.squad.squad_name),
            'attack',
            '⚔',
            user,
            filter_by_squad=True
        )
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
            text = get_top(
                Character.attack.desc(),
                MSG_TOP_ATTACK_SQUAD.format(user.member.squad.squad_name),
                'attack',
                '⚔',
                user,
                filter_by_squad=True
            )
        elif CallbackAction.TOP_DEF in action.action:
            text = get_top(
                Character.defence.desc(),
                MSG_TOP_DEFENCE_SQUAD.format(user.member.squad.squad_name),
                'defence',
                '🛡',
                user,
                filter_by_squad=True)
        elif CallbackAction.TOP_EXP in action.action:
            text = get_top(
                Character.exp.desc(),
                MSG_TOP_EXPERIENCE_SQUAD.format(user.member.squad.squad_name),
                'exp',
                '🔥',
                user,
                filter_by_squad=True)
        elif CallbackAction.TOP_ATT in action.action:
            if CallbackAction.TOP_FILTER_ALL in action.action:
                text, additional_keyboard = __get_top_attendance(
                    user,
                    Report.date > datetime(2017, 12, 11),
                    "this month"
                )
            elif CallbackAction.TOP_FILTER_MONTH in action.action:
                text, additional_keyboard = __get_top_attendance(
                    user,
                    Report.date >= datetime.today().replace(day=1, hour=0, minute=0, second=0),
                    "since the beginning of time"
                )
            else:
                # By default show week
                text, additional_keyboard = __get_top_attendance(
                    user,
                    Report.date > datetime.today().date() - timedelta(days=datetime.today().date().weekday()),
                    "this week"
                )
            keys.append(additional_keyboard)

        bot.edit_message_text(
            chat_id=user.id,
            message_id=update.callback_query.message.message_id,
            text=text,
            reply_markup=InlineKeyboardMarkup(keys),
            parse_mode=ParseMode.HTML,
        )
