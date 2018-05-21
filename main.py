# -*- coding: utf-8 -*-

import json
import logging
import re
from datetime import datetime, time, timedelta

from sqlalchemy import func, tuple_, and_
from sqlalchemy.exc import SQLAlchemyError
from telegram import (
    Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
)
from telegram.error import TelegramError
from telegram.ext import (
    Updater, CommandHandler, MessageHandler,
    Filters, CallbackQueryHandler, InlineQueryHandler
)
from telegram.ext.dispatcher import run_async

from config import TOKEN, GOVERNMENT_CHAT, CASTLE, EXT_ID
from core.chat_commands import CC_SET_WELCOME, CC_HELP, CC_SQUAD, CC_SHOW_WELCOME, CC_TURN_ON_WELCOME, \
    CC_TURN_OFF_WELCOME, CC_SET_TRIGGER, CC_UNSET_TRIGGER, CC_TRIGGER_LIST, CC_ADMIN_LIST, CC_PING, CC_DAY_STATISTICS, \
    CC_WEEK_STATISTICS, CC_BATTLE_STATISTICS, CC_ALLOW_TRIGGER_ALL, CC_DISALLOW_TRIGGER_ALL, CC_ADMINS, \
    CC_ALLOW_PIN_ALL, CC_DISALLOW_PIN_ALL, CC_BOSS_1, CC_BOSS_2, CC_BOSS_3, CC_BOSS_4, CC_OPEN_HIRING, CC_CLOSE_HIRING, \
    CC_PIN, CC_SILENT_PIN, CC_DELETE, CC_KICK
from core.commands import ADMIN_COMMAND_STATUS, ADMIN_COMMAND_RECRUIT, ADMIN_COMMAND_ORDER, ADMIN_COMMAND_SQUAD_LIST, \
    ADMIN_COMMAND_GROUPS, ADMIN_COMMAND_FIRE_UP, USER_COMMAND_ME, USER_COMMAND_BUILD, USER_COMMAND_CONTACTS, \
    USER_COMMAND_SQUAD, USER_COMMAND_STATISTICS, USER_COMMAND_TOP, USER_COMMAND_SQUAD_REQUEST, USER_COMMAND_BACK, \
    TOP_COMMAND_ATTACK, TOP_COMMAND_DEFENCE, TOP_COMMAND_EXP, STATISTICS_COMMAND_EXP, USER_COMMAND_SQUAD_LEAVE, \
    ADMIN_COMMAND_REPORTS, ADMIN_COMMAND_ADMINPANEL, ADMIN_COMMAND_ATTENDANCE, TOP_COMMAND_BUILD, \
    TOP_COMMAND_BATTLES, STATISTICS_COMMAND_SKILLS, USER_COMMAND_REGISTER, \
    USER_COMMAND_SETTINGS
from core.constants import DAYS_PROFILE_REMIND, DAYS_OLD_PROFILE_KICK
from core.functions.activity import (
    day_activity, week_activity, battle_activity
)
from core.functions.admins import (
    list_admins, admins_for_users, set_admin, del_admin,
    set_global_admin, set_super_admin, del_global_admin
)
from core.functions.ban import unban, ban
from core.functions.bosses import (
    boss_leader, boss_zhalo, boss_monoeye, boss_hydra)
from core.functions.common import (
    help_msg, ping, error, kick,
    admin_panel, stock_compare_forwarded, trade_compare, delete_msg, delete_user, user_panel, web_auth, StockType,
    stock_compare_text, MSG_CHANGES_SINCE_LAST_UPDATE, MSG_LAST_UPDATE, MSG_USER_BATTLE_REPORT,
    MSG_USER_BATTLE_REPORT_PRELIM, MSG_USER_BATTLE_REPORT_STOCK, stock_split,
    get_weighted_diff)
from core.functions.inline_keyboard_handling import (
    callback_query, inlinequery, send_status, send_order
)
from core.functions.inline_markup import QueryType
from core.functions.order_groups import group_list, add_group
from core.functions.orders import order, orders
from core.functions.pin import pin, not_pin_all, pin_all, silent_pin
from core.functions.profile import char_update, profession_update, char_show, find_by_username, find_by_character, \
    find_by_id, report_received, build_report_received, \
    repair_report_received, grant_access, handle_access_token, settings, revoke
