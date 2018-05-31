# -*- coding: utf-8 -*-
import json
import logging
from datetime import datetime, timedelta

from sqlalchemy import func, tuple_, and_
from sqlalchemy.exc import SQLAlchemyError
from telegram import (
    Bot, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
)
from telegram.error import TelegramError
from telegram.ext import Job
from telegram.ext.dispatcher import run_async

from config import GOVERNMENT_CHAT, CASTLE
from core.constants import DAYS_PROFILE_REMIND, DAYS_OLD_PROFILE_KICK
from core.functions.common import (
    StockType,
    stock_compare_text, MSG_CHANGES_SINCE_LAST_UPDATE, MSG_LAST_UPDATE, MSG_USER_BATTLE_REPORT,
    MSG_USER_BATTLE_REPORT_PRELIM, MSG_USER_BATTLE_REPORT_STOCK, stock_split,
    get_weighted_diff)
from core.functions.inline_keyboard_handling import (
    send_order
)
from core.functions.inline_markup import QueryType
from core.functions.profile import get_latest_report
from core.texts import (
    MSG_MAIN_INLINE_BATTLE,
    MSG_REPORT_SUMMARY, MSG_REPORT_TOTAL, MSG_REPORT_SUMMARY_RATING, MSG_UPDATE_PROFILE,
    MSG_SQUAD_DELETE_OUTDATED,
    MSG_SQUAD_DELETE_OUTDATED_EXT)
from core.types import Session, Order, Squad, Admin, Character, Report, SquadMember, User, Stock
from core.utils import send_async
from cwmq import Publisher


@run_async
def ready_to_battle(bot: Bot, job_queue: Job):
    session = Session()
    try:
        group = session.query(Squad).all()
        for item in group:
            if not item.reminders_enabled:
                continue

            new_order = Order()
            new_order.text = job_queue.context
            new_order.chat_id = item.chat_id
            new_order.date = datetime.now()
            new_order.confirmed_msg = 0
            session.add(new_order)
            session.commit()

            callback_data = json.dumps(
                {'t': QueryType.OrderOk.value, 'id': new_order.id})
            markup = InlineKeyboardMarkup([
                [InlineKeyboardButton(MSG_MAIN_INLINE_BATTLE,
                                      callback_data=callback_data)]])

            msg = send_order(bot, new_order.text, 0, new_order.chat_id, markup=None)

            try:
                msg = msg.result().result()
                if msg:
                    bot.request.post(bot.base_url + '/pinChatMessage',
                                     {'chat_id': new_order.chat_id,
                                      'message_id': msg.message_id,
                                      'disable_notification': False})

            except TelegramError as err:
                bot.logger.error(err.message)

    except SQLAlchemyError as err:
        bot.logger.error(str(err))
        Session.rollback()


