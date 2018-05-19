import re

from datetime import timedelta, datetime
from enum import Enum

from telegram import Update, Bot, ParseMode

from config import CASTLE, EXT_ID
from core.functions.ban import ban_traitor
from core.functions.inline_keyboard_handling import generate_profile_buttons
from core.regexp import HERO, PROFILE, REPORT, BUILD_REPORT, REPAIR_REPORT, PROFESSION, ACCESS_CODE
from core.template import fill_char_template
from core.texts import *
from core.types import Character, Report, User, admin_allowed, Equip, user_allowed, BuildReport, Profession
from core.utils import send_async
from cwmq import Publisher


class BuildType(Enum):
    Build = 1
    Repair = 0

# Get the Publisher Singleton
p = Publisher()

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
        if char.castle == CASTLE:
            session.commit()
        else:
            print('Traitor')
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
        char.gold = int(parsed_data.group(11)) #+ int(parsed_data.group(12)) if parsed_data.group(12) else 0
        char.donateGold = int(parsed_data.group(12)) if parsed_data.group(12) else 0
        if parsed_data.group(21):
            char.pet = str(parsed_data.group(21))
            char.petLevel = int(parsed_data.group(23))
        if parsed_data.group(17):
            equip = Equip()
            equip.user_id = user_id
            equip.date = date
            equip.equip = str(parsed_data.group(18))
            session.add(equip)
        session.add(char)
        if char.castle == CASTLE:
            session.commit()
        else:
            print('Traitor')
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
        report.attack = int(parsed_data.group(3))  #+ int(parsed_data.group(4) if parsed_data.group(4) else 0)
        report.defence = int(parsed_data.group(6))  #+ int(parsed_data.group(7) if parsed_data.group(7) else 0)
        report.level = int(parsed_data.group(9))
        if parsed_data.group(10):
            report.earned_exp = int(parsed_data.group(10))
        else:
            report.earned_exp = 0
        if parsed_data.group(11):
            report.earned_gold = int(parsed_data.group(11))
        else:
            report.earned_gold = 0
        if parsed_data.group(12):
            report.earned_stock = int(parsed_data.group(12))
        else:
            report.earned_stock = 0
        if report.castle == CASTLE:
            session.add(report)
            session.commit()
        else:
            print('Traitor')
    return report


def parse_profession(prof, user_id, date, session):
    parsed_data = re.search(PROFESSION, prof)
    profession = None
    if parsed_data is not None:
        profession = Profession()
        profession.user_id = user_id
        profession.date = date
        profession.name = str(parsed_data.group(1))
        strings = prof.splitlines()
        skillList = ""
        for string in strings[2:]:
            skillList += string.split("/")[0] + "\n"
        profession.skillList = skillList
        session.add(profession)
        session.commit()
    return profession

def get_required_xp(level):
    """ Get required XP for next level.
    Based on https://wiki.chatwars.me/index.php?title=%D0%93%D0%B5%D1%80%D0%BE%D0%B9"""

    # We need the XP for next level...
    level += 1

    required = {
        1: 0,
        2: 5,
        3: 15,
        4: 38,
        5: 79,
        6: 142,
        7: 227,
        8: 329,
        9: 444,
        10: 577,
        11: 721,
        12: 902,
        13: 1127,
        14: 1409,
        15: 1761,
        16: 2202,
        17: 2752,
        18: 3440,
        19: 4300,
        20: 5375,
        21: 6719,
        22: 8399,
        23: 10498,
        24: 13123,
        25: 16404,
        26: 20504,
        27: 25631,
        28: 32038,
        29: 39023,
        30: 46636,
        31: 54934,
        32: 63979,
        33: 73838,
        34: 84584,
        35: 96297,
        36: 109065,
        37: 122982,
        38: 138151,
        39: 154685,
        40: 172708,
        41: 192353,
        42: 213765,
        43: 237105,
        44: 262545,
        45: 290275,
        46: 320501,
        47: 353447,
        48: 389358,
        49: 428501,
        50: 471167,
        51: 517673,
        52: 568364,
        53: 623618,
        54: 683845,
        55: 749492,
        56: 821047,
        57: 899042,
        58: 984057,
        59: 1076723,
        60: 1177728,
        61: 1287825,
        62: 1407830,
        63: 1538636,
        64: 1681214,
        65: 1836624,
        66: 2006021,
    }
    return required[level]

