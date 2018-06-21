# -*- coding: utf-8 -*-

import logging
import re
from datetime import datetime, timedelta
from logging.handlers import TimedRotatingFileHandler

from telegram import Bot, Update
from telegram.ext import (CallbackQueryHandler, InlineQueryHandler,
                          MessageQueue, Updater)
from telegram.ext.dispatcher import run_async

from config import CASTLE, CWBOT_ID, DEBUG, EXT_ID, LOGFILE, TOKEN
from core.battle import report_after_battle
from core.bot import MQBot
from core.decorators import user_allowed
from core.functions.common import (delete_msg, delete_user, error,
                                   stock_compare_forwarded)
from core.functions.common.pin import pin, silent_pin
from core.functions.inline_keyboard_handling import (callback_query,
                                                     inlinequery)
from core.functions.order_groups import add_group
from core.functions.orders import order
from core.functions.profile import (build_report_received, char_update,
                                    handle_access_token,
                                    profession_update, repair_report_received,
                                    report_received, user_panel)
from core.functions.quest import parse_quest
from core.functions.triggers import (trigger_show)
from core.functions.welcome import (welcome)
from core.handlers.group_handler import *
from core.handlers.private_handler import *
from core.handlers.trigger_handler import add_commands
from core.jobs.job_queue import (add_after_war_messages,
                                 add_battle_report_messages,
                                 add_pre_war_messages,
                                 add_war_warning_messages)
from core.regexp import (ACCESS_CODE, BUILD_REPORT, HERO, PROFESSION,
                         REPAIR_REPORT, REPORT, STOCK)
from core.state import GameState, get_game_state
from core.types import Admin, Session, Squad, User
from core.utils import create_or_update_user
from cwmq import Consumer, Publisher
from cwmq.handler.deals import deals_handler
from cwmq.handler.digest import digest_handler
from cwmq.handler.offers import offers_handler
from cwmq.handler.profiles import profile_handler

Session()


@run_async
@user_allowed
def manage_all(bot: Bot, update: Update, chat_data, job_queue):
    create_or_update_user(update.message.from_user)

    user = Session.query(User).filter_by(id=update.message.from_user.id).first()
    registered = user and user.character and (user.character.castle == CASTLE or update.message.from_user.id == EXT_ID)
    if update.message.chat.type in ['group', 'supergroup', 'channel']:
        squad = Session.query(Squad).filter_by(
            chat_id=update.message.chat.id).first()
        admin = Session.query(Admin).filter(
            Admin.user_id == update.message.from_user.id and
            Admin.admin_group in [update.message.chat.id, 0]).first()

        logging.debug("SILENCE STATE: State: {}, Squad: {}, Admin: {}".format(
            get_game_state(),
            squad.squad_name if squad else 'NO SQUAD',
            admin,
        ))

        if squad and squad.silence_enabled and not admin and GameState.BATTLE_SILENCE in get_game_state():
            bot.delete_message(update.message.chat.id,
                               update.message.message_id)
        if not update.message.text:
            return

        handlers = [
            welcome_handler,
            help_handler,
            squad_handler(registered),
            show_welcome_handler,
            enable_welcome_handler,
            disable_welcome_handler,
            set_trigger_handler,
            del_trigger_handler,
            list_triggers_handler,
            list_admins_handler,
            ping_handler,
            day_activity_handler,
            week_activity_handler,
            battle_activity_handler,
            enable_trigger_all_handler,
            disable_trigger_all_handler,
            admins_for_users_handler,
            pin_all_handler,
            not_pin_all_handler,
            open_hiring_handler,
            close_hiring_handler
        ]

        text = update.message.text.lower()

        is_msg_handled = handle_message(handlers, text, bot, update)

        if not is_msg_handled:
            if update.message.reply_to_message is not None:
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
        admin = Session.query(Admin).filter_by(user_id=update.message.from_user.id).all()
        is_admin = False
        for _ in admin:
            is_admin = True
            break

        if 'order_wait' in chat_data and chat_data['order_wait']:
            order(bot, update, chat_data)
        elif update.message.text:

            handlers = [
                send_status_handler(registered),
                user_panel_handler(registered),
                squad_request_handler(registered),
                list_squad_requests_handler,
                orders_handler,
                squad_list_handler,
                group_list_handler,
                battle_reports_show_handler,
                battle_attendance_show_handler,
                remove_from_squad_handler,
                show_char_handler,
                grant_access_handler,
                settings_handler,
                top_about_handler(registered),
                attack_top_handler,
                def_top_handler,
                exp_top_handler,
                week_build_top_handler,
                week_battle_top_handler,
                statistic_about_handler,
                exp_statistic_handler,
                skill_statistic_handler,
                quest_statistic_handler,
                foray_statistic_handler,
                squad_about_handler,
                leave_squad_request_handler,
                admin_panel_handler,
                hide_gold_info_handler,
                sniping_info_handler
            ]

            text = update.message.text.lower()

            is_msg_handled = handle_message(handlers, text, bot, update)

            if not is_msg_handled:
                if 'wait_group_name' in chat_data and chat_data['wait_group_name']:
                    add_group(bot, update, chat_data)
                # TODO: FWD Checks are no longer needed here if command_handler decorator is used properly.
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
    logger.setLevel(logging.DEBUG)
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
        updater.job_queue.run_once(report_after_battle, datetime.now() + timedelta(seconds=5))

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
        digest_handler,
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