from core.functions.squad import (
    add_squad, del_squad, set_invite_link, set_squad_name,
    enable_thorns, disable_thorns, enable_silence, disable_silence, enable_reminders, disable_reminders,
    squad_list, squad_request, list_squad_requests,
    open_hiring, close_hiring, remove_from_squad, add_to_squad, force_add_to_squad,
    leave_squad_request, squad_about, call_squad, battle_reports_show, battle_attendance_show)
from core.functions.statistics import statistic_about, exp_statistic, skill_statistic
from core.functions.top import top_about, attack_top, exp_top, def_top, week_build_top, \
    week_battle_top
from core.functions.triggers import (
    set_trigger, add_trigger, del_trigger, list_triggers, enable_trigger_all,
    disable_trigger_all, trigger_show,
    set_global_trigger, add_global_trigger, del_global_trigger
)
from core.functions.welcome import (
    welcome, set_welcome, show_welcome, enable_welcome, disable_welcome
)
from core.regexp import HERO, REPORT, BUILD_REPORT, REPAIR_REPORT, STOCK, TRADE_BOT, PROFESSION, ACCESS_CODE
from core.state import get_game_state, GameState
from core.texts import (
    MSG_MAIN_INLINE_BATTLE, MSG_MAIN_READY_TO_BATTLE_30, MSG_MAIN_READY_TO_BATTLE_45, MSG_MAIN_SEND_REPORTS,
    MSG_REPORT_SUMMARY, MSG_REPORT_TOTAL, MSG_REPORT_SUMMARY_RATING, MSG_IN_DEV, MSG_UPDATE_PROFILE,
    MSG_SQUAD_DELETE_OUTDATED,
    MSG_SQUAD_DELETE_OUTDATED_EXT)
from core.types import Session, Order, Squad, Admin, user_allowed, Character, Report, SquadMember, User, Stock
from core.utils import add_user, send_async
from cwmq import Consumer, Publisher
from cwmq.handler import mq_handler

# -----constants----
CWBOT_ID = 408101137
TRADEBOT_ID = 0
#278525885
# -------------------

logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def del_msg(bot, job):
    try:
        bot.delete_message(job.context[0], job.context[1])
    except TelegramError:
        pass