def parse_build_reports(report, user_id, date, session):
    parsed_data = re.search(BUILD_REPORT, report)
    report = session.query(BuildReport).filter_by(user_id=user_id, date=date).first()
    if report is None:
        report = BuildReport()
        report.user_id = user_id
        report.date = date
        report.building = str(parsed_data.group(1))
        report.progress_percent = str(parsed_data.group(2))
        report.report_type = BuildType.Build.value
        session.add(report)
        session.commit()
    return report


def parse_repair_reports(report, user_id, date, session):
    parsed_data = re.search(REPAIR_REPORT, report)
    report = session.query(BuildReport).filter_by(user_id=user_id, date=date).first()
    if report is None:
        report = BuildReport()
        report.user_id = user_id
        report.date = date
        report.building = str(parsed_data.group(1))
        report.report_type = BuildType.Repair.value
        session.add(report)
        session.commit()
    return report


@user_allowed(False)
def build_report_received(bot: Bot, update: Update, session):
    if datetime.now() - update.message.forward_date > timedelta(minutes=10):
        send_async(bot, chat_id=update.message.from_user.id, text=MSG_BUILD_REPORT_TOO_OLD)
        return
    report = re.search(BUILD_REPORT, update.message.text)
    user = session.query(User).filter_by(id=update.message.from_user.id).first()
    if report and user.character:
        old_report = session.query(BuildReport) \
            .filter(BuildReport.user_id == user.id,
                    BuildReport.date > update.message.forward_date - timedelta(minutes=5),
                    BuildReport.date < update.message.forward_date + timedelta(minutes=5)).first()
        if old_report is None:
            parse_build_reports(update.message.text, update.message.from_user.id, update.message.forward_date, session)
            user_builds = session.query(BuildReport).filter_by(user_id=user.id).count()
            send_async(bot, chat_id=update.message.from_user.id, text=MSG_BUILD_REPORT_OK.format(user_builds))
        else:
            send_async(bot, chat_id=update.message.from_user.id, text=MSG_BUILD_REPORT_EXISTS)


@user_allowed(False)
def repair_report_received(bot: Bot, update: Update, session):
    if datetime.now() - update.message.forward_date > timedelta(minutes=10):
        send_async(bot, chat_id=update.message.from_user.id, text=MSG_BUILD_REPORT_TOO_OLD)
        return
    report = re.search(REPAIR_REPORT, update.message.text)
    user = session.query(User).filter_by(id=update.message.from_user.id).first()
    if report and user.character:
        old_report = session.query(BuildReport) \
            .filter(BuildReport.user_id == user.id,
                    BuildReport.date > update.message.forward_date - timedelta(minutes=5),
                    BuildReport.date < update.message.forward_date + timedelta(minutes=5)).first()
        if old_report is None:
            parse_repair_reports(update.message.text, update.message.from_user.id, update.message.forward_date, session)
            user_builds = session.query(BuildReport).filter_by(user_id=user.id).count()
            send_async(bot, chat_id=update.message.from_user.id, text=MSG_BUILD_REPORT_OK.format(user_builds))
        else:
            send_async(bot, chat_id=update.message.from_user.id, text=MSG_BUILD_REPORT_EXISTS)


