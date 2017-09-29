from telegram import Update, Bot

from core.functions.inline_keyboard_handling import generate_profile_buttons
from core.regexp import HERO, PROFILE, REPORT
from core.types import Character, User, admin_allowed, Equip, user_allowed
from core.utils import send_async
from datetime import timedelta
import re
from core.template import fill_char_template
from core.texts import *


def parse_profile(profile, user_id, date, session):
    parsed_data = re.search(PROFILE, profile)
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


def parse_hero(profile, user_id, date, session):
    parsed_data = re.search(HERO, profile)
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


def parse_reports(report, user_id, date, session):
    parsed_data = re.search(REPORT, report)
    char = session.query(Character).filter_by(user_id=user_id, date=date).first()
    if char is None:
        char = Character()
        char.user_id = user_id
        char.date = date
        char.castle = str(parsed_data.group(1))
        char.name = str(parsed_data.group(2))
        char.attack = str(parsed_data.group(3))
        char.defence = str(parsed_data.group(4))
        char.level = int(parsed_data.group(5))
        char.level = int(parsed_data.group(5))
        char.level = int(parsed_data.group(5))
        char.earned_exp = int(parsed_data.group(6))
        char.earned_gold = int(parsed_data.group(7))
        char.earned_stock = int(parsed_data.group(8))
        session.add(char)
        session.commit()
    return char

@user_allowed
def char_update(bot: Bot, update: Update, session):
    if update.message.date - update.message.forward_date > timedelta(minutes=1):
        send_async(bot, chat_id=update.message.chat.id, text=MSG_PROFILE_OLD)
    else:
        char = None
        if re.search(HERO, update.message.text):
            char = parse_hero(update.message.text,
                              update.message.from_user.id,
                              update.message.forward_date,
                              session)
        elif re.search(PROFILE, update.message.text):
            char = parse_profile(update.message.text,
                                 update.message.from_user.id,
                                 update.message.forward_date,
                                 session)
        send_async(bot, chat_id=update.message.chat.id, text=MSG_PROFILE_SAVED.format(char.name))


@user_allowed
def char_show(bot: Bot, update: Update, session):
    if update.message.chat.type == 'private':
        user = session.query(User).filter_by(id=update.message.from_user.id).first()
        if user is not None and user.character is not None:
            char = user.character
            text = fill_char_template(MSG_PROFILE_SHOW_FORMAT, user, char)
            btns = generate_profile_buttons(user)
            send_async(bot, chat_id=update.message.chat.id, text=text, reply_markup=btns)


@admin_allowed()
def find_by_username(bot: Bot, update: Update, session):
    if update.message.chat.type == 'private':
        msg = update.message.text.split(' ', 1)[1]
        msg = msg.replace('@', '')
        if msg != '':
            user = session.query(User).filter_by(username=msg).first()
            if user is not None and user.character:
                char = user.character
                text = fill_char_template(MSG_PROFILE_SHOW_FORMAT, user, char)
                btns = generate_profile_buttons(user)
                send_async(bot, chat_id=update.message.chat.id, text=text, reply_markup=btns)
            else:
                send_async(bot, chat_id=update.message.chat.id, text=MSG_PROFILE_NOT_FOUND)
