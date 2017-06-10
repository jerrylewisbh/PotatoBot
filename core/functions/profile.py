from telegram import Update, Bot, ParseMode
import logging
from core.functions.triggers import trigger_decorator
from core.types import AdminType, Admin, Stock, Character, User, admin, session
from core.utils import send_async
from core.functions.reply_markup import generate_standard_markup
from enum import Enum
from datetime import datetime, timedelta
import re
from core import regexp
from core.template import fill_char_template


def parse_profile(profile, user_id, date):
        parsed_data = re.search(regexp.profile, profile)

        char = Character()
        char.user_id = user_id
        char.date = date
        char.castle = str(parsed_data.group(1))
        char.name = str(parsed_data.group(2))
        char.prof = str(parsed_data.group(3))
        char.level = int(parsed_data.group(4))
        char.attack = int(parsed_data.group(5))
        char.defence = int(parsed_data.group(6))
        char.exp = int(parsed_data.group(7))
        char.needExp = int(parsed_data.group(8))
        char.maxStamina = int(parsed_data.group(10))
        char.gold = int(parsed_data.group(11))
        char.donateGold = int(parsed_data.group(12))
        if parsed_data.group(16):
            char.pet = str(parsed_data.group(16))
            char.petLevel = int(parsed_data.group(18))
        session.add(char)
        session.commit()
        return char


def char_update(bot: Bot, update: Update):
    if update.message.date - update.message.forward_date > timedelta(minutes=1):
        send_async(bot, chat_id=update.message.chat.id, text='Твой профиль завял, нужно что-то посвежей...')
    else:
        char = parse_profile(update.message.text, update.message.from_user.id, update.message.forward_date)
        send_async(bot, chat_id=update.message.chat.id, text='Располагайся в зарослях мяты, {}!\n'
                                                             'Не забывай поливать свой профиль хотя бы раз в день. 🌱'
                   .format(char.name))


def char_show(bot: Bot, update: Update):
    if update.message.chat.type == 'private':
        user = session.query(User).filter_by(id=update.message.from_user.id).first()
        if user is not None and user.character is not None:
            text = '👤 %first_name% (%username%)\n' \
                   '%castle% %name%\n' \
                   '🏅 %prof% %level% уровня\n' \
                   '⚜️ Отряд <В РАЗРАБОТКЕ>\n' \
                   '⚔️ %attack% | 🛡 %defence% | 🔥 %exp%/%needExp%\n' \
                   '💰 %gold% | 🔋 %maxStamina%\n' \
                   '🕑 Последнее обновление %date%'
            text = fill_char_template(text, user)
            send_async(bot, chat_id=update.message.chat.id, text=text)