@user_allowed(False)
def report_received(bot: Bot, update: Update, session):
    if datetime.now() - update.message.forward_date > timedelta(minutes=1):
         send_async(bot, chat_id=update.message.chat.id, text=MSG_REPORT_OLD)
    else:
        report = re.search(REPORT, update.message.text)
        user = session.query(User).filter_by(id=update.message.from_user.id).first()
        if report and user.character and str(report.group(2)) == user.character.name:
            
            date= update.message.forward_date
            if (update.message.forward_date.hour < 7):
                date= update.message.forward_date - timedelta(days=1)
            
            time_from = date.replace(hour=(int((update.message.forward_date.hour+1) / 8) * 8 - 1 + 24) % 24, minute=0, second=0)
     
            date= update.message.forward_date
            if (update.message.forward_date.hour == 23):
                date= update.message.forward_date + timedelta(days=1)

            time_to = date.replace(hour=(int((update.message.forward_date.hour+1) / 8 + 1) * 8 - 1) % 24, minute=0, second=0)
            

            report = session.query(Report).filter(Report.date > time_from, Report.date < time_to,
                                                  Report.user_id == update.message.from_user.id).all()

            if len(report) > 0 and report[0].castle != CASTLE:
                ban_traitor(bot, session,update.message.from_user.id)

            if len(report) == 0:
                parse_reports(update.message.text, update.message.from_user.id, update.message.forward_date, session)
                send_async(bot, chat_id=update.message.from_user.id, text=MSG_REPORT_OK)
                if report and report.castle != CASTLE:
                    ban_traitor(bot, session,update.message.from_user.id)

            else:
                send_async(bot, chat_id=update.message.from_user.id, text=MSG_REPORT_EXISTS)


@user_allowed(False)
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
            if char and (char.castle == CASTLE or update.message.from_user.id == EXT_ID) :
                char.castle = CASTLE
                send_async(bot, chat_id=update.message.chat.id, text=MSG_PROFILE_SAVED.format(char.name),
                           parse_mode=ParseMode.HTML)
            else:
                send_async(bot, chat_id=update.message.chat.id,
                           text=MSG_PROFILE_CASTLE_MISTAKE, parse_mode=ParseMode.HTML)
        else:
            send_async(bot, chat_id=update.message.chat.id, text=MSG_PROFILE_SAVED.format(char.name),
                       parse_mode=ParseMode.HTML)
        if char and char.castle != CASTLE:
            ban_traitor(bot, session , update.message.from_user.id)

@user_allowed(False)
def profession_update(bot: Bot, update: Update, session):
    if update.message.date - update.message.forward_date > timedelta(minutes=1):
        send_async(bot, chat_id=update.message.chat.id, text=MSG_PROFILE_OLD)
    else:
        profession = None
        if re.search(PROFESSION, update.message.text):
            profession = parse_profession(update.message.text,
                              update.message.from_user.id,
                              update.message.forward_date,
                              session)
            if profession:
                send_async(bot, chat_id=update.message.chat.id, text=MSG_SKILLS_SAVED.format(profession.name),parse_mode=ParseMode.HTML)

@user_allowed
def char_show(bot: Bot, update: Update, session):
    if update.message.chat.type == 'private':
        user = session.query(User).filter_by(id=update.message.from_user.id).first()

        if user.is_api_profile_allowed:
            p.publish({
                "token": user.api_token,
                "action": "requestStock"
            })
            p.publish({
                "token": user.api_token,
                "action": "requestProfile"
            })

        if user is not None and user.character is not None:
            char = user.character
            profession = user.profession
            if CASTLE:
                if char.castle == CASTLE or user.id == EXT_ID :
                    char.castle = CASTLE
                    text = fill_char_template(MSG_PROFILE_SHOW_FORMAT, user, char, profession)
                    btns = generate_profile_buttons(user)
                    send_async(bot, chat_id=update.message.chat.id, text=text, reply_markup=btns, parse_mode=ParseMode.HTML)
            else:
                text = fill_char_template(MSG_PROFILE_SHOW_FORMAT, user, char, profession)
                btns = generate_profile_buttons(user)
                send_async(bot, chat_id=update.message.chat.id, text=text, reply_markup=btns, parse_mode=ParseMode.HTML)


@user_allowed()
def revoke(bot: Bot, update: Update, session):
    if update.message.chat.type == 'private':
        user = session.query(User).filter_by(id=update.message.from_user.id).first()
        user.api_token = None
        user.is_api_profile_allowed = False
        user.is_api_stock_allowed = False
        session.add(user)
        session.commit()

        btns = generate_profile_buttons(user)
        send_async(bot, chat_id=update.message.chat.id, text=MSG_API_ACCESS_RESET, reply_markup=btns, parse_mode=ParseMode.HTML)


@user_allowed
def grant_access(bot: Bot, update: Update, session):
    if update.message.chat.type == 'private':
        user = session.query(User).filter_by(id=update.message.from_user.id).first()

        reg_req = {
            "action": "createAuthCode",
            "payload": {
                "userId": update.message.chat.id
            }
        }
        p.publish(reg_req)
        send_async(bot, chat_id=update.message.chat.id, text=MSG_API_INFO, parse_mode=ParseMode.HTML)

