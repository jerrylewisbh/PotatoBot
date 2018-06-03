# -*- coding: utf-8 -*-

import logging
import re
from config import CASTLE, DEBUG, EXT_ID, TOKEN, LOGFILE
from datetime import datetime, time, timedelta
from logging.handlers import TimedRotatingFileHandler

from core.battle import report_after_battle
from core.bot import MQBot
from core.chat_commands import (CC_ADMIN_LIST, CC_ADMINS, CC_ALLOW_PIN_ALL,
                                CC_ALLOW_TRIGGER_ALL, CC_BATTLE_STATISTICS,
                                CC_BOSS_1, CC_BOSS_2, CC_BOSS_3, CC_BOSS_4,
                                CC_CLOSE_HIRING, CC_DAY_STATISTICS, CC_DELETE,
                                CC_DISALLOW_PIN_ALL, CC_DISALLOW_TRIGGER_ALL,
                                CC_HELP, CC_KICK, CC_OPEN_HIRING, CC_PIN,
                                CC_PING, CC_SET_TRIGGER, CC_SET_WELCOME,
                                CC_SHOW_WELCOME, CC_SILENT_PIN, CC_SQUAD,
                                CC_TRIGGER_LIST, CC_TURN_OFF_WELCOME,
                                CC_TURN_ON_WELCOME, CC_UNSET_TRIGGER,
                                CC_WEEK_STATISTICS)
from core.commands import (ADMIN_COMMAND_ADMINPANEL, ADMIN_COMMAND_ATTENDANCE,
                           ADMIN_COMMAND_FIRE_UP, ADMIN_COMMAND_GROUPS,
                           ADMIN_COMMAND_ORDER, ADMIN_COMMAND_RECRUIT,
                           ADMIN_COMMAND_REPORTS, ADMIN_COMMAND_SQUAD_LIST,
                           ADMIN_COMMAND_STATUS, STATISTICS_COMMAND_EXP,
                           STATISTICS_COMMAND_SKILLS, TOP_COMMAND_ATTACK,
                           TOP_COMMAND_BATTLES, TOP_COMMAND_BUILD,
                           TOP_COMMAND_DEFENCE, TOP_COMMAND_EXP,
                           USER_COMMAND_BACK, USER_COMMAND_BUILD,
                           USER_COMMAND_CONTACTS, USER_COMMAND_ME,
                           USER_COMMAND_REGISTER, USER_COMMAND_SETTINGS,
                           USER_COMMAND_SQUAD, USER_COMMAND_SQUAD_LEAVE,
                           USER_COMMAND_SQUAD_REQUEST, USER_COMMAND_STATISTICS,
                           USER_COMMAND_TOP, USER_COMMAND_HIDE, USER_COMMAND_EXCHANGE)
from core.exchange import sniping_info, hide_gold_info
from core.functions.activity import (battle_activity, day_activity,
                                     week_activity)
from core.functions.admins import admins_for_users, list_admins
from core.functions.bosses import (boss_hydra, boss_leader, boss_monoeye,
                                   boss_zhalo)
from core.functions.common import (admin_panel, delete_msg, delete_user, error,
                                   help_msg, ping, stock_compare_forwarded,
                                   trade_compare, user_panel, web_auth)
from core.functions.inline_keyboard_handling import (callback_query,
                                                     inlinequery, send_status)
from core.functions.order_groups import add_group, group_list
from core.functions.orders import order, orders
from core.functions.pin import not_pin_all, pin, pin_all, silent_pin
from core.functions.profile import (build_report_received, char_show,
                                    char_update, grant_access,
                                    handle_access_token, profession_update,
                                    repair_report_received, report_received,
                                    settings)
from core.functions.quest import parse_quest
from core.functions.squad import (battle_attendance_show, battle_reports_show,
                                  call_squad, close_hiring,
                                  leave_squad_request, list_squad_requests,
                                  open_hiring, remove_from_squad, squad_about,
                                  squad_list, squad_request)
from core.functions.statistics import (exp_statistic, skill_statistic,
                                       statistic_about)
from core.functions.top import (attack_top, def_top, exp_top, top_about,
                                week_battle_top, week_build_top)
from core.functions.triggers import (del_trigger, disable_trigger_all,
                                     enable_trigger_all, list_triggers,
                                     set_trigger, trigger_show)
from core.functions.welcome import (disable_welcome, enable_welcome,
                                    set_welcome, show_welcome, welcome)
from core.handlers.trigger_handler import add_commands
from core.jobs.job_queue import (add_after_war_messages,
                                 add_battle_report_messages,
                                 add_pre_war_messages,
                                 add_war_warning_messages)
