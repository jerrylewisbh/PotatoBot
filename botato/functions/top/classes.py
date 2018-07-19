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
from core.model import User, Character, Report
from functions.top import get_top, __gen_top_msg


def gen_class_top_msg(data, counts, header, icon):
    text = header
    str_format = MSG_TOP_FORMAT
    for i in range(min(10, len(data))):
        squad_count = 1
        for squad, count in counts:
            if squad.chat_id == data[i][0].chat_id:
                squad_count = count
                break
        text += str_format.format(i + 1, data[i][0].squad_name, squad_count,
                                  data[i][1], icon, round(data[i][1] / squad_count, 2), icon)
    return text


def __get_top_attendance(user: User, date_filter, class_name, date_desc):
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
        date_filter,
        Character.characterClass.ilike(class_name),
    ).filter(
        Report.earned_exp > 0
    ).group_by(
        Character
    ).order_by(
        func.count(Report.user_id).desc()
    ).filter(
        Character.castle == collate(CASTLE, 'utf8mb4_unicode_520_ci')
    ).all()

    text = __gen_top_msg(battles, user.id, MSG_TOP_WEEK_WARRIORS_CLASS.format(class_name, date_desc), '⛳️')
    additional_markup = [
        InlineKeyboardButton(
            TOP_COMMAND_BATTLES_WEEK,
            callback_data=create_callback(
                CallbackAction.TOP | CallbackAction.TOP_FILTER_CLASS | CallbackAction.TOP_ATT | CallbackAction.TOP_FILTER_WEEK,
                user.id,
                class_name=class_name
            )
        ),
        InlineKeyboardButton(
            TOP_COMMAND_BATTLES_MONTH,
            callback_data=create_callback(
                CallbackAction.TOP | CallbackAction.TOP_FILTER_CLASS | CallbackAction.TOP_ATT | CallbackAction.TOP_FILTER_MONTH,
                user.id,
                class_name=class_name
            )
        ),
        InlineKeyboardButton(
            TOP_COMMAND_BATTLES_ALL,
            callback_data=create_callback(
                CallbackAction.TOP | CallbackAction.TOP_FILTER_CLASS | CallbackAction.TOP_ATT | CallbackAction.TOP_FILTER_ALL,
                user.id,
                class_name=class_name
            )
        ),
    ]
    return text, additional_markup


