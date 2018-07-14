import logging
import re
from datetime import datetime, timedelta
from enum import Enum

from sqlalchemy import collate
from telegram import ParseMode, Update, InlineKeyboardButton, InlineKeyboardMarkup

from config import CASTLE
from core.bot import MQBot
from core.enums import CASTLE_MAP
from core.handler.callback import CallbackAction
from core.handler.callback.util import create_callback
from core.regexp import BUILD_REPORT, HERO, PROFESSION, REPAIR_REPORT, REPORT
from core.state import get_last_battle
from core.template import fill_char_template
from core.texts import *
from core.texts import BTN_HERO, BTN_STOCK, BTN_EQUIPMENT, BTN_SKILL
from core.types import (BuildReport, Character, Equip, Item, Profession,
                        Report, Session, Stock, User, new_item)
from core.utils import send_async
from functions.common import StockType, __ban_traitor, __get_item_worth


class BuildType(Enum):
    Build = 1
    Repair = 0


def parse_hero_text(report_text):
    if not report_text:
        return None

    parsed = re.search(HERO, report_text, flags=re.UNICODE)
    if not parsed:
        return None

    return {
        'castle': parsed.group("castle"),
        'castle_name': CASTLE_MAP[parsed.group("castle")],
        'name_standalone': parsed.group("name"),
        'name': "{}{}".format(
            "{}".format(parsed.group("guild")) if parsed.group("guild") else "",
            parsed.group("name"),
        ),
        'ribbon': parsed.group("ribbon") if parsed.group("ribbon") else None,
        'guild': parsed.group("guild"),
        'attack': int(parsed.group("attack")) if parsed.group("attack") else 0,
        'defence': int(parsed.group("defence")) if parsed.group("defence") else 0,
        'level': int(parsed.group("level")) if parsed.group("level") else 0,
        'exp': int(parsed.group("exp")) if parsed.group("exp") else 0,
        'gold': int(parsed.group("gold")) if parsed.group("gold") else 0,
        'mana': int(parsed.group("mana")) if parsed.group("mana") else 0,
        'stamina': int(parsed.group("stamina")) if parsed.group("stamina") else 0,
        'max_stamina': int(parsed.group("max_stamina")) if parsed.group("max_stamina") else 0,
        'pouches': int(parsed.group("pouches")) if parsed.group("pouches") else 0,
        'exp_needed': int(parsed.group("exp_needed")) if parsed.group("exp_needed") else 0,
        'expertise': parsed.group("expertise") if parsed.group("expertise") else None,
        'pvp': parsed.group("pvp") if parsed.group("expertise") else None,
        'diamonds': int(parsed.group("diamonds")) if parsed.group("diamonds") else 0,
        'equipment': parsed.group(23)
    }

    # TODO: Should boosted def/atk be used?


def parse_hero(bot: MQBot, profile, user_id, date):
    """ Parse a forwarded hero """
    logging.info("parse_hero for user_id='%s'", user_id)
    char = Session.query(Character).filter_by(user_id=user_id, date=date).first()
    if char is None:
        parsed_data = parse_hero_text(profile)

        char = Character()
        char.user_id = user_id
        char.date = date
        char.castle = parsed_data['castle']
        char.name = parsed_data['name']
        char.prof = parsed_data['castle_name']
        char.level = parsed_data['level']
        char.attack = parsed_data['attack']
        char.defence = parsed_data['defence']
        char.exp = parsed_data['exp']
        char.needExp = parsed_data['exp_needed']
        char.maxStamina = parsed_data['max_stamina']
        char.gold = parsed_data['gold']
        char.donateGold = parsed_data['pouches']

        # We don't get this fom forwarded text. So get it from the last one sent in to make sure its set.
        last_with_class = Session.query(Character).filter(
            Character.user_id == user_id,
            Character.characterClass is not None
        ).order_by(Character.date).first()
        if last_with_class:
            char.characterClass = last_with_class.characterClass

        # if parsed_data.group(21):
        #    char.pet = str(parsed_data.group(21))
        #    char.petLevel = int(parsed_data.group(23))
        if parsed_data['equipment']:
            equip = Equip()
            equip.user_id = user_id
            equip.date = date
            equip.equip = parsed_data['equipment']
            Session.add(equip)

        Session.add(char)
        if char.castle == CASTLE:
            Session.commit()
        else:
            Session.rollback()
            __ban_traitor(bot, user_id)
            logging.warning('%s is a traitor!', user_id)
    return char


def parse_report_text(report_text):
    if not report_text:
        return None

    parsed = re.search(REPORT, report_text, flags=re.UNICODE)
    if not parsed:
        return None

    # TODO: Should boosted def/atk be used?
    return {
        'castle': parsed.group("castle"),
        'name_standalone': parsed.group("name"),
        'name': "{}{}".format(
            parsed.group("guild") if parsed.group("guild") else "",
            parsed.group("name"),
        ),
        'ribbon': parsed.group("ribbon") if parsed.group("ribbon") else None,
        'guild': parsed.group("guild"),
        'attack': int(parsed.group("attack")) if parsed.group("attack") else 0,
        'defence': int(parsed.group("defence")) if parsed.group("defence") else 0,
        'level': int(parsed.group("level")) if parsed.group("level") else 0,
        'exp': int(parsed.group("exp")) if parsed.group("exp") else 0,
        'gold': int(parsed.group("gold")) if parsed.group("gold") else 0,
        'stock': int(parsed.group("stock")) if parsed.group("stock") else 0,
    }