@user_allowed
def handle_access_token(bot: Bot, update: Update, session):
    """ Handle a forwarded access code to authorize API access by bot.
    Note: We do not send back a confirmation at this point. User should be notified after async answer from APMQ
    TODO: Maybe add some kind of timeout if API is not availiable? """

    if update.message.chat.type == 'private':
        user = session.query(User).filter_by(id=update.message.from_user.id).first()
        # Extract token...
        code = re.search(ACCESS_CODE, update.message.text)
        if not code:
            send_async(bot, chat_id=update.message.chat.id, text=MSG_API_INVALID_CODE, parse_mode=ParseMode.HTML)
            return

        # For what is this code. Send the right response
        if user.api_request_id and user.api_grant_operation:
            add_grant_req = {
                "action": "grantAdditionalOperation",
                "token": user.api_token,
                "payload": {
                    "requestId": user.api_request_id,
                    "authCode": code.group(2),
                }
            }
            p.publish(add_grant_req)
        else:
            grant_req = {
                "action": "grantToken",
                "payload": {
                    "userId": update.message.chat.id,
                    "authCode": code.group(2),
                }
            }
            p.publish(grant_req)

@user_allowed
def settings(bot: Bot, update: Update, session):
    if update.message.chat.type == 'private':
        user = session.query(User).filter_by(id=update.message.from_user.id).first()

        text = "Automatic stock update: {}\nAutomatic profile update: {}".format(
            user.setting_automated_stock,
            user.setting_automated_profile,
        )

        send_async(bot, chat_id=update.message.chat.id, text=text, parse_mode=ParseMode.HTML)
        return


@admin_allowed()
def find_by_username(bot: Bot, update: Update, session):
    if update.message.chat.type == 'private':
        msg = update.message.text.split(' ', 1)[1]
        msg = msg.replace('@', '')
        if msg != '':
            user = session.query(User).filter_by(username=msg).first()
            if user is not None and user.character:
                char = user.character
                profession = user.profession
                text = fill_char_template(MSG_PROFILE_SHOW_FORMAT, user, char, profession)
                btns = generate_profile_buttons(user)
                send_async(bot, chat_id=update.message.chat.id, text=text, reply_markup=btns, parse_mode=ParseMode.HTML)
            else:
                send_async(bot, chat_id=update.message.chat.id, text=MSG_PROFILE_NOT_FOUND, parse_mode=ParseMode.HTML)
                
@admin_allowed()
def find_by_character(bot: Bot, update: Update, session):
    if update.message.chat.type == 'private':
        msg = update.message.text.split(' ', 1)[1]
        msg = msg.replace('@', '')
        if msg != '':
            char = session.query(Character).filter_by(name=msg).order_by(Character.date.desc()).first()
            if char is not None and char.user:
                user = char.user
                profession = user.profession
                text = fill_char_template(MSG_PROFILE_SHOW_FORMAT, user, char, profession)
                btns = generate_profile_buttons(user)
                send_async(bot, chat_id=update.message.chat.id, text=text, reply_markup=btns, parse_mode=ParseMode.HTML)
            else:
                send_async(bot, chat_id=update.message.chat.id, text=MSG_PROFILE_NOT_FOUND, parse_mode=ParseMode.HTML)

@admin_allowed()
def find_by_id(bot: Bot, update: Update, session):
    if update.message.chat.type == 'private':
        msg = update.message.text.split(' ', 1)[1]
        msg = msg.replace('@', '')
        if msg != '':
            user = session.query(User).filter_by(id=msg).first()
            if user is not None and user.character:
                char = user.character
                profession = user.profession
                text = fill_char_template(MSG_PROFILE_SHOW_FORMAT, user, char, profession)
                btns = generate_profile_buttons(user)
                send_async(bot, chat_id=update.message.chat.id, text=text, reply_markup=btns, parse_mode=ParseMode.HTML)
            else:
                send_async(bot, chat_id=update.message.chat.id, text=MSG_PROFILE_NOT_FOUND, parse_mode=ParseMode.HTML)
