import logging
import re
from datetime import datetime, timedelta
from enum import Enum

from telegram import Bot, Update, ParseMode

from config import CASTLE
from core.functions.common import StockType
from core.functions.inline_markup import generate_profile_buttons, generate_settings_buttons
from core.regexp import PROFILE, HERO, REPORT, PROFESSION, BUILD_REPORT, REPAIR_REPORT
from core.state import get_last_battle
from core.template import fill_char_template
from core.texts import MSG_PROFILE_SHOW_FORMAT, MSG_PROFILE_ADMIN_INFO_ADDON, MSG_PROFILE_NOT_FOUND, \
    MSG_NEEDS_API_ACCESS, MSG_NEEDS_TRADE_ACCESS, MSG_SETTINGS_INFO, MSG_USER_BATTLE_REPORT_PRELIM, \
    MSG_USER_BATTLE_REPORT_HEADER, MSG_USER_BATTLE_REPORT, MSG_USER_BATTLE_REPORT_FULL
from core.types import Session, Character, Equip, Report, Profession, BuildReport, User, Stock
from core.utils import send_async

class BuildType(Enum):
    Build = 1
    Repair = 0


def parse_profile(profile, user_id, date):
    parsed_data = re.search(PROFILE, profile)
    char = Session.query(Character).filter_by(user_id=user_id, date=date).first()
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
        Session.add(char)
        if char.castle == CASTLE:
            Session.commit()
        else:
            logging.warning('%s is a traitor!', user_id)
    return char


def parse_hero(profile, user_id, date):
    parsed_data = re.search(HERO, profile)
    char = Session.query(Character).filter_by(user_id=user_id, date=date).first()
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
        char.gold = int(parsed_data.group(11))  # + int(parsed_data.group(12)) if parsed_data.group(12) else 0
        char.donateGold = int(parsed_data.group(12)) if parsed_data.group(12) else 0
        if parsed_data.group(21):
            char.pet = str(parsed_data.group(21))
            char.petLevel = int(parsed_data.group(23))
        if parsed_data.group(17):
            equip = Equip()
            equip.user_id = user_id
            equip.date = date
            equip.equip = str(parsed_data.group(18))
            Session.add(equip)
        Session.add(char)
        if char.castle == CASTLE:
            Session.commit()
        else:
            logging.warning('%s is a traitor!', user_id)
    return char


def parse_reports(report_text, user_id, date):
    parsed_data = re.search(REPORT, report_text)
    logging.info("Report: report_text='%s', user_id='%s', date='%s'", report_text, user_id, date)
    existing_report = get_latest_report(user_id)
    # New one or update to preliminary
    report = None
    if not existing_report or (existing_report and existing_report.preliminary_report):
        if not existing_report:
            # New one
            report = Report()
        else:
            report = existing_report

        report.user_id = user_id
        report.date = date
        report.castle = str(parsed_data.group(1))
        report.name = str(parsed_data.group(2))
        report.attack = int(parsed_data.group(3))  # + int(parsed_data.group(4) if parsed_data.group(4) else 0)
        report.defence = int(parsed_data.group(6))  # + int(parsed_data.group(7) if parsed_data.group(7) else 0)
        report.preliminary_report = False
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
            Session.add(report)
            Session.commit()
        else:
            logging.warning('%s is a traitor!', user_id)

    return report


def parse_profession(prof, user_id, date):
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
        Session.add(profession)
        Session.commit()
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


def parse_build_reports(report, user_id, date):
    parsed_data = re.search(BUILD_REPORT, report)
    report = Session.query(BuildReport).filter_by(user_id=user_id, date=date).first()
    if report is None:
        report = BuildReport()
        report.user_id = user_id
        report.date = date
        report.building = str(parsed_data.group(1))
        report.progress_percent = str(parsed_data.group(2))
        report.report_type = BuildType.Build.value
        Session.add(report)
        Session.commit()
    return report


def parse_repair_reports(report, user_id, date):
    parsed_data = re.search(REPAIR_REPORT, report)
    report = Session.query(BuildReport).filter_by(user_id=user_id, date=date).first()
    if report is None:
        report = BuildReport()
        report.user_id = user_id
        report.date = date
        report.building = str(parsed_data.group(1))
        report.report_type = BuildType.Repair.value
        Session.add(report)
        Session.commit()
    return report


