from datetime import datetime, timedelta

from sqlalchemy import func, tuple_
from sqlalchemy import text as text_
from telegram import Bot, Update

from config import CASTLE
from core.decorators import command_handler
from core.texts import *
from core.types import (BuildReport, Character, Report, Session, Squad,
                        SquadMember, User)
from core.utils import send_async
from functions.inline_markup import generate_build_top, generate_battle_top
from functions.reply_markup import generate_top_markup

TOP_START_DATE = datetime(2017, 12, 11)

Session()


@command_handler()
def top_about(bot: Bot, update: Update, user: User):
    markup = generate_top_markup()
    send_async(bot,
               chat_id=update.message.chat.id,
               text=MSG_TOP_ABOUT,
               reply_markup=markup)


def get_top(condition, header, field_name, icon, user_id, additional_filter=text_('')):
    actual_profiles = Session.query(Character.user_id, func.max(Character.date)). \
        group_by(Character.user_id)
    actual_profiles = actual_profiles.all()
    characters = Session.query(Character).filter(tuple_(Character.user_id, Character.date)
                                                 .in_([(a[0], a[1]) for a in actual_profiles]),
                                                 Character.date > datetime.now() - timedelta(days=7),
                                                 additional_filter)\
        .order_by(condition)
    if CASTLE:
        characters = characters.filter_by(castle=CASTLE)
    characters = characters.all()
    text = header
    str_format = MSG_TOP_FORMAT
    for i in range(min(10, len(characters))):
        text += str_format.format(i + 1, characters[i].name, characters[i].level,
                                  getattr(characters[i], field_name), icon)
    if user_id in [character.user_id for character in characters]:
        if user_id not in [character.user_id for character in characters[:10]]:
            for i in range(10, len(characters)):
                if characters[i].user_id == user_id:
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


@command_handler()
def attack_top(bot: Bot, update: Update, user: User):
    text = get_top(Character.attack.desc(), MSG_TOP_ATTACK, 'attack', '⚔', update.message.from_user.id)
    send_async(bot,
               chat_id=update.message.chat.id,
               text=text)


@command_handler()
def def_top(bot: Bot, update: Update, user: User):
    text = get_top(Character.defence.desc(), MSG_TOP_DEFENCE, 'defence', '🛡', update.message.from_user.id)
    send_async(bot,
               chat_id=update.message.chat.id,
               text=text)


@command_handler()
def exp_top(bot: Bot, update: Update, user: User):
    text = get_top(Character.exp.desc(), MSG_TOP_EXPERIENCE, 'exp', '🔥', update.message.from_user.id)
    send_async(bot,
               chat_id=update.message.chat.id,
               text=text)


def gen_top_msg(data, user_id, header, icon):
    text = header
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


@command_handler()
def global_build_top(bot: Bot, update: Update, user: User):
    actual_profiles = Session.query(Character.user_id, func.max(Character.date)). \
        group_by(Character.user_id)
    actual_profiles = actual_profiles.all()
    builds = Session.query(Character, func.count(BuildReport.user_id))\
        .filter(tuple_(Character.user_id, Character.date)
                .in_([(a[0], a[1]) for a in actual_profiles]),
                Character.date > datetime.now() - timedelta(days=7))\
        .outerjoin(BuildReport, BuildReport.user_id == Character.user_id) \
        .filter(BuildReport.date > TOP_START_DATE).group_by(Character)\
        .order_by(func.count(BuildReport.user_id).desc())
    if CASTLE:
        builds = builds.filter(Character.castle == CASTLE)
    builds = builds.all()
    user_id = 0
    if update.message:
        user_id = update.message.from_user.id
    elif update.callback_query:
        user_id = update.callback_query.from_user.id
    text = gen_top_msg(builds, user_id, MSG_TOP_GLOBAL_BUILDERS, '⚒')
    markup = generate_build_top()
    if update.message:
        send_async(bot,
                   chat_id=update.message.chat.id,
                   text=text, reply_markup=markup)
    elif update.callback_query:
        bot.editMessageText(text, update.callback_query.message.chat.id, update.callback_query.message.message_id,
                            reply_markup=markup)


@command_handler()
def week_build_top(bot: Bot, update: Update, user: User):
    actual_profiles = Session.query(Character.user_id, func.max(Character.date)). \
        group_by(Character.user_id)
    actual_profiles = actual_profiles.all()
    today = datetime.today().date()
    builds = Session.query(Character, func.count(BuildReport.user_id))\
        .filter(tuple_(Character.user_id, Character.date)
                .in_([(a[0], a[1]) for a in actual_profiles]),
                Character.date > datetime.now() - timedelta(days=7))\
        .outerjoin(BuildReport, BuildReport.user_id == Character.user_id) \
        .filter(BuildReport.date > today - timedelta(days=today.weekday())).group_by(Character)\
        .order_by(func.count(BuildReport.user_id).desc())
    if CASTLE:
        builds = builds.filter(Character.castle == CASTLE)
    builds = builds.all()
    user_id = 0
    if update.message:
        user_id = update.message.from_user.id
    elif update.callback_query:
        user_id = update.callback_query.from_user.id
    text = gen_top_msg(builds, user_id, MSG_TOP_WEEK_BUILDERS, '⚒')
    markup = generate_build_top()
    if update.message:
        send_async(bot,
                   chat_id=update.message.chat.id,
                   text=text, reply_markup=markup)
    elif update.callback_query:
        bot.editMessageText(text, update.callback_query.message.chat.id, update.callback_query.message.message_id,
                            reply_markup=markup)