@run_async
@user_allowed
def manage_all(bot: Bot, update: Update, session, chat_data, job_queue):
    add_user(update.message.from_user, session)

    user = session.query(User).filter_by(id=update.message.from_user.id).first()
    registered = user and user.character and  (user.character.castle == CASTLE or update.message.from_user.id == EXT_ID)
    if update.message.chat.type in ['group', 'supergroup', 'channel']:
        squad = session.query(Squad).filter_by(
            chat_id=update.message.chat.id).first()
        admin = session.query(Admin).filter(
            Admin.user_id == update.message.from_user.id and
            Admin.admin_group in [update.message.chat.id, 0]).first()

        if squad is not None and squad.silence_enabled and admin is None and get_game_state() == GameState.HOWLING_WIND:
            bot.delete_message(update.message.chat.id,
                               update.message.message_id)
        if not update.message.text:
            return

        text = update.message.text.lower()

        if text.startswith(CC_SET_WELCOME):
            set_welcome(bot, update)
        elif text == CC_HELP:
            help_msg(bot, update)
        elif text == CC_SQUAD and registered:
            call_squad(bot, update)
        elif text == CC_SHOW_WELCOME:
            show_welcome(bot, update)
        elif text == CC_TURN_ON_WELCOME:
            enable_welcome(bot, update)
        elif text == CC_TURN_OFF_WELCOME:
            disable_welcome(bot, update)
        elif text.startswith(CC_SET_TRIGGER):
            set_trigger(bot, update)
        elif text.startswith(CC_UNSET_TRIGGER):
            del_trigger(bot, update)
        elif text == CC_TRIGGER_LIST:
            list_triggers(bot, update)
        elif text == CC_ADMIN_LIST:
            list_admins(bot, update)
        elif text == CC_PING:
            ping(bot, update)
        elif text == CC_DAY_STATISTICS:
            day_activity(bot, update)
        elif text == CC_WEEK_STATISTICS:
            week_activity(bot, update)
        elif text == CC_BATTLE_STATISTICS:
            battle_activity(bot, update)
        elif text == CC_ALLOW_TRIGGER_ALL:
            enable_trigger_all(bot, update)
        elif text == CC_DISALLOW_TRIGGER_ALL:
            disable_trigger_all(bot, update)
        elif text in CC_ADMINS:
            admins_for_users(bot, update)
        elif text == CC_ALLOW_PIN_ALL:
            pin_all(bot, update)
        elif text == CC_DISALLOW_PIN_ALL:
            not_pin_all(bot, update)
        elif text in CC_BOSS_1:
            boss_leader(bot, update)
        elif text in CC_BOSS_2:
            boss_zhalo(bot, update)
        elif text in CC_BOSS_3:
            boss_monoeye(bot, update)
        elif text in CC_BOSS_4:
            boss_hydra(bot, update)
        elif text == CC_OPEN_HIRING:
            open_hiring(bot, update)
        elif text == CC_CLOSE_HIRING:
            close_hiring(bot, update)
        elif update.message.reply_to_message is not None:
            if text == CC_PIN:
                pin(bot, update)
            elif text == CC_SILENT_PIN:
                silent_pin(bot, update)
            elif text == CC_DELETE:
                delete_msg(bot, update)
            elif text == CC_KICK:
                delete_user(bot, update)
            else:
                trigger_show(bot, update)
        elif re.search(REPORT, update.message.text):
            if update.message.forward_from.id == CWBOT_ID:
                report_received(bot, update)
        else:
            trigger_show(bot, update)

    elif update.message.chat.type == 'private':
        admin = session.query(Admin).filter_by(user_id=update.message.from_user.id).all()
        is_admin = False
        for _ in admin:
            is_admin = True
            break

        if 'order_wait' in chat_data and chat_data['order_wait']:
            order(bot, update, chat_data)

        elif update.message.text:
            text = update.message.text.lower()

            if text == ADMIN_COMMAND_STATUS.lower() and registered:
                send_status(bot, update)
            elif text == USER_COMMAND_BACK.lower() and registered:
                user_panel(bot, update)
            elif text == USER_COMMAND_SQUAD_REQUEST.lower() and registered:
                squad_request(bot, update)
            elif text == ADMIN_COMMAND_RECRUIT.lower():
                list_squad_requests(bot, update)
            elif text == ADMIN_COMMAND_ORDER.lower():
                orders(bot, update, chat_data)
            elif text == ADMIN_COMMAND_SQUAD_LIST.lower():
                squad_list(bot, update)
            elif text == ADMIN_COMMAND_GROUPS.lower():
                group_list(bot, update)
            elif text == ADMIN_COMMAND_REPORTS.lower():
                battle_reports_show(bot, update)
            elif text == ADMIN_COMMAND_ATTENDANCE.lower():
                battle_attendance_show(bot, update)
            elif text == ADMIN_COMMAND_FIRE_UP.lower():
                remove_from_squad(bot, update)
            elif text == USER_COMMAND_ME.lower():
                char_show(bot, update)
            elif text == USER_COMMAND_REGISTER.lower():
                grant_access(bot, update)
            elif text == USER_COMMAND_SETTINGS.lower():
                settings(bot, update)
            elif text == USER_COMMAND_TOP.lower() and registered:
                top_about(bot, update)
            elif text == TOP_COMMAND_ATTACK.lower():
                attack_top(bot, update)
            elif text == TOP_COMMAND_DEFENCE.lower():
                def_top(bot, update)
            elif text == TOP_COMMAND_EXP.lower():
                exp_top(bot, update)
            elif text == TOP_COMMAND_BUILD.lower():
                week_build_top(bot, update)
            elif text == TOP_COMMAND_BATTLES.lower():
                week_battle_top(bot, update)
            elif text == USER_COMMAND_BUILD.lower():
                send_async(bot,
                           chat_id=update.message.chat.id,
                           text=MSG_IN_DEV,
                           parse_mode=ParseMode.HTML)
            elif text == USER_COMMAND_STATISTICS.lower():
                statistic_about(bot, update)
            elif text == STATISTICS_COMMAND_EXP.lower():
                exp_statistic(bot, update)
            elif text == STATISTICS_COMMAND_SKILLS.lower():
                skill_statistic(bot, update)
            elif text == USER_COMMAND_SQUAD.lower():
                squad_about(bot, update)
            elif text == USER_COMMAND_SQUAD_LEAVE.lower():
                leave_squad_request(bot, update)
            elif text == USER_COMMAND_CONTACTS.lower():
                web_auth(bot, update)
            elif text == ADMIN_COMMAND_ADMINPANEL.lower():
                admin_panel(bot, update)
            elif 'wait_group_name' in chat_data and chat_data['wait_group_name']:
                add_group(bot, update, chat_data)

            elif update.message.forward_from:
                from_id = update.message.forward_from.id

                if from_id == CWBOT_ID:
                    if text.startswith(STOCK):
                        stock_compare_forwarded(bot, update, chat_data)
                    elif re.search(HERO, update.message.text):
                        char_update(bot, update)
                    elif re.search(REPORT, update.message.text):
                        report_received(bot, update)
                    elif re.search(BUILD_REPORT, update.message.text):
                        build_report_received(bot, update)
                    elif re.search(REPAIR_REPORT, update.message.text):
                        repair_report_received(bot, update)
                    elif re.search(PROFESSION, update.message.text):
                        profession_update(bot, update)
                    elif re.search(ACCESS_CODE, update.message.text):
                        handle_access_token(bot, update)
                elif from_id == TRADEBOT_ID:
                    if TRADE_BOT in text:
                        trade_compare(bot, update, chat_data)
            elif not is_admin:
                user_panel(bot, update)
            else:
                order(bot, update, chat_data)
        elif not is_admin:
            user_panel(bot, update)
        else:
            order(bot, update, chat_data)


