from sqlalchemy import func, text as text_, tuple_
from telegram import Update, Bot

from core.functions.reply_markup import generate_top_markup
from core.texts import MSG_TOP_ABOUT
from core.types import user_allowed, Character
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
    str_format = '{}. {} ({}🌟) - {}{}\n'
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
    text = get_top(Character.attack.desc(), session, '⚔Топ атакеры:\n', 'attack', '⚔', update.message.from_user.id)
    send_async(bot,
               chat_id=update.message.chat.id,
               text=text)


@user_allowed
def def_top(bot: Bot, update: Update, session):
    text = get_top(Character.defence.desc(), session, '🛡Топ дэферы:\n', 'defence', '🛡', update.message.from_user.id)
    send_async(bot,
               chat_id=update.message.chat.id,
               text=text)


@user_allowed
def exp_top(bot: Bot, update: Update, session):
    text = get_top(Character.exp.desc(), session, '🔥Топ качки:\n', 'exp', '🔥', update.message.from_user.id)
    send_async(bot,
               chat_id=update.message.chat.id,
               text=text)