@command_handler()
def week_squad_build_top(bot: Bot, update: Update, user: User):
    actual_profiles = Session.query(Character.user_id, func.max(Character.date)). \
        group_by(Character.user_id)
    actual_profiles = actual_profiles.all()
    today = datetime.today().date()
    builds = Session.query(Squad, func.count(BuildReport.user_id))\
        .join(SquadMember).join(Character, SquadMember.user_id == Character.user_id)\
        .filter(tuple_(Character.user_id, Character.date)
                .in_([(a[0], a[1]) for a in actual_profiles]),
                Character.date > datetime.now() - timedelta(days=7))\
        .outerjoin(BuildReport, BuildReport.user_id == Character.user_id) \
        .filter(BuildReport.date > today - timedelta(days=today.weekday()))\
        .order_by(func.count(BuildReport.user_id).desc())
    if CASTLE:
        builds = builds.filter(Character.castle == CASTLE)
    builds = builds.group_by(Squad).all()
    counts = Session.query(Squad, func.count(SquadMember.user_id)).join(SquadMember).group_by(Squad)
    text = gen_squad_top_msg(builds, counts, MSG_TOP_WEEK_BUILDERS, '⚒')
    markup = generate_build_top()
    if update.message:
        send_async(bot,
                   chat_id=update.message.chat.id,
                   text=text, reply_markup=markup)
    elif update.callback_query:
        bot.editMessageText(text, update.callback_query.message.chat.id, update.callback_query.message.message_id,
                            reply_markup=markup)


@command_handler()
def global_squad_build_top(bot: Bot, update: Update, user: User):
    actual_profiles = Session.query(Character.user_id, func.max(Character.date)). \
        group_by(Character.user_id)
    actual_profiles = actual_profiles.all()
    builds = Session.query(Squad, func.count(BuildReport.user_id))\
        .join(SquadMember).join(Character, SquadMember.user_id == Character.user_id)\
        .filter(tuple_(Character.user_id, Character.date)
                .in_([(a[0], a[1]) for a in actual_profiles]),
                Character.date > datetime.now() - timedelta(days=7))\
        .outerjoin(BuildReport, BuildReport.user_id == Character.user_id) \
        .filter(BuildReport.date > TOP_START_DATE) \
        .order_by(func.count(BuildReport.user_id).desc())
    if CASTLE:
        builds = builds.filter(Character.castle == CASTLE)
    builds = builds.group_by(Squad).all()
    counts = Session.query(Squad, func.count(SquadMember.user_id)).join(SquadMember).group_by(Squad)
    text = gen_squad_top_msg(builds, counts, MSG_TOP_GLOBAL_BUILDERS, '⚒')
    markup = generate_build_top()
    if update.message:
        send_async(bot,
                   chat_id=update.message.chat.id,
                   text=text, reply_markup=markup)
    elif update.callback_query:
        bot.editMessageText(text, update.callback_query.message.chat.id, update.callback_query.message.message_id,
                            reply_markup=markup)


@command_handler()
def week_battle_top(bot: Bot, update: Update, user: User):
    actual_profiles = Session.query(Character.user_id, func.max(Character.date)). \
        group_by(Character.user_id)
    actual_profiles = actual_profiles.all()
    today = datetime.today().date()
    battles = Session.query(Character, func.count(Report.user_id))\
        .filter(tuple_(Character.user_id, Character.date)
                .in_([(a[0], a[1]) for a in actual_profiles]),
                Character.date > datetime.now() - timedelta(days=7))\
        .outerjoin(Report, Report.user_id == Character.user_id) \
        .filter(Report.date > today - timedelta(days=today.weekday())) \
        .filter(Report.earned_exp > 0).group_by(Character) \
        .order_by(func.count(Report.user_id).desc())
    if CASTLE:
        battles = battles.filter(Character.castle == CASTLE)
    battles = battles.all()
    user_id = 0
    if update.message:
        user_id = update.message.from_user.id
    elif update.callback_query:
        user_id = update.callback_query.from_user.id
    text = gen_top_msg(battles, user_id, MSG_TOP_WEEK_WARRIORS, '⛳️')
    markup = generate_battle_top()
    if update.message:
        send_async(bot,
                   chat_id=update.message.chat.id,
                   text=text, reply_markup=markup)
    elif update.callback_query:
        bot.editMessageText(text, update.callback_query.message.chat.id, update.callback_query.message.message_id,
                            reply_markup=markup)


@command_handler()
def global_battle_top(bot: Bot, update: Update, user: User):
    actual_profiles = Session.query(Character.user_id, func.max(Character.date)). \
        group_by(Character.user_id)
    actual_profiles = actual_profiles.all()
    battles = Session.query(Character, func.count(Report.user_id))\
        .filter(tuple_(Character.user_id, Character.date)
                .in_([(a[0], a[1]) for a in actual_profiles]),
                Character.date > datetime.now() - timedelta(days=7))\
        .outerjoin(Report, Report.user_id == Character.user_id) \
        .filter(Report.earned_exp > 0) \
        .filter(Report.date > TOP_START_DATE).group_by(Character) \
        .order_by(func.count(Report.user_id).desc())
    if CASTLE:
        battles = battles.filter(Character.castle == CASTLE)
    battles = battles.all()
    user_id = 0
    if update.message:
        user_id = update.message.from_user.id
    elif update.callback_query:
        user_id = update.callback_query.from_user.id
    text = gen_top_msg(battles, user_id, MSG_TOP_WEEK_WARRIORS, '⛳️')
    markup = generate_battle_top()
    if update.message:
        send_async(bot,
                   chat_id=update.message.chat.id,
                   text=text, reply_markup=markup)
    elif update.callback_query:
        bot.editMessageText(text, update.callback_query.message.chat.id, update.callback_query.message.message_id,
                            reply_markup=markup)
