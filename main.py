# -*- coding: utf-8 -*-

import logging
from datetime import datetime, timedelta
from logging.handlers import TimedRotatingFileHandler

from ratelimitingfilter import RateLimitingFilter
from telegram import Bot, Update
from telegram.ext import (CallbackQueryHandler, InlineQueryHandler,
                          MessageQueue, Updater)
from telegram.ext import MessageHandler, Filters
from telegram.ext.dispatcher import run_async
from telegram.utils.request import Request

from config import DEBUG, LOGFILE, TOKEN, CWBOT_ID, LOG_GROUP_LEVEL, LOG_GROUP, LOG_LEVEL
from functions.battle import report_after_battle, ready_to_battle_result, refresh_api_users, fresh_profiles, ready_to_battle
from core.bot import MQBot
from core.decorators import command_handler
from core.handler import buttons, chats
from core.handler import commands
from core.handler.callback import callback_query
from core.handler.inline.__init__ import (inlinequery)
from core.jobs.job_queue import (add_after_war_messages,
                                 add_battle_report_messages,
                                 add_pre_war_messages,
                                 add_war_warning_messages)
from core.texts import *
from core.logging import TelegramHandler, HtmlFormatter
from core.state import GameState, get_game_state
from core.types import Admin, Session, Squad, User
from cwmq import Consumer, Publisher
from cwmq.handler.deals import deals_handler
from cwmq.handler.digest import digest_handler
from cwmq.handler.offers import offers_handler
from cwmq.handler.profiles import profile_handler
from functions.common import error_callback
from functions.order_groups import add_group
from functions.orders import order
from functions.profile import user_panel
from functions.quest import parse_quest
from functions.report import fwd_report
from functions.triggers import trigger_show
from functions.welcome import (welcome)

Session()

@run_async
@command_handler(
    allow_channel=True,
    allow_group=True,
    allow_private=True
)
def manage_all(bot: Bot, update: Update, user: User, chat_data, job_queue):#
    if update.effective_message.chat.type == "channel":
        fwd_report(bot, update)
    elif update.effective_message.chat.type in ['group', 'supergroup']:
        squad = Session.query(Squad).filter_by(chat_id=update.message.chat.id).first()

        admin = Session.query(Admin).filter(
            Admin.user_id == update.message.from_user.id and
            Admin.admin_group in [update.message.chat.id, 0]).first()

        logging.debug("SILENCE STATE: State: {}, Squad: {}, Admin: {}".format(
            get_game_state(),
            squad.squad_name if squad else 'NO SQUAD',
            admin,
        ))

        if squad and squad.silence_enabled and not admin and GameState.BATTLE_SILENCE in get_game_state():
            bot.delete_message(
                update.message.chat.id,
                update.message.message_id
            )

        if update.message.text:
            trigger_show(bot, update)

    elif update.effective_message.chat.type == 'private':
        admin = Session.query(Admin).filter_by(user_id=update.message.from_user.id).all()
        is_admin = False
        for _ in admin:
            is_admin = True
            break
        if 'order_wait' in chat_data and chat_data['order_wait']:
            order(bot, update, user, chat_data=chat_data)
        elif update.message.text:
            if update.message.forward_from and update.message.forward_from.id == CWBOT_ID:
                parse_quest(bot, update, user)
            elif 'wait_group_name' in chat_data and chat_data['wait_group_name']:
                add_group(bot, update, user, chat_data=chat_data)
            elif not is_admin:
                user_panel(bot, update)
            else:
                order(bot, update, user, chat_data=chat_data)
        elif not is_admin:
            user_panel(bot, update)
        else:
            order(bot, update, user, chat_data=chat_data)

def main():
    # Logging!
    logger = logging.getLogger()
    logger.setLevel(LOG_LEVEL)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Logging for console
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # Logging into file
    rh = TimedRotatingFileHandler(LOGFILE, when='midnight', backupCount=10)
    rh.setLevel(logging.DEBUG)
    rh.setFormatter(formatter)
    logger.addHandler(rh)

    token = TOKEN
    q = MessageQueue()
    request = Request(con_pool_size=8)
    bot = MQBot(token, request=request, mqueue=q)
    updater = Updater(bot=bot)
    updater.bot.logger.setLevel(logging.INFO)

    # Logging to telegram
    # We enable throttling to avoid spamming the channel...
    th = TelegramHandler(bot, LOG_GROUP)
    th.setLevel(LOG_GROUP_LEVEL)
    th.setFormatter(HtmlFormatter(use_emoji=True))
    throttle = RateLimitingFilter(rate=1, per=60, burst=5)
    th.addFilter(throttle)
    logger.addHandler(th)

    # Get the dispatcher to register handler
    disp = updater.dispatcher

    commands.add_handler(disp)
    buttons.add_handler(disp)
    chats.add_handler(disp)

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

    # Python Telegram Bot Error handler
    disp.add_error_handler(error_callback)

    # API refreshing, etc.
    add_war_warning_messages(updater)
    add_pre_war_messages(updater)
    add_after_war_messages(updater)
    add_battle_report_messages(updater)

    # THIS IS FOR DEBUGGING AND TESTING!
    if DEBUG:
        now = datetime.now()
        updater.job_queue.run_once(report_after_battle, now + timedelta(seconds=5))
        updater.job_queue.run_once(ready_to_battle_result, now + timedelta(seconds=10))
        updater.job_queue.run_once(refresh_api_users, now + timedelta(seconds=15))
        updater.job_queue.run_once(fresh_profiles, now + timedelta(seconds=20))
        updater.job_queue.run_once(ready_to_battle, now + timedelta(seconds=5), context=MSG_MAIN_SEND_REPORTS)
        updater.job_queue.run_once(ready_to_battle, now + timedelta(seconds=30), context=MSG_MAIN_READY_TO_BATTLE_30)
        updater.job_queue.run_once(ready_to_battle, now + timedelta(seconds=35), context=MSG_MAIN_READY_TO_BATTLE_45)

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