from core.regexp import (ACCESS_CODE, BUILD_REPORT, HERO, PROFESSION,
                         REPAIR_REPORT, REPORT, STOCK, TRADE_BOT)
from core.state import GameState, get_game_state
from core.texts import MSG_IN_DEV
from core.types import Admin, Squad, User, user_allowed, Session
from core.utils import add_user, send_async
from cwmq import Consumer, Publisher
from cwmq.handler.deals import deals_handler
from cwmq.handler.offers import offers_handler
from cwmq.handler.profiles import profile_handler
from telegram import Bot, ParseMode, Update
from telegram.error import TelegramError
from telegram.ext import (CallbackQueryHandler, Filters, InlineQueryHandler,
                          MessageHandler, Updater, MessageQueue)
from telegram.ext.dispatcher import run_async

# -----constants----
CWBOT_ID = 408101137
TRADEBOT_ID = 0
# 278525885
# -------------------


@run_async
@user_allowed
def manage_all(bot: Bot, update: Update, chat_data, job_queue):
    session = Session()
    add_user(update.message.from_user)

    user = session.query(User).filter_by(id=update.message.from_user.id).first()
    registered = user and user.character and (user.character.castle == CASTLE or update.message.from_user.id == EXT_ID)
    if update.message.chat.type in ['group', 'supergroup', 'channel']:
        squad = session.query(Squad).filter_by(
            chat_id=update.message.chat.id).first()
        admin = session.query(Admin).filter(
            Admin.user_id == update.message.from_user.id and
            Admin.admin_group in [update.message.chat.id, 0]).first()

        logging.warning("SILENCE STATE: State: {}, Squad: {}, Admin: {}".format(
            get_game_state(),
            squad.squad_name if squad else 'NO SQUAD',
            admin,
        ))

        if squad and squad.silence_enabled and not admin and GameState.BATTLE_SILENCE in get_game_state():
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
            elif text == USER_COMMAND_HIDE.lower():
                hide_gold_info(bot, update)
            elif text == USER_COMMAND_EXCHANGE.lower():
                sniping_info(bot, update)
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
                    else:
                        # Handle everying else as Quest-Text.. At least for now...
                        parse_quest(bot, update)
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


def main():
    # Logging!
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Logging for console
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    rh = TimedRotatingFileHandler(LOGFILE, when='midnight', backupCount=10)
    rh.setLevel(logging.DEBUG)
    rh.setFormatter(formatter)
    logger.addHandler(rh)

    # Create the EventHandler and pass it your bot's token.
    from telegram.ext import MessageHandler, Filters
    from telegram.utils.request import Request

    token = TOKEN
    # for test purposes limit global throughput to 3 messages per 3 seconds
    q = MessageQueue(all_burst_limit=3, all_time_limit_ms=3000)
    request = Request(con_pool_size=8)
    bot = MQBot(token, request=request, mqueue=q)
    updater = Updater(bot=bot)
    updater.bot.logger.setLevel(logging.INFO)

    # Get the dispatcher to register handler
    disp = updater.dispatcher

    add_commands(disp)

    disp.add_handler(CallbackQueryHandler(callback_query, pass_chat_data=True, pass_job_queue=True))

    disp.add_handler(InlineQueryHandler(inlinequery))

    # on noncommand i.e message - echo the message on Telegram
    disp.add_handler(MessageHandler(Filters.status_update, welcome))
    # disp.add_handler(MessageHandler(
    # Filters.text, manage_text, pass_chat_data=True))

    disp.add_handler(MessageHandler(
        Filters.all,
        manage_all,
        pass_chat_data=True,
        pass_job_queue=True
    ))

    # log all errors
    disp.add_error_handler(error)
    add_war_warning_messages(updater)

    # API refreshing, etc.
    add_pre_war_messages(updater)
    add_after_war_messages(updater)
    add_battle_report_messages(updater)

    # THIS IS FOR DEBUGGING AND TESTING!
    if DEBUG:
        updater.job_queue.run_once(report_after_battle, datetime.now() + timedelta(seconds=15))

    # Start the Bot
    updater.start_polling()

    # After we've set up the bot we also now start consuming the CW APMQ messages in seperate threads
    # and handle them

    # Consumer...
    logging.info("Setting up MQ Consumer")
    q_in = Consumer(
        profile_handler,
        deals_handler,
        offers_handler,
        dispatcher=updater
    )
    q_in.setName("T1_IN")
    q_in.start()

    # Publisher
    q_out = Publisher()
    q_out.setName("T1_OUT")
    q_out.start()

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