@run_async
def ready_to_battle(bot: Bot, job_queue):
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

            msg = send_order(bot, new_order.text, 0, new_order.chat_id, markup = None)

            try:
                msg = msg.result().result()
                if msg is not None:
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
def refresh_api_users(bot: Bot, job_queue):
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
def report_after_battle(bot: Bot, job_queue):
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
            if user.squad_membership and user.squad_membership.first() and \
                    user.squad_membership.first().approved and user.squad_membership.first().squad.testing_squad:
                onboarding_squad_member = True

            if user.is_api_profile_allowed and user.is_api_stock_allowed and \
                    user.setting_automated_report and user.api_token and \
                    onboarding_squad_member:
                prev_stock = session.query(Stock).filter_by(
                    user_id=user.id,
                    stock_type=StockType.Stock.value
                ).order_by(Stock.date.desc()).limit(1).offset(1).one()

                prev_character = session.query(Character).filter_by(
                    user_id=user.id,
                ).order_by(Character.date.desc()).limit(1).offset(1).one()

                earned_exp = user.character.exp - prev_character.exp
                earned_gold = user.character.gold - prev_character.gold

                # cmp stock
                second_newest = session.query(Stock).filter_by(
                    user_id=user.id,
                    stock_type=StockType.Stock.value
                ).order_by(Stock.date.desc()).limit(1).offset(1).one()

                resources_new, resources_old = stock_split(second_newest.stock, user.stock.stock)
                resource_diff_add, resource_diff_del = get_weighted_diff(resources_old, resources_new)
                stock_diff = stock_compare_text(second_newest.stock, user.stock.stock)

                gained_sum = sum([x[1] for x in resource_diff_add])
                lost_sum = sum([x[1] for x in resource_diff_del])
                diff_stock = gained_sum + lost_sum

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

@run_async
#@admin_allowed()
def ready_to_battle_result(bot: Bot, update: Update):
#def ready_to_battle_result(bot: Bot, job_queue):
    if GOVERNMENT_CHAT is None:
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
            now= now - timedelta(days=1)
        time_from = now.replace(hour=(int((now.hour+1) / 8) * 8 - 1 + 24) % 24, minute=0, second=0)
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

                    players_atk += 1  if report.earned_stock > 0 else 0 
                    players_def += 1  if report.earned_exp > 0 and report.earned_stock == 0 else 0 
                    total_reports += 1
            global_def += full_def
            global_atk += full_atk
            global_exp += full_exp
            global_stock += full_stock
            global_gold += full_gold
            global_members += total_members
            global_reports += total_reports
            if total_members > 0:
                text += MSG_REPORT_SUMMARY.format(squad.squad_name, total_reports, total_members, full_atk, full_def, full_exp, full_gold, full_stock)
        text +=  MSG_REPORT_SUMMARY.format('TOTAL', global_reports, global_members, global_atk, global_def, global_exp, global_gold, global_stock)
        text +=  MSG_REPORT_TOTAL.format(players_atk, players_def, real_atk, real_def)
        send_async(bot, chat_id=GOVERNMENT_CHAT, text=text, parse_mode=ParseMode.HTML, reply_markup=None)

    except SQLAlchemyError as err:
        bot.logger.error(str(err))
        Session.rollback()


@run_async
def fresh_profiles(bot: Bot, job_queue):
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


