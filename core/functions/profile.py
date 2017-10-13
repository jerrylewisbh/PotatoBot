from telegram import Update, Bot, ParseMode

from core.functions.inline_keyboard_handling import generate_profile_buttons
from core.regexp import HERO, PROFILE, REPORT
from core.types import Character, Report, User, admin_allowed, Equip, user_allowed
from core.utils import send_async
from datetime import timedelta, datetime
import re
from core.template import fill_char_template
from core.texts import *

from config import CASTLE


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
    report = session.query(Report).filter_by(user_id=user_id, date=date).first()
    if report is None:
        report = Report()
        report.user_id = user_id
        report.date = date
        report.castle = str(parsed_data.group(1))
        report.name = str(parsed_data.group(2))
        report.attack = str(parsed_data.group(3))
        report.defence = str(parsed_data.group(4))
        report.level = int(parsed_data.group(5))
        if parsed_data.group(6):
            report.earned_exp = int(parsed_data.group(6))
        else:
            report.earned_exp = 0
        if parsed_data.group(7):
            report.earned_gold = int(parsed_data.group(7))
        else:
            report.earned_gold = 0
        if parsed_data.group(8):
            report.earned_stock = int(parsed_data.group(8))
        else:
            report.earned_stock = 0
        session.add(report)
        session.commit()
    return report


@user_allowed
def report_received(bot: Bot, update: Update, session):
    # if datetime.now() - update.message.forward_date > timedelta(minutes=1):
    #     send_async(bot, chat_id=update.message.chat.id, text=MSG_REPORT_OLD)
    # else:
    report = re.search(REPORT, update.message.text)
    user = session.query(User).filter_by(id=update.message.from_user.id).first()
    if report and user.character and str(report.group(2)) == user.character.name:
        time_from = datetime(update.message.forward_date.year, update.message.forward_date.month,
                             update.message.forward_date.day, int(update.message.forward_date.hour / 4) * 4, 0, 0)
        time_to = datetime(update.message.forward_date.year, update.message.forward_date.month,
                           update.message.forward_date.day + (1 if update.message.forward_date.hour >= 20 else 0),
                           int(update.message.forward_date.hour / 4 + 1) * 4 % 24, 0, 0)
        report = session.query(Report).filter(Report.date > time_from, Report.date < time_to,
                                              Report.user_id == update.message.from_user.id).all()
        if len(report) == 0:
            parse_reports(update.message.text, update.message.from_user.id, update.message.forward_date, session)
            send_async(bot, chat_id=update.message.from_user.id, text=MSG_REPORT_OK)
        else:
            send_async(bot, chat_id=update.message.from_user.id, text=MSG_REPORT_EXISTS)


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
        if CASTLE:
            if char and char.castle == CASTLE:
                send_async(bot, chat_id=update.message.chat.id, text=MSG_PROFILE_SAVED.format(char.name),
                           parse_mode=ParseMode.HTML)
            else:
                send_async(bot, chat_id=update.message.chat.id,
                           text=MSG_PROFILE_CASTLE_MISTAKE, parse_mode=ParseMode.HTML)
        else:
            send_async(bot, chat_id=update.message.chat.id, text=MSG_PROFILE_SAVED.format(char.name),
                       parse_mode=ParseMode.HTML)


@user_allowed
def char_show(bot: Bot, update: Update, session):
    if update.message.chat.type == 'private':
        user = session.query(User).filter_by(id=update.message.from_user.id).first()
        if user is not None and user.character is not None:
            char = user.character
            if CASTLE:
                if char.castle == CASTLE:
                    text = fill_char_template(MSG_PROFILE_SHOW_FORMAT, user, char)
                    btns = generate_profile_buttons(user)
                    send_async(bot, chat_id=update.message.chat.id, text=text, reply_markup=btns)
            else:
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
                send_async(bot, chat_id=update.message.chat.id, text=MSG_PROFILE_NOT_FOUND, parse_mode=ParseMode.HTML)