def save_report(report_text, user_id, date):
    logging.info("Report: report_text='%s', user_id='%s', date='%s'", report_text, user_id, date)
    existing_report = get_latest_report(user_id)
    # New one or update to preliminary
    report = None
    if not existing_report or (existing_report and existing_report.preliminary_report):
        parsed_data = parse_report_text(report_text)
        if not existing_report:
            # New one
            report = Report()
        else:
            report = existing_report

        report.user_id = user_id
        report.date = date
        report.castle = parsed_data['castle']
        report.name = parsed_data['name']
        report.attack = parsed_data['attack']
        report.defence = parsed_data['defence']
        report.preliminary_report = False
        report.level = parsed_data['level']
        report.earned_exp = parsed_data['exp']
        report.earned_gold = parsed_data['gold']
        report.earned_stock = parsed_data['stock']

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
        skill_list = ""
        for string in strings[2:]:
            skill_list += string.split("/")[0] + "\n"
        profession.skillList = skill_list
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


def __send_user_with_settings(bot: MQBot, update: Update, show_user: User, admin_user: User):
    if show_user and show_user.character:
        char = show_user.character
        profession = show_user.profession
        text = fill_char_template(MSG_PROFILE_SHOW_FORMAT, show_user, char, profession)
        text += MSG_PROFILE_ADMIN_INFO_ADDON.format(
            bool(show_user.is_banned),
            bool(show_user.api_token),
            bool(show_user.api_user_id),
            bool(show_user.is_api_profile_allowed),
            bool(show_user.is_api_stock_allowed),
            bool(show_user.is_api_trade_allowed),
            bool(show_user.setting_automated_report),
            bool(show_user.setting_automated_deal_report),
            bool(show_user.setting_automated_hiding),
            bool(show_user.setting_automated_sniping),
            "Temp. Suspended" if show_user.sniping_suspended else ""
        )
        btns = __get_keyboard_profile(admin_user, show_user)
        send_async(
            bot,
            chat_id=update.message.chat.id,
            text=text,
            reply_markup=btns,
            parse_mode=ParseMode.HTML
        )
    else:
        send_async(bot, chat_id=update.message.chat.id, text=MSG_PROFILE_NOT_FOUND, parse_mode=ParseMode.HTML)


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
    if now.hour < 7:
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

    return before_battle, after_battle


def annotate_stock_with_price(bot: MQBot, stock: str):
    stock_text = ""
    overall_worth = 0
    for line in stock.splitlines():
        find = re.search(r"(?P<item>.+)(?: \((?P<count>[0-9]+)\))", line)
        if find:
            db_item = Session.query(Item).filter(
                Item.name == collate(find.group("item"), 'utf8mb4_unicode_520_ci')
            ).first()
            if not db_item:
                new_item(find.group("item"), False)
                stock_text += "{}\n".format(line)
            elif db_item and not db_item.tradable:
                stock_text += "{}\n".format(line)
            else:
                lowest_price = __get_item_worth(find.group("item"))
                if lowest_price:
                    count = int(find.group("count"))
                    item_overall = (count * lowest_price)
                    overall_worth += item_overall
                    stock_text += MSG_STOCK_PRICE.format(
                        find.group("item"),
                        count,
                        lowest_price,
                        item_overall,
                    )
                else:
                    stock_text += "{} ({})\n".format(find.group("item"), find.group("count"))
        else:
            stock_text += "{}\n".format(line)

    stock_text += MSG_STOCK_OVERALL_PRICE.format(overall_worth)

    return stock_text


def __get_keyboard_profile(user: User, for_user: User, back_button=None):
    inline_keys = [
        [
            InlineKeyboardButton(
                BTN_HERO,
                callback_data=create_callback(
                    CallbackAction.HERO,
                    user.id,
                    profile_id=for_user.id,
                    back_button=back_button
                )
            )
        ]
    ]
    if for_user.stock:
        inline_keys.append([
            InlineKeyboardButton(
                BTN_STOCK,
                callback_data=create_callback(
                    CallbackAction.HERO_STOCK,
                    user.id,
                    profile_id=for_user.id,
                    back_button=back_button
                )
            )
        ])
    if for_user.equip:
        inline_keys.append([
            InlineKeyboardButton(
                BTN_EQUIPMENT,
                callback_data=create_callback(
                    CallbackAction.HERO_EQUIP,
                    user.id,
                    profile_id=for_user.id,
                    back_button=back_button
                )
            )
        ])
    if for_user.profession:
        inline_keys.append([
            InlineKeyboardButton(
                BTN_SKILL,
                callback_data=create_callback(
                    CallbackAction.HERO_SKILL,
                    user.id,
                    profile_id=for_user.id,
                    back_button=back_button
                )
            )
        ])
    if back_button:
        inline_keys.append([
            back_button
        ])

    return InlineKeyboardMarkup(inline_keys)