def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    disp = updater.dispatcher

    # on different commands - answer in Telegram
    #disp.add_handler(CommandHandler("test", ready_to_battle_result))
    disp.add_handler(CommandHandler("start", user_panel))
    disp.add_handler(CommandHandler("test", ready_to_battle_result))
    disp.add_handler(CommandHandler("admin", admin_panel))
    disp.add_handler(CommandHandler("help", help_msg))
    disp.add_handler(CommandHandler("ping", ping))
    disp.add_handler(CommandHandler("set_global_trigger", set_global_trigger))
    disp.add_handler(CommandHandler("add_global_trigger", add_global_trigger))
    disp.add_handler(CommandHandler("del_global_trigger", del_global_trigger))
    disp.add_handler(CommandHandler("set_trigger", set_trigger))
    disp.add_handler(CommandHandler("add_trigger", add_trigger))
    disp.add_handler(CommandHandler("del_trigger", del_trigger))
    disp.add_handler(CommandHandler("list_triggers", list_triggers))
    disp.add_handler(CommandHandler("set_welcome", set_welcome))
    disp.add_handler(CommandHandler("enable_welcome", enable_welcome))
    disp.add_handler(CommandHandler("disable_welcome", disable_welcome))
    disp.add_handler(CommandHandler("show_welcome", show_welcome))
    disp.add_handler(CommandHandler("add_admin", set_admin))
    disp.add_handler(CommandHandler("add_global_admin", set_global_admin))
    disp.add_handler(CommandHandler("del_global_admin", del_global_admin))
    disp.add_handler(CommandHandler("add_super_admin", set_super_admin))
    disp.add_handler(CommandHandler("del_admin", del_admin))
    disp.add_handler(CommandHandler("list_admins", list_admins))
    disp.add_handler(CommandHandler("kick", kick))
    disp.add_handler(CommandHandler("enable_trigger", enable_trigger_all))
    disp.add_handler(CommandHandler("disable_trigger", disable_trigger_all))
    disp.add_handler(CommandHandler("me", char_show))
    disp.add_handler(CommandHandler("grant_access", grant_access))
    disp.add_handler(CommandHandler("add_squad", add_squad))
    disp.add_handler(CommandHandler("del_squad", del_squad))
    disp.add_handler(CommandHandler("enable_thorns", enable_thorns))
    disp.add_handler(CommandHandler("enable_silence", enable_silence))
    disp.add_handler(CommandHandler("enable_reminders", enable_reminders))
    disp.add_handler(CommandHandler("disable_thorns", disable_thorns))
    disp.add_handler(CommandHandler("disable_silence", disable_silence))
    disp.add_handler(CommandHandler("disable_reminders", disable_reminders))
    disp.add_handler(CommandHandler("set_squad_name", set_squad_name))
    disp.add_handler(CommandHandler("set_invite_link", set_invite_link))
    disp.add_handler(CommandHandler("find", find_by_username))
    disp.add_handler(CommandHandler("findc", find_by_character))
    disp.add_handler(CommandHandler("findi", find_by_id))
    disp.add_handler(CommandHandler("add", add_to_squad))
    disp.add_handler(CommandHandler("forceadd", force_add_to_squad))
    disp.add_handler(CommandHandler("ban", ban))
    disp.add_handler(CommandHandler("unban", unban))
    disp.add_handler(CommandHandler("revoke", revoke))

    disp.add_handler(CallbackQueryHandler(callback_query, pass_chat_data=True, pass_job_queue=True))

    disp.add_handler(InlineQueryHandler(inlinequery))

    # on noncommand i.e message - echo the message on Telegram
    disp.add_handler(MessageHandler(Filters.status_update, welcome))
    # disp.add_handler(MessageHandler(
    # Filters.text, manage_text, pass_chat_data=True))
    disp.add_handler(MessageHandler(
        Filters.all, manage_all, pass_chat_data=True, pass_job_queue=True))

    # log all errors
    disp.add_error_handler(error)
    #
    updater.job_queue.run_daily(callback =ready_to_battle, time=time(hour=6, minute=30), context=MSG_MAIN_READY_TO_BATTLE_30)#6
    updater.job_queue.run_daily(callback=ready_to_battle, time=time(hour=6, minute=45), context=MSG_MAIN_READY_TO_BATTLE_45)
    updater.job_queue.run_daily(callback=ready_to_battle, time=time(hour=7, minute=3), context=MSG_MAIN_SEND_REPORTS)
    updater.job_queue.run_daily(callback=ready_to_battle_result, time=time(hour=8, minute=0))
    # updater.job_queue.run_daily(ready_to_battle_result,
    #                             time(hour=6, minute=55))
    # updater.job_queue.run_daily(ready_to_battle, time(hour=10, minute=50))
    # updater.job_queue.run_daily(ready_to_battle_result,
    #                             time(hour=10, minute=55))
    updater.job_queue.run_daily(callback=ready_to_battle, time=time(hour=14, minute=30), context =MSG_MAIN_READY_TO_BATTLE_30)
    updater.job_queue.run_daily(callback=ready_to_battle, time=time(hour=14, minute=45), context =MSG_MAIN_READY_TO_BATTLE_45)
    updater.job_queue.run_daily(callback=ready_to_battle, time=time(hour=15, minute=3), context=MSG_MAIN_SEND_REPORTS)
    updater.job_queue.run_daily(callback=ready_to_battle_result, time=time(hour=16, minute=0))
    # updater.job_queue.run_daily(ready_to_battle_result,)
     #updater.job_queue.run_daily(ready_to_battle, time(hour=14, minute=50))
    # updater.job_queue.run_daily(ready_to_battle_result,
    #                             time(hour=14, minute=55))
    # updater.job_queue.run_daily(ready_to_battle, time(hour=18, minute=50))
    # updater.job_queue.run_daily(ready_to_battle_result,
    #                             time(hour=18, minute=55))
    updater.job_queue.run_daily(callback=ready_to_battle, time=time(hour=22, minute=30), context =MSG_MAIN_READY_TO_BATTLE_30)
    updater.job_queue.run_daily(callback=ready_to_battle, time=time(hour=22, minute=45), context =MSG_MAIN_READY_TO_BATTLE_45)
    updater.job_queue.run_daily(callback=ready_to_battle, time=time(hour=23, minute=3), context=MSG_MAIN_SEND_REPORTS)
    updater.job_queue.run_daily(callback=ready_to_battle_result, time=time(hour=0, minute=0))
    # updater.job_queue.run_daily(ready_to_battle_result,
    #                             time(hour=22, minute=55))
    updater.job_queue.run_daily(fresh_profiles,
                                time(hour=6, minute=40))
    updater.job_queue.run_daily(fresh_profiles,
                                time(hour=14, minute=40))
    updater.job_queue.run_daily(fresh_profiles,
                                time(hour=22, minute=40))
    #updater.job_queue.run_daily(fresh_profiles,
                                #time(hour=18, minute=40))
    #updater.job_queue.run_daily(fresh_profiles,
                                #time(hour=22, minute=40))i


    # API refreshing, etc.
    # Pre-War
    updater.job_queue.run_daily(callback=refresh_api_users, time=time(hour=6, minute=57))
    updater.job_queue.run_daily(callback=refresh_api_users, time=time(hour=14, minute=57))
    updater.job_queue.run_daily(callback=refresh_api_users, time=time(hour=22, minute=57))

    # After-War
    updater.job_queue.run_daily(callback=refresh_api_users, time=time(hour=7, minute=3))
    updater.job_queue.run_daily(callback=refresh_api_users, time=time(hour=15, minute=3))
    updater.job_queue.run_daily(callback=refresh_api_users, time=time(hour=23, minute=3))

    # Battle Report
    updater.job_queue.run_daily(callback=report_after_battle, time=time(hour=7, minute=5))
    updater.job_queue.run_daily(callback=report_after_battle, time=time(hour=15, minute=5))
    updater.job_queue.run_daily(callback=report_after_battle, time=time(hour=23, minute=5))

    # THIS IS FOR DEBUGGING AND TESTING!
    #updater.job_queue.run_once(report_after_battle, datetime.now()+timedelta(seconds=5))

    # Start the Bot
    updater.start_polling()

    # After we've set up the bot we also now start consuming the CW APMQ messages in seperate threads
    # and handle them

    # Consumer...
    logging.info("Setting up MQ Consumer")
    q_in = Consumer(
        mq_handler,
        dispatcher=updater
    )
    q_in.setName("T1_IN")
    q_in.start()

    # Publisher
    q_out = Publisher()
    q_out.setName("T1_OUT")
    q_out.start()

    print("Current game time: {}".format(get_game_state()))

    # app.run(port=API_PORT)
    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    # Force bot TZ into UTC
    import os
    os.environ['TZ'] = 'UTC'

    main()
