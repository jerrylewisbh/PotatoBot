import logging
from datetime import datetime, timedelta
from sqlalchemy import func, tuple_, collate
from telegram import Update, ParseMode

from config import CASTLE
from core.bot import MQBot
from core.decorators import command_handler
from core.texts import *
from core.texts import MSG_TOP_FORMAT
from core.types import Character, Session, Squad, SquadMember, User, Report
from core.utils import send_async
from functions.reply_markup import generate_top_markup

Session()


@command_handler()
def top_about(bot: MQBot,update: Update, user: User):
    markup = generate_top_markup()
    send_async(
        bot,
        chat_id=update.message.chat.id,
        text=MSG_TOP_ABOUT,
        reply_markup=markup
    )


def get_top(condition, header, field_name, icon, user, filter_by_squad=False):
    newest_profiles = Session.query(
        Character.user_id,
        func.max(Character.date)
    ).group_by(Character.user_id).all()

    # Remove all accounts where we have one non ptt castle occurence...
    logging.debug("get_top: Filter by castle")
    if filter_by_squad:
        characters = Session.query(Character).filter(
            tuple_(Character.user_id, Character.date).in_([(a[0], a[1]) for a in newest_profiles]),
            Character.date > datetime.now() - timedelta(days=7),
            Character.castle == collate(CASTLE, 'utf8mb4_unicode_520_ci'),
            Squad.chat_id == user.member.squad.chat_id,
            SquadMember.approved.is_(True)
        ).join(User).join(SquadMember).join(Squad).order_by(condition).all()
    else:
        characters = Session.query(Character).filter(
            tuple_(Character.user_id, Character.date).in_([(a[0], a[1]) for a in newest_profiles]),
            Character.date > datetime.now() - timedelta(days=7),
            Character.castle == collate(CASTLE, 'utf8mb4_unicode_520_ci')
        ).join(User).order_by(condition).all()

    text = "<b>" + header + "</b>"
    str_format = MSG_TOP_FORMAT
    for i in range(min(10, len(characters))):
        text += str_format.format(i + 1, characters[i].name, characters[i].level,
                                  getattr(characters[i], field_name), icon)
    if user.id in [character.user_id for character in characters]:
        if user.id not in [character.user_id for character in characters[:10]]:
            for i in range(10, len(characters)):
                if characters[i].user_id == user.id:
                    text += '...\n'
                    text += str_format.format(i, characters[i - 1].name, characters[i - 1].level,
                                              getattr(characters[i - 1], field_name), icon)
                    text += str_format.format(i + 1, characters[i].name, characters[i].level,
                                              getattr(characters[i], field_name), icon)
                    if i != len(characters) - 1:
                        text += str_format.format(i + 2, characters[i + 1].name, characters[i + 1].level,
                                                  getattr(characters[i + 1], field_name), icon)
                    break
    return text


def __get_attendence(bot: MQBot,update: Update, user: User):
    # Battle stats for squad
    actual_profiles = Session.query(Character.user_id, func.max(Character.date)). \
        group_by(Character.user_id)
    actual_profiles = actual_profiles.all()
    today = datetime.today().date()
    battles = Session.query(Character, func.count(Report.user_id)).filter(
        tuple_(Character.user_id, Character.date).in_([(a[0], a[1]) for a in actual_profiles]),
        Character.date > datetime.now() - timedelta(days=7),
        Squad.chat_id == user.member.squad.chat_id,
        SquadMember.approved.is_(True)
    ).outerjoin(Report, Report.user_id == Character.user_id).join(User).join(SquadMember).filter(
        Report.date > today - timedelta(days=today.weekday())
    ).filter(Report.earned_exp > 0).group_by(Character).order_by(func.count(Report.user_id).desc())

    battles = battles.filter(Character.castle == CASTLE).all()
    user_id = user.id
    text_battle = gen_top_msg(battles, user_id, MSG_TOP_WEEK_WARRIORS, '⛳️')

    send_async(
        bot,
        chat_id=update.message.chat.id,
        text=MSG_TOP_SQUAD + "\n",
        parse_mode=ParseMode.HTML,
    )


def gen_top_msg(data, user_id, header, icon):
    text = "<b>" + header + "</b>"
    str_format = MSG_TOP_FORMAT
    for i in range(min(10, len(data))):
        text += str_format.format(i + 1, data[i][0].name, data[i][0].level,
                                  data[i][1], icon)
    if len(data) and hasattr(data[0][0], 'user_id') and user_id in [build[0].user_id for build in data]:
        if user_id not in [build[0].user_id for build in data[:10]]:
            for i in range(10, len(data)):
                if data[i][0].user_id == user_id:
                    text += '...\n'
                    text += str_format.format(i, data[i - 1][0].name, data[i - 1][0].level,
                                              data[i - 1][1], icon)
                    text += str_format.format(i + 1, data[i][0].name, data[i][0].level,
                                              data[i][1], icon)
                    if i != len(data) - 1:
                        text += str_format.format(i + 2, data[i + 1][0].name, data[i + 1][0].level,
                                                  data[i + 1][1], icon)
                    break
    return text
