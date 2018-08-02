import logging
from datetime import datetime, timedelta
from sqlalchemy import func, tuple_, collate
from telegram import Update, ParseMode

from config import CASTLE
from core.bot import MQBot
from core.utils import send_async
from core.decorators import command_handler
from core.texts import *
from core.texts import MSG_TOP_FORMAT
from core.db import Session
from core.model import User, Character, Report, Squad, SquadMember
from functions.reply_markup import generate_top_markup

Session()


@command_handler()
def top_about(bot: MQBot, update: Update, user: User):
    markup = generate_top_markup(user)
    send_async(
        bot,
        chat_id=update.message.chat.id,
        text=MSG_TOP_ABOUT,
        reply_markup=markup
    )


def get_top(condition, header, field_name, icon, user, character_class=None, filter_by_squad=False):
    newest_profiles = Session.query(
        Character.user_id,
        func.max(Character.date)
    ).group_by(Character.user_id).all()

    # Remove all accounts where we have one non ptt castle occurence...
    logging.debug("get_top: Filter by castle")

    # TODO: This is a workaround for empty classes for people who update manually....

    if character_class:
        if filter_by_squad:
            characters = Session.query(Character).filter(
                tuple_(Character.user_id, Character.date).in_([(a[0], a[1]) for a in newest_profiles]),
                Character.date > datetime.now() - timedelta(days=7),
                Character.castle == collate(CASTLE, 'utf8mb4_unicode_520_ci'),
                Squad.chat_id == user.member.squad.chat_id,
                SquadMember.approved.is_(True),
                Character.characterClass.ilike(character_class)
            ).join(User).join(SquadMember).join(Squad).order_by(condition).all()
        else:
            characters = Session.query(Character).filter(
                tuple_(Character.user_id, Character.date).in_([(a[0], a[1]) for a in newest_profiles]),
                Character.date > datetime.now() - timedelta(days=7),
                Character.castle == collate(CASTLE, 'utf8mb4_unicode_520_ci'),
                Character.characterClass.ilike(character_class)
            ).join(User).order_by(condition).all()
    else:
        if filter_by_squad:
            characters = Session.query(Character).filter(
                tuple_(Character.user_id, Character.date).in_([(a[0], a[1]) for a in newest_profiles]),
                Character.date > datetime.now() - timedelta(days=7),
                Character.castle == collate(CASTLE, 'utf8mb4_unicode_520_ci'),
                Squad.chat_id == user.member.squad.chat_id,
                SquadMember.approved.is_(True),
            ).join(User).join(SquadMember).join(Squad).order_by(condition).all()
        else:
            characters = Session.query(Character).filter(
                tuple_(Character.user_id, Character.date).in_([(a[0], a[1]) for a in newest_profiles]),
                Character.date > datetime.now() - timedelta(days=7),
                Character.castle == collate(CASTLE, 'utf8mb4_unicode_520_ci'),
            ).join(User).order_by(condition).all()

    text = "<b>" + header + "</b>"
    str_format = MSG_TOP_FORMAT
    str_format_reduced = MSG_TOP_FORMAT_REDUCED

    user_in_top_n = user.id in [character.user_id for character in characters[:3]]
    for i in range(min(3, len(characters))):
        if not user_in_top_n:
            text += str_format_reduced.format(
                i + 1,
                characters[i].name_with_guildtag,
                characters[i].level,
                getattr(characters[i], field_name),
                icon
            )
        else:
            text += str_format.format(
                i + 1,
                characters[i ].name_with_guildtag,
                characters[i].level,
                getattr(characters[i], field_name),
                icon
            )
    if user.id in [character.user_id for character in characters]:
        if user_in_top_n:
            for i in range(3, len(characters)):
                if characters[i].user_id == user.id:
                    text += '...\n'
                    text += str_format.format(i, characters[i - 1].name_with_guildtag, characters[i - 1].level,
                                              getattr(characters[i - 1], field_name), icon)
                    text += str_format.format(i + 1, characters[i].name_with_guildtag, characters[i].level,
                                              getattr(characters[i], field_name), icon)
                    if i != len(characters) - 1:
                        text += str_format.format(i + 2, characters[i + 1].name_with_guildtag, characters[i + 1].level,
                                                  getattr(characters[i + 1], field_name), icon)
                    break
    return text


def __gen_top_msg(data, user_id, header, icon):
    text = "<b>" + header + "</b>"
    str_format = MSG_TOP_FORMAT
    for i in range(min(3, len(data))):
        text += str_format.format(i + 1, data[i][0].name_with_guildtag, data[i][0].level, data[i][1], icon)

    if len(data) and hasattr(data[0][0], 'user_id') and user_id in [build[0].user_id for build in data]:
        if user_id not in [build[0].user_id for build in data[:3]]:
            for i in range(3, len(data)):
                if data[i][0].user_id == user_id:
                    text += '...\n'
                    text += str_format.format(i, data[i - 1][0].name_with_guildtag, data[i - 1][0].level, data[i - 1][1], icon)
                    text += str_format.format(i + 1, data[i][0].name_with_guildtag, data[i][0].level, data[i][1], icon)
                    if i != len(data) - 1:
                        text += str_format.format(i + 2, data[i + 1][0].name_with_guildtag, data[i + 1][0].level, data[i + 1][1], icon)
                    break
    return text