@run_async
def ready_to_battle_result(bot: Bot, job_queue: Job):
    if not GOVERNMENT_CHAT:
        return

    global_def = 0
    global_atk = 0
    global_exp = 0
    global_gold = 0
    global_stock = 0
    global_reports = 0
    global_members = 0

    real_def = 0
    real_atk = 0
    players_atk = 0
    players_def = 0
    session = Session()
    try:
        squads = session.query(Squad).all()
        text = MSG_REPORT_SUMMARY_RATING
        now = datetime.now()
        if (now.hour < 7):
            now = now - timedelta(days=1)
        time_from = now.replace(hour=(int((now.hour + 1) / 8) * 8 - 1 + 24) % 24, minute=0, second=0)
        text = MSG_REPORT_SUMMARY_RATING.format(time_from.strftime('%d-%m-%Y %H:%M'))
        for squad in squads:
            reports = session.query(User, Report) \
                .join(SquadMember) \
                .outerjoin(Report, and_(User.id == Report.user_id, Report.date > time_from)) \
                .filter(SquadMember.squad_id == squad.chat_id).order_by(Report.date.desc()).all()
            full_def = 0
            full_atk = 0
            full_exp = 0
            full_gold = 0
            full_stock = 0
            total_reports = 0
            total_members = 0

            for user, report in reports:
                total_members += 1
                if report:
                    full_atk += report.attack
                    full_def += report.defence
                    full_exp += report.earned_exp
                    full_gold += report.earned_gold
                    full_stock += report.earned_stock

                    real_atk += report.attack if report.earned_stock > 0 else 0
                    real_def += report.defence if report.earned_exp > 0 and report.earned_stock == 0 else 0

                    players_atk += 1 if report.earned_stock > 0 else 0
                    players_def += 1 if report.earned_exp > 0 and report.earned_stock == 0 else 0
                    total_reports += 1
            global_def += full_def
            global_atk += full_atk
            global_exp += full_exp
            global_stock += full_stock
            global_gold += full_gold
            global_members += total_members
            global_reports += total_reports
            if total_members > 0:
                text += MSG_REPORT_SUMMARY.format(squad.squad_name, total_reports, total_members, full_atk, full_def,
                                                  full_exp, full_gold, full_stock)
        text += MSG_REPORT_SUMMARY.format('TOTAL', global_reports, global_members, global_atk, global_def, global_exp,
                                          global_gold, global_stock)
        text += MSG_REPORT_TOTAL.format(players_atk, players_def, real_atk, real_def)
        send_async(bot, chat_id=GOVERNMENT_CHAT, text=text, parse_mode=ParseMode.HTML, reply_markup=None)

    except SQLAlchemyError as err:
        bot.logger.error(str(err))
        Session.rollback()


@run_async
def fresh_profiles(bot: Bot, job_queue: Job):
    session = Session()
    try:
        actual_profiles = session.query(Character.user_id, func.max(Character.date)). \
            group_by(Character.user_id)
        actual_profiles = actual_profiles.all()
        characters = session.query(Character).filter(tuple_(Character.user_id, Character.date)
                                                     .in_([(a[0], a[1]) for a in actual_profiles]),
                                                     datetime.now() - timedelta(
                                                         days=DAYS_PROFILE_REMIND) > Character.date,
                                                     Character.date > datetime.now() - timedelta(
                                                         days=DAYS_OLD_PROFILE_KICK))
        if CASTLE:
            characters = characters.filter_by(castle=CASTLE)
        characters = characters.all()
        for character in characters:
            send_async(bot,
                       chat_id=character.user_id,
                       text=MSG_UPDATE_PROFILE,
                       parse_mode=ParseMode.HTML)
        characters = session.query(Character).filter(tuple_(Character.user_id, Character.date)
                                                     .in_([(a[0], a[1]) for a in actual_profiles]),
                                                     Character.date < datetime.now() - timedelta(
                                                         days=DAYS_OLD_PROFILE_KICK)).all()
        members = session.query(SquadMember, User).filter(SquadMember.user_id
                                                          .in_([character.user_id for character in characters])) \
            .join(User, User.id == SquadMember.user_id).all()
        for member, user in members:
            session.delete(member)
            admins = session.query(Admin).filter_by(admin_group=member.squad_id).all()
            try:
                bot.restrictChatMember(member.squad_id, member.user_id)
                bot.kick_chat_member(member.squad_id, member.user_id)
            except TelegramError as err:
                bot.logger.error(err.message)

            for adm in admins:
                send_async(bot, chat_id=adm.user_id,
                           text=MSG_SQUAD_DELETE_OUTDATED_EXT
                           .format(member.user.character.name, member.user.username, member.squad.squad_name),
                           parse_mode=ParseMode.HTML)
            send_async(bot, chat_id=member.squad_id,
                       text=MSG_SQUAD_DELETE_OUTDATED_EXT.format(member.user.character.name, member.user.username,
                                                                 member.squad.squad_name),
                       parse_mode=ParseMode.HTML)
            send_async(bot,
                       chat_id=member.user_id,
                       text=MSG_SQUAD_DELETE_OUTDATED,
                       parse_mode=ParseMode.HTML)
        session.commit()
    except SQLAlchemyError as err:
        bot.logger.error(str(err))
        Session.rollback()


