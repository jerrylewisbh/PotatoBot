# -*- coding: utf-8 -*-

from datetime import datetime, time
import json
import logging
import re
from threading import Thread

from telegram import (
    Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
)
from telegram.ext import (
    Updater, CommandHandler, MessageHandler,
    Filters, CallbackQueryHandler
)
from telegram.ext.dispatcher import run_async
from telegram.error import TelegramError

from config import TOKEN, GOVERNMENT_CHAT
from core.functions.activity import (
    day_activity, week_activity, battle_activity
)
from core.functions.admins import (
    list_admins, admins_for_users, set_admin, del_admin,
    set_global_admin, set_super_admin, del_global_admin
)
from core.functions.bosses import (
    boss_leader, boss_zhalo, boss_monoeye, boss_hydra)
from core.functions.orders import order, orders

from core.functions.common import (
    help_msg, ping, start, error, kick,
    admin_panel, stock_compare, trade_compare,
    delete_msg, delete_user
)
from core.functions.inline_keyboard_handling import (
    callback_query, send_status, send_order, QueryType
)
from core.functions.order_groups import group_list, add_group
from core.functions.pin import pin, not_pin_all, pin_all, silent_pin
from core.functions.profile import char_update, char_show, find_by_username
from core.functions.squad import (
    add_squad, del_squad, set_invite_link, set_squad_name,
    enable_thorns, disable_thorns,
    squad_list, squad_request, list_squad_requests,
    open_hiring, close_hiring, remove_from_squad, add_to_squad
)
from core.functions.triggers import (
    set_trigger, add_trigger, del_trigger, list_triggers, enable_trigger_all,
    disable_trigger_all, trigger_show,
    set_global_trigger, add_global_trigger, del_global_trigger
)
from core.functions.welcome import (
    welcome, set_welcome, show_welcome, enable_welcome, disable_welcome
)
from core.regexp import PROFILE, HERO
from core.texts import (
    MSG_SQUAD_READY, MSG_FULL_TEXT_LINE, MSG_FULL_TEXT_TOTAL
)
from core.types import Session, Order, Squad, Admin, user_allowed
from core.utils import add_user, send_async

from sqlalchemy.exc import SQLAlchemyError

last_welcome = 0
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def battle_time():
    """ Определяет, наступило ли время битвы """
    now = datetime.now().time()
    if now.hour % 4 == 3 and now.minute >= 57:
        return True
    return False


def del_msg(bot, job):
    bot.delete_message(job.context[0], job.context[1])


@run_async
@user_allowed
def manage_all(bot: Bot, update: Update, session, chat_data, job_queue):
    add_user(update.message.from_user, session)
    if update.message.chat.type in ['group', 'supergroup', 'channel']:
        squad = session.query(Squad).filter_by(
            chat_id=update.message.chat.id).first()
        admin = session.query(Admin).filter(
            Admin.user_id == update.message.from_user.id and
            Admin.admin_group in [update.message.chat.id, 0]).first()

        if squad is not None and admin is None and battle_time():
            bot.delete_message(update.message.chat.id,
                               update.message.message_id)

        if not update.message.text:
            return

        text = update.message.text.lower()

        if text.startswith('приветствие:'):
            set_welcome(bot, update)
        elif text == 'помощь':
            help_msg(bot, update)
        elif text == 'покажи приветствие':
            show_welcome(bot, update)
        elif text == 'включи приветствие':
            enable_welcome(bot, update)
        elif text == 'выключи приветствие':
            disable_welcome(bot, update)
        elif text.startswith('затриггерь:'):
            set_trigger(bot, update)
        elif text.startswith('разтриггерь:'):
            del_trigger(bot, update)
        elif text == 'список триггеров':
            list_triggers(bot, update)
        elif text == 'список админов':
            list_admins(bot, update)
        elif text == 'пинг':
            ping(bot, update)
        elif text == 'статистика за день':
            day_activity(bot, update)
        elif text == 'cтатистика за неделю':
            week_activity(bot, update)
        elif text == 'cтатистика за бой':
            battle_activity(bot, update)
        elif text == 'разрешить триггерить всем':
            enable_trigger_all(bot, update)
        elif text == 'запретить триггерить всем':
            disable_trigger_all(bot, update)
        elif text in ['админы', 'офицер']:
            admins_for_users(bot, update)
        elif text == 'пинят все':
            pin_all(bot, update)
        elif text == 'хорош пинить':
            not_pin_all(bot, update)
        elif text in ['бандит', 'краб']:
            boss_leader(bot, update)
        elif text in ['жало', 'королева роя']:
            boss_zhalo(bot, update)
        elif text in ['циклоп', 'борода']:
            boss_monoeye(bot, update)
        elif text in ['гидра', 'лич']:
            boss_hydra(bot, update)
        elif text == 'открыть набор':
            open_hiring(bot, update)
        elif text == 'закрыть набор':
            close_hiring(bot, update)
        elif update.message.text:
            trigger_show(bot, update)
        elif update.message.reply_to_message is not None:
            if text == 'пин':
                pin(bot, update)
            elif text == 'сайлентпин':
                silent_pin(bot, update)
            elif text == 'удоли':
                delete_msg(bot, update)
            elif text == 'свали':
                delete_user(bot, update)

        elif 'твои результаты в бою:' in text:
            if update.message.forward_from.id == 265204902:
                job_queue.run_once(del_msg, 2, (update.message.chat.id,
                                                update.message.message_id))

    elif update.message.chat.type == 'private':
        if update.message.text:
            text = update.message.text.lower()

            if text == 'статус':
                send_status(bot, update)
            elif text == 'хочу в отряд':
                squad_request(bot, update)
            elif text == 'заявки в отряд':
                list_squad_requests(bot, update)
            elif text in ['приказы', 'пин']:
                orders(bot, update, chat_data)
            elif text in ['список отряда', 'список']:
                Thread(target=squad_list, args=(bot, update)).start()
            elif text == 'группы':
                group_list(bot, update)
            elif text == 'чистка отряда':
                remove_from_squad(bot, update)
            elif 'wait_group_name' in chat_data and chat_data['wait_group_name']:
                add_group(bot, update, chat_data)

            elif update.message.forward_from:
                from_id = update.message.forward_from.id

                if from_id == 265204902:
                    if text.startswith('📦содержимое склада'):
                        stock_compare(bot, update, chat_data)
                    elif re.search(PROFILE, text) or re.search(HERO, text):
                        char_update(bot, update)

                elif from_id == 278525885:
                    if '📦твой склад с материалами:' in text:
                        trade_compare(bot, update, chat_data)
        else:
            order(bot, update, chat_data)