def __send_user_with_settings(bot: Bot, update: Update, user: User):
    if user and user.character:
        char = user.character
        profession = user.profession
        text = fill_char_template(MSG_PROFILE_SHOW_FORMAT, user, char, profession)
        text += MSG_PROFILE_ADMIN_INFO_ADDON.format(
            bool(user.is_banned),
            bool(user.api_token),
            bool(user.api_user_id),
            bool(user.is_api_profile_allowed),
            bool(user.is_api_stock_allowed),
            bool(user.is_api_trade_allowed),
            bool(user.setting_automated_report),
            bool(user.setting_automated_deal_report),
            bool(user.setting_automated_hiding),
            bool(user.setting_automated_sniping),
            "Temp. Suspended" if user.sniping_suspended else ""
        )
        btns = generate_profile_buttons(user)
        send_async(
            bot,
            chat_id=update.message.chat.id,
            text=text,
            reply_markup=btns,
            parse_mode=ParseMode.HTML
        )
    else:
        send_async(bot, chat_id=update.message.chat.id, text=MSG_PROFILE_NOT_FOUND, parse_mode=ParseMode.HTML)


def send_settings(bot, update, user):
    automated_report = MSG_NEEDS_API_ACCESS
    if user.setting_automated_report and user.api_token and user.is_api_profile_allowed:
        automated_report = user.setting_automated_deal_report

    automated_deal_report = MSG_NEEDS_API_ACCESS
    if user.setting_automated_deal_report and user.api_token and user.is_api_stock_allowed:
        automated_deal_report = user.setting_automated_deal_report

    automated_sniping = MSG_NEEDS_TRADE_ACCESS
    if user.setting_automated_sniping and user.api_token and user.is_api_trade_allowed:
        automated_deal_report = user.setting_automated_deal_report

    automated_hiding = MSG_NEEDS_TRADE_ACCESS
    if user.setting_automated_sniping and user.api_token and user.is_api_trade_allowed:
        automated_hiding = user.setting_automated_hiding

    msg = MSG_SETTINGS_INFO.format(
        automated_report,
        automated_deal_report,
        automated_sniping,
        automated_hiding,
        user.stock.date if user.stock else "Unknown",
        user.character.date if user.character else "Unknown",
    )

    if update.callback_query:
        bot.editMessageText(
            text=msg,
            chat_id=user.id,
            message_id=update.callback_query.message.message_id,
            reply_markup=generate_settings_buttons(user),
            parse_mode=ParseMode.HTML
        )
    else:
        bot.send_message(
            text=msg,
            chat_id=user.id,
            reply_markup=generate_settings_buttons(user),
            parse_mode=ParseMode.HTML
        )

def format_report(report: Report) -> str:
    """ Return a formatted battle report. """

    if report.preliminary_report:
        text = MSG_USER_BATTLE_REPORT_HEADER
        text += MSG_USER_BATTLE_REPORT_PRELIM.format(
            report.castle,
            report.name,
            report.level,
        )
    else:
        text = MSG_USER_BATTLE_REPORT_FULL
        text += MSG_USER_BATTLE_REPORT.format(
            report.castle,
            report.name,
            report.attack,
            report.defence,
            report.level,
            report.earned_exp,
            report.earned_gold,
            report.earned_stock
        )

    return text

# TODO: Review. Can't this be moved directly into User class and a getter?
def get_latest_report(user_id) -> Report:
    logging.debug("get_latest_report for '%s'", user_id)
    now = datetime.now()
    if (now.hour < 7):
        now = now - timedelta(days=1)
    time_from = now.replace(hour=(int((now.hour + 1) / 8) * 8 - 1 + 24) % 24, minute=0, second=0, microsecond=0)
    existing_report = Session.query(Report).filter(Report.user_id == user_id, Report.date > time_from).first()

    return existing_report

def get_stock_before_after_war(user: User) -> tuple:
    """ Return the latest stock from before battle and the oldest after battle for comparison """

    last_battle = get_last_battle()

    before_battle = Session.query(Stock).filter(
        Stock.user_id == user.id,
        Stock.stock_type == StockType.Stock.value,
        Stock.date < last_battle
    ).order_by(Stock.date.desc()).first()

    after_battle = Session.query(Stock).filter(
        Stock.user_id == user.id,
        Stock.stock_type == StockType.Stock.value,
        Stock.date > last_battle
    ).order_by(Stock.date.asc()).first()

    return (before_battle, after_battle)