@run_async
def refresh_api_users(bot: Bot, job_queue: Job):
    logging.info("API REFRESH type %s")
    session = Session()
    try:
        p = Publisher()
        api_users = session.query(User).filter(User.api_token is not None)
        for user in api_users:
            logging.info("Updating data for %s", user.id)
            if user.is_api_profile_allowed:
                p.publish({
                    "token": user.api_token,
                    "action": "requestProfile"
                })
            if user.is_api_stock_allowed:
                p.publish({
                    "token": user.api_token,
                    "action": "requestStock"
                })
    except SQLAlchemyError as err:
        bot.logger.error(str(err))
        Session.rollback()


@run_async
def report_after_battle(bot: Bot, job_queue: Job):
    logging.info("API REFRESH type %s")
    session = Session()
    try:
        api_users = session.query(User).filter(User.api_token is not None)
        for user in api_users:
            logging.info("Updating data for %s", user.id)

            text = MSG_USER_BATTLE_REPORT
            # We must have the actual access rights and user has to be in a testing squad to allow onboarding of this
            # feature!
            onboarding_squad_member = False
            if user and user.member and user.member.approved and user.member.squad and user.member.squad.testing_squad:
                onboarding_squad_member = True

            if user.is_api_profile_allowed and user.is_api_stock_allowed and \
                user.setting_automated_report and user.api_token and \
                onboarding_squad_member:

                prev_character = session.query(Character).filter_by(
                    user_id=user.id,
                ).order_by(Character.date.desc()).limit(1).offset(1).first()

                earned_exp = user.character.exp - prev_character.exp
                earned_gold = user.character.gold - prev_character.gold

                # Get the newest stock-report from before war for this comparison...
                filter_latest = datetime.now().replace(minute=0, second=0, microsecond=0)
                filter_cutoff = filter_latest - timedelta(minutes=30)

                second_newest = session.query(Stock).filter(
                    Stock.user_id == user.id,
                    Stock.stock_type == StockType.Stock.value,
                    Stock.date < filter_latest,
                    Stock.date > filter_cutoff
                ).order_by(Stock.date.desc()).first()

                stock_diff = "<i>Missing before/after war data to generate comparison. Sorry.</i>"
                gained_sum = 0
                lost_sum = 0
                diff_stock = 0
                if second_newest and user.stock.date >= filter_latest:
                    resources_new, resources_old = stock_split(second_newest.stock, user.stock.stock)
                    resource_diff_add, resource_diff_del = get_weighted_diff(resources_old, resources_new)
                    stock_diff = stock_compare_text(second_newest.stock, user.stock.stock)

                    gained_sum = sum([x[1] for x in resource_diff_add])
                    lost_sum = sum([x[1] for x in resource_diff_del])
                    diff_stock = gained_sum + lost_sum

                # Only create a preliminary report if user hasn't already sent in a complete one.
                existing_report = get_latest_report(session, user.id)
                if not existing_report:
                    r = Report()
                    r.user = user
                    r.name = user.character.name
                    r.date = datetime.now()
                    r.level = user.character.level
                    r.attack = user.character.attack
                    r.defence = user.character.defence
                    r.castle = user.character.castle
                    r.earned_exp = earned_exp
                    r.earned_gold = earned_gold
                    r.earned_stock = diff_stock
                    r.preliminary_report = True
                    session.add(r)
                    session.commit()

                # Text with prelim. battle report
                """text += MSG_USER_BATTLE_REPORT_PRELIM.format(
                    user.character.castle, user.character.name, user.character.attack, user.character.defence,
                    user.character.level, earned_exp, earned_gold, diff_stock
                )"""

                text += MSG_USER_BATTLE_REPORT_PRELIM.format(
                    user.character.castle, user.character.name, user.character.level
                )

                stock_text = MSG_USER_BATTLE_REPORT_STOCK.format(
                    MSG_CHANGES_SINCE_LAST_UPDATE,
                    stock_diff,
                    MSG_LAST_UPDATE,
                    user.stock.date.strftime("%Y-%m-%d %H:%M:%S")
                )
                text += stock_text

                send_async(bot,
                           chat_id=user.id,
                           text=text,
                           parse_mode=ParseMode.HTML,
                           reply_markup=None
                           )

    except SQLAlchemyError as err:
        bot.logger.error(str(err))
        Session.rollback()