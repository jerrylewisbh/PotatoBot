# -*- coding: utf-8 -*-

import logging
from datetime import datetime, timedelta
from logging.handlers import TimedRotatingFileHandler

from core.bot import MQBot
from core.db import Session
from core.handler import buttons, chats, manage_all
from core.handler import commands
from core.handler.callback import callback_query
from core.handler.inline import inlinequery
from core.jobs.job_queue import (add_after_war_messages,
                                 add_battle_report_messages,
                                 add_pre_war_messages,
                                 add_war_warning_messages)
from core.logging import TelegramHandler, HtmlFormatter
from core.texts import *
from cwmq import Consumer, Publisher
from cwmq.handler.deals import deals_handler
from cwmq.handler.offers import offers_handler
from cwmq.handler.profiles import profile_handler
from functions.battle import report_after_battle, ready_to_battle_result, refresh_api_users, fresh_profiles, \
    ready_to_battle
from functions.common import error_callback
from functions.welcome import (welcome)
from ratelimitingfilter import RateLimitingFilter
from telegram.ext import (CallbackQueryHandler, InlineQueryHandler,
                          MessageQueue, Updater)
from telegram.ext import MessageHandler, Filters
from telegram.utils.request import Request

from botato.cwmq.handler.digest import digest_handler
from config import DEBUG, LOGFILE, TOKEN, LOG_GROUP_LEVEL, LOG_GROUP, LOG_LEVEL

Session()


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