@command_handler()
def top(bot: MQBot, update: Update, user: User):
    class_name = 'Knight'
    text = ""

    action = None
    if update.callback_query:
        action = get_callback_action(update.callback_query.data, user.id)
        if "class_name" in action.data:
            class_name = action.data["class_name"]

    if not update.callback_query:
        # Initial call...
        text = get_top(
            Character.attack.desc(),
            MSG_TOP_ATTACK_CLASS.format(class_name),
            'attack',
            '⚔',
            user,
            filter_by_squad=False,
            character_class="Knight"
        )
        class_buttons = __get_class_keyboard(user)

        send_async(
            bot,
            chat_id=user.id,
            text="Please choose the class you want to get the statistics for.",
            reply_markup=InlineKeyboardMarkup(class_buttons),
            parse_mode=ParseMode.HTML,
        )
    else:
        # Call with callback_query
        keys = [
            [
                InlineKeyboardButton(
                    TOP_COMMAND_ATTACK,
                    callback_data=create_callback(
                        CallbackAction.TOP | CallbackAction.TOP_ATK | CallbackAction.TOP_FILTER_CLASS,
                        user.id,
                        class_name=class_name
                    )
                ),
                InlineKeyboardButton(
                    TOP_COMMAND_DEFENCE,
                    callback_data=create_callback(
                        CallbackAction.TOP | CallbackAction.TOP_DEF | CallbackAction.TOP_FILTER_CLASS,
                        user.id,
                        class_name=class_name
                    )
                ),
                InlineKeyboardButton(
                    TOP_COMMAND_EXP,
                    callback_data=create_callback(
                        CallbackAction.TOP | CallbackAction.TOP_EXP | CallbackAction.TOP_FILTER_CLASS,
                        user.id,
                        class_name=class_name
                    )
                ),
                InlineKeyboardButton(
                    TOP_COMMAND_BATTLES,
                    callback_data=create_callback(
                        CallbackAction.TOP | CallbackAction.TOP_ATT | CallbackAction.TOP_FILTER_CLASS,
                        user.id,
                        class_name=class_name
                    )
                )
            ],
            [
                InlineKeyboardButton(
                    USER_COMMAND_BACK,
                    callback_data=create_callback(
                        CallbackAction.TOP | CallbackAction.TOP_FILTER_CLASS,
                        user.id,
                        class_name=class_name
                    )
                )
            ]
        ]

        if CallbackAction.TOP_ATK in action.action:
            text = get_top(
                Character.attack.desc(),
                MSG_TOP_ATTACK_CLASS.format(class_name),
                'attack',
                '⚔',
                user,
                filter_by_squad=False,
                character_class=class_name
            )
        elif CallbackAction.TOP_DEF in action.action:
            text = get_top(
                Character.defence.desc(),
                MSG_TOP_DEFENCE_CLASS.format(class_name),
                'defence',
                '🛡',
                user,
                filter_by_squad=False,
                character_class=class_name)
        elif CallbackAction.TOP_EXP in action.action:
            text = get_top(
                Character.exp.desc(),
                MSG_TOP_EXPERIENCE_CLASS.format(class_name),
                'exp',
                '🔥',
                user,
                filter_by_squad=False,
                character_class=class_name)
        elif CallbackAction.TOP_ATT in action.action:
            if CallbackAction.TOP_FILTER_ALL in action.action:
                text, additional_keyboard = __get_top_attendance(
                    user,
                    Report.date > datetime(2017, 12, 11),
                    class_name,
                    "this month"
                )
            elif CallbackAction.TOP_FILTER_MONTH in action.action:
                text, additional_keyboard = __get_top_attendance(
                    user,
                    Report.date >= datetime.today().replace(day=1, hour=0, minute=0, second=0),
                    class_name,
                    "since the beginning of time"
                )
            else:
                # By default show week
                text, additional_keyboard = __get_top_attendance(
                    user,
                    Report.date > datetime.today().date() - timedelta(days=datetime.today().date().weekday()),
                    class_name,
                    "this week"
                )
            text = "" + text
            keys.insert(1, additional_keyboard)
        else:
            class_buttons = __get_class_keyboard(user)

            bot.edit_message_text(
                chat_id=user.id,
                message_id=update.callback_query.message.message_id,
                text="Please choose the class you want to get the statistics for.",
                reply_markup=InlineKeyboardMarkup(class_buttons),
                parse_mode=ParseMode.HTML,
            )

        bot.edit_message_text(
            chat_id=user.id,
            message_id=update.callback_query.message.message_id,
            text=text,
            reply_markup=InlineKeyboardMarkup(keys),
            parse_mode=ParseMode.HTML,
        )


def __get_class_keyboard(user):
    class_buttons = []
    class_buttons_esquire = [
        InlineKeyboardButton(
            '⚔️Knight',
            callback_data=create_callback(
                CallbackAction.TOP | CallbackAction.TOP_ATK | CallbackAction.TOP_FILTER_CLASS,
                user.id,
                class_name="Knight",
            )
        ),
        InlineKeyboardButton(
            '🛡Sentinel',
            callback_data=create_callback(
                CallbackAction.TOP | CallbackAction.TOP_ATK | CallbackAction.TOP_FILTER_CLASS,
                user.id,
                class_name="Sentinel",
            )
        ),
        InlineKeyboardButton(
            '🏹Ranger',
            callback_data=create_callback(
                CallbackAction.TOP | CallbackAction.TOP_ATK | CallbackAction.TOP_FILTER_CLASS,
                user.id,
                class_name="Ranger",
            )
        )
    ]
    class_buttons_master = [
        InlineKeyboardButton(
            '⚗️Alchemist',
            callback_data=create_callback(
                CallbackAction.TOP | CallbackAction.TOP_ATK | CallbackAction.TOP_FILTER_CLASS,
                user.id,
                class_name="Alchemist",
            )
        ),
        InlineKeyboardButton(
            '⚒️Blacksmith',
            callback_data=create_callback(
                CallbackAction.TOP | CallbackAction.TOP_ATK | CallbackAction.TOP_FILTER_CLASS,
                user.id,
                class_name="Blacksmith",
            )
        ),
        InlineKeyboardButton(
            '📦Collector',
            callback_data=create_callback(
                CallbackAction.TOP | CallbackAction.TOP_ATK | CallbackAction.TOP_FILTER_CLASS,
                user.id,
                class_name="Collector",
            )
        )
    ]
    class_buttons_other = [
        InlineKeyboardButton(
            '🐣Others',
            callback_data=create_callback(
                CallbackAction.TOP | CallbackAction.TOP_ATK | CallbackAction.TOP_FILTER_CLASS,
                user.id,
                class_name="Esquire / Master"
            )
        ),
    ]
    class_buttons.append(class_buttons_esquire)
    class_buttons.append(class_buttons_master)
    class_buttons.append(class_buttons_other)
    return class_buttons