@run_async
def ready_to_battle(bot: Bot):
    session = Session()
    try:
        group = session.query(Squad).all()
        for item in group:
            new_order = Order()
            new_order.text = 'К битве готовсь!'
            new_order.chat_id = item.chat_id
            new_order.date = datetime.now()
            new_order.confirmed_msg = 0
            session.add(new_order)
            session.commit()

            callback_data = json.dumps(
                {'t': QueryType.OrderOk.value, 'id': new_order.id})
            markup = InlineKeyboardMarkup([
                [InlineKeyboardButton('ГРАБЬНАСИЛУЙУБИВАЙ!',
                                      callback_data=callback_data)]])

            msg = send_order(bot, new_order.text, 0, new_order.chat_id, markup)

            try:
                msg = msg.result().result()
                bot.request.post(bot.base_url + '/pinChatMessage',
                                 {'chat_id': new_order.chat_id,
                                  'message_id': msg.message_id,
                                  'disable_notification': False})

            except TelegramError as err:
                bot.logger(err.message)

    except SQLAlchemyError as err:
        bot.logger(str(err))
        Session.rollback()


@run_async
def ready_to_battle_result(bot: Bot):
    session = Session()
    try:
        group = session.query(Squad).all()
        full_attack = 0
        full_defence = 0
        full_text = ''
        full_count = 0

        for item in group:
            ready_order = session.query(Order).filter_by(
                chat_id=item.chat_id,
                text='К битве готовсь!').order_by(Order.date.desc()).first()

            if ready_order is not None:
                attack = 0
                defence = 0
                for clear in ready_order.cleared:
                    if clear.user.character:
                        attack += clear.user.character.attack
                        defence += clear.user.character.defence

                text = MSG_SQUAD_READY.format(len(ready_order.cleared),
                                              item.squad_name,
                                              attack,
                                              defence)

                send_async(bot,
                           chat_id=item.chat_id,
                           text=text,
                           parse_mode=ParseMode.HTML)

                full_attack += attack
                full_defence += defence
                full_count += len(ready_order.cleared)
                full_text += MSG_FULL_TEXT_LINE.format(item.squad_name,
                                                       len(ready_order.cleared),
                                                       attack,
                                                       defence)

        full_text += MSG_FULL_TEXT_TOTAL.format(full_count,
                                                full_attack,
                                                full_defence)

        send_async(bot,
                   chat_id=GOVERNMENT_CHAT,
                   text=full_text,
                   parse_mode=ParseMode.HTML)

    except SQLAlchemyError as err:
        bot.logger(str(err))
        Session.rollback()


def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    disp = updater.dispatcher

    # on different commands - answer in Telegram
    disp.add_handler(CommandHandler("start", start))
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

    disp.add_handler(CommandHandler("add_squad", add_squad))
    disp.add_handler(CommandHandler("del_squad", del_squad))
    disp.add_handler(CommandHandler("enable_thorns", enable_thorns))
    disp.add_handler(CommandHandler("disable_thorns", disable_thorns))
    disp.add_handler(CommandHandler("set_squad_name", set_squad_name))
    disp.add_handler(CommandHandler("set_invite_link", set_invite_link))
    disp.add_handler(CommandHandler("find", find_by_username))
    disp.add_handler(CommandHandler("add", add_to_squad))

    disp.add_handler(CallbackQueryHandler(callback_query, pass_chat_data=True))

    # on noncommand i.e message - echo the message on Telegram
    disp.add_handler(MessageHandler(Filters.status_update, welcome))
    # disp.add_handler(MessageHandler(
    # Filters.text, manage_text, pass_chat_data=True))
    disp.add_handler(MessageHandler(
        Filters.all, manage_all, pass_chat_data=True, pass_job_queue=True))

    # log all errors
    disp.add_error_handler(error)

    updater.job_queue.run_daily(ready_to_battle, time(hour=7, minute=50))
    updater.job_queue.run_daily(ready_to_battle_result,
                                time(hour=7, minute=55))
    updater.job_queue.run_daily(ready_to_battle, time(hour=11, minute=50))
    updater.job_queue.run_daily(ready_to_battle_result,
                                time(hour=11, minute=55))
    updater.job_queue.run_daily(ready_to_battle, time(hour=15, minute=50))
    updater.job_queue.run_daily(ready_to_battle_result,
                                time(hour=15, minute=55))
    updater.job_queue.run_daily(ready_to_battle, time(hour=19, minute=50))
    updater.job_queue.run_daily(ready_to_battle_result,
                                time(hour=19, minute=55))
    updater.job_queue.run_daily(ready_to_battle, time(hour=23, minute=50))
    updater.job_queue.run_daily(ready_to_battle_result,
                                time(hour=23, minute=55))

    # Start the Bot
    updater.start_polling()
    # app.run(port=API_PORT)
    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
