# -*- coding: utf-8 -*-
import logging
from datetime import datetime, timedelta
from sqlalchemy import and_, func, tuple_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql.operators import collate
from telegram import ParseMode, Update
from telegram.error import TelegramError
from telegram.ext import Job
from telegram.ext.dispatcher import run_async
from typing import Optional

from config import (CASTLE, DAYS_OLD_PROFILE_KICK, DAYS_PROFILE_REMIND,
                    GOVERNMENT_CHAT)
from core.bot import MQBot
from core.utils import send_async
from core.decorators import command_handler
from core.state import get_last_battle
from core.texts import *
from core.db import Session
from core.enums import AdminType, MessageType
from core.model import Group, User, Admin, Order, Character, Report, Squad, SquadMember
from cwmq import Publisher
from functions.admin import __kickban_from_chat
from functions.common import (get_weighted_diff, stock_compare_text,
                              stock_split)
from functions.order import OrderDraft, __send_order
from functions.profile import (format_report, get_latest_report,
                               get_stock_before_after_war)

Session()


def ready_to_battle(bot: MQBot, job_queue: Job):
    try:
        group = Session.query(Group).filter(
            Group.reminders_enabled.is_(True),
            Group.bot_in_group.is_(True),
        ).all()
        for item in group:
            new_order = Order()
            new_order.text = job_queue.context
            new_order.chat_id = item.id
            new_order.date = datetime.now()
            new_order.confirmed_msg = 0
            Session.add(new_order)
            Session.commit()

            # Temporary object... TODO: Move this directly to DB?
            o = OrderDraft()
            o.pin = True
            o.order = new_order.text
            o.type = MessageType.TEXT
            o.button = False

            __send_order(
                bot=bot,
                order=o,
                chat_id=new_order.chat_id,
                markup=None
            )
    except SQLAlchemyError as err:
        logging.error(str(err))
        Session.rollback()


def after_battle(bot: MQBot, job_queue: Job):
    # This will only get send to groups without mini-report enabled. Mini-Report groups get the after battle
    # reminder sent after fwd....
    try:
        group = Session.query(Squad).filter(
            Group.reminders_enabled.is_(True),
            Group.fwd_minireport.is_(False),
            Group.bot_in_group.is_(True)
        ).join(Group).all()

        for item in group:
            new_order = Order()
            new_order.text = job_queue.context
            new_order.chat_id = item.chat_id
            new_order.date = datetime.now()
            new_order.confirmed_msg = 0
            Session.add(new_order)
            Session.commit()

            # Temporary object... TODO: Move this directly to DB?
            o = OrderDraft()
            o.pin = True
            o.order = new_order.text
            o.type = MessageType.TEXT
            o.button = False

            __send_order(
                bot=bot,
                order=o,
                chat_id=new_order.chat_id,
                markup=None
            )
    except SQLAlchemyError as err:
        bot.logger.error(str(err))
        Session.rollback()


@command_handler(
    min_permission=AdminType.FULL,
    allow_private=True
)
def call_ready_to_battle_result(bot: MQBot, update: Update, user: User):
    ready_to_battle_result(bot, None)


@run_async
def ready_to_battle_result(bot: MQBot, job_queue: Job):
    if not GOVERNMENT_CHAT:
        return
    logging.info("Generating ready_to_battle_result")

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
    try:
        squads = Session.query(Squad).all()
        now = datetime.now()
        if now.hour < 7:
            now = now - timedelta(days=1)
        time_from = now.replace(hour=(int((now.hour + 1) / 8) * 8 - 1 + 24) % 24, minute=0, second=0)
        text = MSG_REPORT_SUMMARY_RATING.format(time_from.strftime('%d-%m-%Y %H:%M'))
        for squad in squads:
            reports = Session.query(User, Report) \
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
                text += MSG_REPORT_SUMMARY.format(
                    squad.squad_name,
                    total_reports,
                    total_members,
                    full_atk,
                    full_def,
                    full_exp,
                    full_gold,
                    full_stock
                )
        text += MSG_REPORT_SUMMARY.format(
            'TOTAL',
            global_reports,
            global_members,
            global_atk,
            global_def,
            global_exp,
            global_gold,
            global_stock
        )
        text += MSG_REPORT_TOTAL.format(players_atk, players_def, real_atk, real_def)
        send_async(
            bot,
            chat_id=GOVERNMENT_CHAT,
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=None
        )

    except SQLAlchemyError as err:
        logging.error(str(err))
        Session.rollback()


