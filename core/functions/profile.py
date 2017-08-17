from telegram import Update, Bot, ParseMode
import logging

from core.functions.inline_keyboard_handling import generate_profile_buttons
from core.functions.triggers import trigger_decorator
from core.regexp import hero, profile
from core.types import AdminType, Admin, Stock, Character, User, admin, session, data_update, Equip
from core.utils import send_async
from core.functions.reply_markup import generate_standard_markup
from enum import Enum
from datetime import datetime, timedelta
import re
from core import regexp
from core.template import fill_char_template
from core.texts import *


def parse_profile(profile, user_id, date):
        parsed_data = re.search(regexp.profile, profile)
        char = session.query(Character).filter_by(user_id=user_id, date=date).first()
        if char is None:
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


def parse_hero(profile, user_id, date):
    parsed_data = re.search(regexp.hero, profile)
    char = session.query(Character).filter_by(user_id=user_id, date=date).first()
    if char is None:
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
        if parsed_data.group(18):
            char.pet = str(parsed_data.group(18))
            char.petLevel = int(parsed_data.group(20))
        if parsed_data.group(15):
            equip = Equip()
            equip.user_id = user_id
            equip.date = date
            equip.equip = str(parsed_data.group(15))
            session.add(equip)
        session.add(char)
        session.commit()
    return char


def char_update(bot: Bot, update: Update):
    if update.message.date - update.message.forward_date > timedelta(minutes=1):
        send_async(bot, chat_id=update.message.chat.id, text=MSG_PROFILE_OLD)
    else:
        char = None
        if re.search(hero, update.message.text):
            char = parse_hero(update.message.text, update.message.from_user.id, update.message.forward_date)
        elif re.search(profile, update.message.text):
            char = parse_profile(update.message.text, update.message.from_user.id, update.message.forward_date)
        if char and char.castle == '🇲🇴':
            send_async(bot, chat_id=update.message.chat.id, text=MSG_PROFILE_SAVED.format(char.name))
        else:
            send_async(bot, chat_id=update.message.chat.id,
                       text=MSG_PROFILE_CASTLE_MISTAKE)


def char_show(bot: Bot, update: Update):
    if update.message.chat.type == 'private':
        user = session.query(User).filter_by(id=update.message.from_user.id).first()
        if user is not None and user.character is not None:
            char =user.character
            if char.castle == '🇲🇴':
                text = fill_char_template(MSG_PROFILE_SHOW_FORMAT, user, char)
                btns = generate_profile_buttons(user)
                send_async(bot, chat_id=update.message.chat.id, text=text, reply_markup=btns)


#@data_update
@admin()
def find_by_username(bot: Bot, update: Update):
    if update.message.chat.type == 'private':
        msg = update.message.text.split(' ', 1)[1]
        msg = msg.replace('@', '')
        if msg != '':
            user = session.query(User).filter_by(username=msg).first()
            if user is not None and len(user.character) >= 1:
                char = user.character
                text = fill_char_template(MSG_PROFILE_SHOW_FORMAT, user, char)
                btns = generate_profile_buttons(user)
                send_async(bot, chat_id=update.message.chat.id, text=text, reply_markup=btns)
            else:
                send_async(bot, chat_id=update.message.chat.id, text=MSG_PROFILE_NOT_FOUND)
