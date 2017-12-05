from sqlalchemy import func, text as text_, tuple_
from telegram import Update, Bot

from core.functions.reply_markup import generate_top_markup
from core.texts import MSG_TOP_ABOUT, MSG_TOP_FORMAT, MSG_TOP_ATTACK, MSG_TOP_DEFENCE, MSG_TOP_EXPERIENCE, \
    MSG_TOP_GLOBAL_BUILDERS, MSG_TOP_WEEK_BUILDERS, MSG_TOP_WEEK_WARRIORS
from core.types import user_allowed, Character, BuildReport, Report
from core.utils import send_async

from config import CASTLE

from datetime import datetime, timedelta


@user_allowed
def top_about(bot: Bot, update: Update, session):
    markup = generate_top_markup()
    send_async(bot,
               chat_id=update.message.chat.id,
               text=MSG_TOP_ABOUT,
               reply_markup=markup)


def get_top(condition, session, header, field_name, icon, user_id, additional_filter=text_('')):
    actual_profiles = session.query(Character.user_id, func.max(Character.date)). \
        group_by(Character.user_id)
    actual_profiles = actual_profiles.all()
    characters = session.query(Character).filter(tuple_(Character.user_id, Character.date)
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
                    text += str_format.format(i, characters[i - 1].name, characters[i-1].level,
                                              getattr(characters[i-1], field_name), icon)
                    text += str_format.format(i + 1, characters[i].name, characters[i].level,
                                              getattr(characters[i], field_name), icon)
                    if i != len(characters) - 1:
                        text += str_format.format(i + 2, characters[i + 1].name, characters[i+1].level,
                                                  getattr(characters[i+1], field_name), icon)
                    break
    return text


@user_allowed
def attack_top(bot: Bot, update: Update, session):
    text = get_top(Character.attack.desc(), session, MSG_TOP_ATTACK, 'attack', '⚔', update.message.from_user.id)
    send_async(bot,
               chat_id=update.message.chat.id,
               text=text)


@user_allowed
def def_top(bot: Bot, update: Update, session):
    text = get_top(Character.defence.desc(), session, MSG_TOP_DEFENCE, 'defence', '🛡', update.message.from_user.id)
    send_async(bot,
               chat_id=update.message.chat.id,
               text=text)


@user_allowed
def exp_top(bot: Bot, update: Update, session):
    text = get_top(Character.exp.desc(), session, MSG_TOP_EXPERIENCE, 'exp', '🔥', update.message.from_user.id)
    send_async(bot,
               chat_id=update.message.chat.id,
               text=text)


@user_allowed
def global_build_top(bot: Bot, update: Update, session):
    actual_profiles = session.query(Character.user_id, func.max(Character.date)). \
        group_by(Character.user_id)
    actual_profiles = actual_profiles.all()
    builds = session.query(Character, func.count(BuildReport.user_id))\
        .filter(tuple_(Character.user_id, Character.date)
                .in_([(a[0], a[1]) for a in actual_profiles]),
                Character.date > datetime.now() - timedelta(days=7))\
        .outerjoin(BuildReport, BuildReport.user_id == Character.user_id).group_by(Character) \
        .filter(BuildReport.date > datetime(2017, 12, 1))\
        .order_by(func.count(BuildReport.user_id).desc())
    if CASTLE:
        builds = builds.filter(Character.castle == CASTLE)
    builds = builds.all()
    text = MSG_TOP_GLOBAL_BUILDERS
    str_format = MSG_TOP_FORMAT
    for i in range(min(10, len(builds))):
        text += str_format.format(i + 1, builds[i][0].name, builds[i][0].level,
                                  builds[i][1], '⚒')
    if update.message.from_user.id in [build[0].user_id for build in builds]:
        if update.message.from_user.id not in [build[0].user_id for build in builds[:10]]:
            for i in range(10, len(builds)):
                if builds[i][0].user_id == update.message.from_user.id:
                    text += '...\n'
                    text += str_format.format(i, builds[i - 1][0].name, builds[i-1][0].level,
                                              builds[i - 1][1], '⚒')
                    text += str_format.format(i + 1, builds[i][0].name, builds[i][0].level,
                                              builds[i][1], '⚒')
                    if i != len(builds) - 1:
                        text += str_format.format(i + 2, builds[i + 1][0].name, builds[i+1][0].level,
                                                  builds[i + 1][1], '⚒')
                    break
    send_async(bot,
               chat_id=update.message.chat.id,
               text=text)


@user_allowed
def week_build_top(bot: Bot, update: Update, session):
    actual_profiles = session.query(Character.user_id, func.max(Character.date)). \
        group_by(Character.user_id)
    actual_profiles = actual_profiles.all()
    today = datetime.today()
    builds = session.query(Character, func.count(BuildReport.user_id))\
        .filter(tuple_(Character.user_id, Character.date)
                .in_([(a[0], a[1]) for a in actual_profiles]),
                Character.date > datetime.now() - timedelta(days=7))\
        .outerjoin(BuildReport, BuildReport.user_id == Character.user_id).group_by(Character) \
        .filter(BuildReport.date > today - timedelta(days=today.weekday()))\
        .order_by(func.count(BuildReport.user_id).desc())
    if CASTLE:
        builds = builds.filter(Character.castle == CASTLE)
    builds = builds.all()
    text = MSG_TOP_WEEK_BUILDERS
    str_format = MSG_TOP_FORMAT
    for i in range(min(10, len(builds))):
        text += str_format.format(i + 1, builds[i][0].name, builds[i][0].level,
                                  builds[i][1], '⚒')
    if update.message.from_user.id in [build[0].user_id for build in builds]:
        if update.message.from_user.id not in [build[0].user_id for build in builds[:10]]:
            for i in range(10, len(builds)):
                if builds[i][0].user_id == update.message.from_user.id:
                    text += '...\n'
                    text += str_format.format(i, builds[i - 1][0].name, builds[i-1][0].level,
                                              builds[i - 1][1], '⚒')
                    text += str_format.format(i + 1, builds[i][0].name, builds[i][0].level,
                                              builds[i][1], '⚒')
                    if i != len(builds) - 1:
                        text += str_format.format(i + 2, builds[i + 1][0].name, builds[i+1][0].level,
                                                  builds[i + 1][1], '⚒')
                    break
    send_async(bot,
               chat_id=update.message.chat.id,
               text=text)


@user_allowed
def week_battle_top(bot: Bot, update: Update, session):
    actual_profiles = session.query(Character.user_id, func.max(Character.date)). \
        group_by(Character.user_id)
    actual_profiles = actual_profiles.all()
    today = datetime.today()
    battles = session.query(Character, func.count(Report.user_id))\
        .filter(tuple_(Character.user_id, Character.date)
                .in_([(a[0], a[1]) for a in actual_profiles]),
                Character.date > datetime.now() - timedelta(days=7))\
        .outerjoin(Report, Report.user_id == Character.user_id).group_by(Character) \
        .filter(Report.date > today - timedelta(days=today.weekday())) \
        .filter(Report.earned_exp > 1) \
        .order_by(func.count(Report.user_id).desc())
    if CASTLE:
        battles = battles.filter(Character.castle == CASTLE)
    battles = battles.all()
    text = MSG_TOP_WEEK_WARRIORS
    str_format = MSG_TOP_FORMAT
    for i in range(min(10, len(battles))):
        text += str_format.format(i + 1, battles[i][0].name, battles[i][0].level,
                                  battles[i][1], '⚔')
    if update.message.from_user.id in [build[0].user_id for build in battles]:
        if update.message.from_user.id not in [build[0].user_id for build in battles[:10]]:
            for i in range(10, len(battles)):
                if battles[i][0].user_id == update.message.from_user.id:
                    text += '...\n'
                    text += str_format.format(i, battles[i - 1][0].name, battles[i-1][0].level,
                                              battles[i - 1][1], '⚔')
                    text += str_format.format(i + 1, battles[i][0].name, battles[i][0].level,
                                              battles[i][1], '⚔')
                    if i != len(battles) - 1:
                        text += str_format.format(i + 2, battles[i + 1][0].name, battles[i+1][0].level,
                                                  battles[i + 1][1], '⚔')
                    break
    send_async(bot,
               chat_id=update.message.chat.id,
               text=text)