@run_async
def fresh_profiles(bot: MQBot, job_queue: Job):
    try:
        actual_profiles = Session.query(Character.user_id, func.max(Character.date)).group_by(Character.user_id).all()

        characters = Session.query(Character).filter(
            tuple_(Character.user_id, Character.date).in_([(a[0], a[1]) for a in actual_profiles]),
            datetime.now() - timedelta(days=DAYS_PROFILE_REMIND) > Character.date,
            Character.date > datetime.now() - timedelta(days=DAYS_OLD_PROFILE_KICK),
            Character.castle == collate(CASTLE, 'utf8mb4_unicode_520_ci')
        )

        characters = characters.filter_by(castle=CASTLE)
        for character in characters:
            send_async(
                bot,
                chat_id=character.user_id,
                text=MSG_UPDATE_PROFILE,
                parse_mode=ParseMode.HTML
            )

        characters = Session.query(Character).filter(
            tuple_(Character.user_id, Character.date).in_([(a[0], a[1]) for a in actual_profiles]),
            Character.date < datetime.now() - timedelta(days=DAYS_OLD_PROFILE_KICK)
        ).all()

        members = Session.query(SquadMember, User).filter(
            SquadMember.user_id.in_([character.user_id for character in characters])
        ).join(User, User.id == SquadMember.user_id).all()

        for member, user in members:
            Session.delete(member)
            admins = Session.query(Admin).filter_by(group_id=member.squad_id).all()

            # Remove the inactive user from chat
            __kickban_from_chat(bot, member, member.squad.chat)

            for adm in admins:
                send_async(
                    bot,
                    chat_id=adm.user_id,
                    text=MSG_SQUAD_DELETE_OUTDATED_EXT.format(
                        member.user.character.name,
                        member.user.username,
                        member.squad.squad_name
                    ),
                    parse_mode=ParseMode.HTML
                )

            send_async(
                bot,
                chat_id=member.squad_id,
                text=MSG_SQUAD_DELETE_OUTDATED_EXT.format(
                    member.user.character.name,
                    member.user.username,
                    member.squad.squad_name
                ),
                parse_mode=ParseMode.HTML
            )
            send_async(
                bot,
                chat_id=member.user_id,
                text=MSG_SQUAD_DELETE_OUTDATED,
                parse_mode=ParseMode.HTML
            )
        Session.commit()
    except SQLAlchemyError as err:
        bot.logger.error(str(err))
        Session.rollback()


@run_async
def refresh_api_users(bot: MQBot, job_queue: Job):
    logging.info("Running refresh_api_users")
    try:
        p = Publisher()
        api_users = Session.query(User).filter(User.api_token is not None)
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


def create_user_report(user: User) -> Optional[str]:
    if user.is_api_profile_allowed and user.is_api_stock_allowed and user.api_token:

        logging.info("Processing report_after_battle for user_id='%s'", user.id)

        # Get the oldest stock-report from after war for this comparison...
        before_war_stock, after_war_stock = get_stock_before_after_war(user)
        logging.debug("after_war_stock: %s", after_war_stock)
        logging.debug("before_war_stock stock: %s", before_war_stock)

        # Get previous character and calculate difference in exp + gold
        prev_character = Session.query(Character).filter(
            Character.user_id == user.id,
            Character.date < get_last_battle(),
        ).order_by(Character.date.desc()).first()

        if not prev_character:
            logging.warning(
                "Couldn't find previous Character! This should only happen for a user with only ONE character.")
            return
        logging.debug("Previous character: %s", prev_character)

        earned_exp = user.character.exp - prev_character.exp
        earned_gold = user.character.gold - prev_character.gold

        stock_diff = "<i>Missing before/after war data to generate comparison. Sorry.</i>"
        gained_sum = 0
        lost_sum = 0
        diff_stock = 0
        if before_war_stock and after_war_stock:
            resources_new, resources_old = stock_split(before_war_stock.stock, after_war_stock.stock)
            resource_diff_add, resource_diff_del = get_weighted_diff(resources_old, resources_new)
            stock_diff = stock_compare_text(before_war_stock.stock, after_war_stock.stock)

            gained_sum = sum([x[1] for x in resource_diff_add])
            lost_sum = sum([x[1] for x in resource_diff_del])
            diff_stock = gained_sum + lost_sum

        # Only create a preliminary report if user hasn't already sent in a complete one.
        existing_report = get_latest_report(user.id)
        if not existing_report:
            logging.debug("Report does not exist yet. Creating preliminary Report.")
            r = Report()
            r.user_id = user.id

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
            Session.add(r)
            Session.commit()

            text = format_report(r)
        else:
            text = format_report(existing_report)

        stock_text = MSG_USER_BATTLE_REPORT_STOCK.format(
            MSG_CHANGES_SINCE_LAST_UPDATE,
            stock_diff,
            before_war_stock.date.strftime("%Y-%m-%d %H:%M:%S") if before_war_stock else "Missing",
            after_war_stock.date.strftime("%Y-%m-%d %H:%M:%S") if after_war_stock else "Missing",
        )
        text += stock_text
        if user.character and user.character.characterClass == "Knight":
            text += TRIBUTE_NOTE

        return text

    return


@run_async
def report_after_battle(bot: MQBot, job_queue: Job):
    logging.info("report_after_battle - Running")
    try:
        api_users = Session.query(User).join(SquadMember).join(Squad).join(Character).filter(
            User.api_token is not None,
            SquadMember.approved == True,
        ).all()
        for user in api_users:
            try:
                logging.info("report_after_battle for user_id='%s'", user.id)
                text = create_user_report(user)
                if text and user.setting_automated_report:
                    send_async(
                        bot,
                        chat_id=user.id,
                        text=text,
                        parse_mode=ParseMode.HTML
                    )
                logging.info("END report_after_battle for user_id='%s'", user.id)
            except Exception:
                try:
                    Session.rollback()
                except BaseException:
                    logging.exception("Can't do rollback")

                logging.exception("Exception in report_after_battle for user_id='%s'", user.id)

        logging.info("END report_after_battle")

    except SQLAlchemyError as err:
        logging.error(str(err))
        Session.rollback()
