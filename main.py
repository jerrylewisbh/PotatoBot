# -*- coding: utf-8 -*-
import logging
from threading import Thread

from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram.ext.dispatcher import run_async

from core.functions.bosses import boss_leader, boss_zhalo, boss_monoeye, boss_hydra
from core.functions.orders import order, orders
from core.functions.admins import list_admins, admins_for_users, set_admin, del_admin, set_global_admin, \
    set_super_admin, del_global_admin
from core.functions.common import help_msg, ping, start, error, kick, admin_panel, stock_compare, trade_compare, \
    check_bot_in_chats, delete_msg
from core.functions.inline_keyboard_handling import callback_query, send_status, generate_ok_markup, send_order
from core.functions.pin import pin, not_pin_all, pin_all, silent_pin
from core.functions.triggers import set_trigger, add_trigger, del_trigger, list_triggers, enable_trigger_all, \
    disable_trigger_all, trigger_show
from core.functions.welcome import welcome, set_welcome, show_welcome, enable_welcome, disable_welcome
from core.functions.order_groups import group_list, add_group
from core.types import data_update, Session, Group, Order, Squad, Admin
from core.utils import add_user, send_async
from config import TOKEN
from core.regexp import profile, hero
import re
from core.functions.profile import char_update, char_show, find_by_username
from core.functions.squad import add_squad, del_squad, set_invite_link, set_squad_name, enable_thorns, disable_thorns, \
    squad_list, squad_request, list_squad_requests, open_hiring, close_hiring
from core.functions.activity import day_activity, week_activity, battle_activity
from datetime import datetime, time

last_welcome = 0
logging.basicConfig(level=logging.WARNING,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def battle_time():
    now = datetime.now().time()
    _BATTLE_TIME = [[time(7, 57), time(8, 0)],
                    [time(11, 57), time(12, 0)],
                    [time(15, 57), time(16, 0)],
                    [time(19, 57), time(20, 0)],
                    [time(23, 57), time(0, 0)]]
    for time_start, time_end in _BATTLE_TIME:
        if time_start <= time_end and time_start <= now <= time_end or \
                        not time_start <= time_end and (time_start <= now or now <= time_end):
            return True
    return False


@data_update
@run_async
def manage_all(bot: Bot, update: Update, chat_data):
    add_user(update.message.from_user)
    if update.message.chat.type in ['group', 'supergroup', 'channel']:
        session = Session()
        squad = session.query(Squad).filter_by(chat_id=update.message.chat.id).first()
        admin = session.query(Admin).filter(Admin.user_id == update.message.from_user.id and
                                            Admin.admin_group in [update.message.chat.id, 0]).first()
        if squad is not None and admin is None and battle_time():
            bot.delete_message(update.message.chat.id, update.message.message_id)
        if update.message.text and update.message.text.upper().startswith('Приветствие:'.upper()):
            set_welcome(bot, update)
        elif update.message.text and update.message.text.upper() == 'Помощь'.upper():
            help_msg(bot, update)
        elif update.message.text and update.message.text.upper() == 'Покажи приветствие'.upper():
            show_welcome(bot, update)
        elif update.message.text and update.message.text.upper() == 'Включи приветствие'.upper():
            enable_welcome(bot, update)
        elif update.message.text and update.message.text.upper() == 'Выключи приветствие'.upper():
            disable_welcome(bot, update)
        elif update.message.text and update.message.text.upper().startswith('Затриггерь:'.upper()):
            set_trigger(bot, update)
        elif update.message.text and update.message.text.upper().startswith('Разтриггерь:'.upper()):
            del_trigger(bot, update)
        elif update.message.text and update.message.text.upper() == 'Список триггеров'.upper():
            list_triggers(bot, update)
        elif update.message.text and update.message.text.upper() == 'Список админов'.upper():
            list_admins(bot, update)
        elif update.message.text and update.message.text.upper() == 'Пинг'.upper():
            ping(bot, update)
        elif update.message.text and update.message.text.upper() == 'Статистика за день'.upper():
            day_activity(bot, update)
        elif update.message.text and update.message.text.upper() == 'Статистика за неделю'.upper():
            week_activity(bot, update)
        elif update.message.text and update.message.text.upper() == 'Статистика за бой'.upper():
            battle_activity(bot, update)
        elif update.message.text and update.message.text.upper() == 'Разрешить триггерить всем'.upper():
            enable_trigger_all(bot, update)
        elif update.message.text and update.message.text.upper() == 'Запретить триггерить всем'.upper():
            disable_trigger_all(bot, update)
        elif update.message.text and update.message.text.upper() in ['Админы'.upper(), 'офицер'.upper()]:
            admins_for_users(bot, update)
        elif update.message.text and update.message.text.upper() == 'Пинят все'.upper():
            pin_all(bot, update)
        elif update.message.text and update.message.text.upper() == 'Хорош пинить'.upper():
            not_pin_all(bot, update)
        elif update.message.text and update.message.text.upper() == 'Пин'.upper() and update.message.reply_to_message is not None:
            pin(bot, update)
        elif update.message.text and update.message.text.upper() == 'сайлентпин'.upper() and update.message.reply_to_message is not None:
            silent_pin(bot, update)
        elif update.message.text and update.message.text.upper() == 'бандит'.upper():
            boss_leader(bot, update)
        elif update.message.text and update.message.text.upper() == 'жало'.upper():
            boss_zhalo(bot, update)
        elif update.message.text and update.message.text.upper() == 'циклоп'.upper():
            boss_monoeye(bot, update)
        elif update.message.text and update.message.text.upper() == 'гидра'.upper():
            boss_hydra(bot, update)
        elif update.message.text and update.message.text.upper() == 'открыть набор'.upper():
            open_hiring(bot, update)
        elif update.message.text and update.message.text.upper() == 'закрыть набор'.upper():
            close_hiring(bot, update)
        elif update.message.text and update.message.text.upper() == 'удоли'.upper() and update.message.reply_to_message is not None:
            delete_msg(bot, update)
        elif update.message.text:
            trigger_show(bot, update)
    elif update.message.chat.type == 'private':
        if update.message.text and update.message.text.upper() == 'Статус'.upper():
            send_status(bot, update)
        elif update.message.text and update.message.text.upper() == 'хочу в отряд'.upper():
            squad_request(bot, update)
        elif update.message.text and update.message.text.upper() == 'заявки в отряд'.upper():
            list_squad_requests(bot, update)
        elif update.message.text and update.message.text.upper() in ['Приказы'.upper(), 'пин'.upper()]:
            orders(bot, update, chat_data)
        elif update.message.text and update.message.text.upper() in ['список отряда'.upper(), 'список'.upper()]:
            Thread(target=squad_list, args=(bot, update)).start()
        elif update.message.text and update.message.text.upper() == 'Группы'.upper():
            group_list(bot, update)
        elif update.message.forward_from and update.message.forward_from.id == 265204902 and \
                update.message.text.startswith('📦Содержимое склада'):
            stock_compare(bot, update, chat_data)
        elif update.message.forward_from and update.message.forward_from.id == 278525885 and \
                        '📦Твой склад с материалами:' in update.message.text:
            trade_compare(bot, update, chat_data)
        elif 'wait_group_name' in chat_data and chat_data['wait_group_name']:
            add_group(bot, update, chat_data)
        elif update.message.text and update.message.forward_from and update.message.forward_from.id == 265204902 and \
                (re.search(profile, update.message.text) or re.search(hero, update.message.text)):
            char_update(bot, update)
        else:
            order(bot, update, chat_data)


@run_async
def ready_to_battle(bot, job_queue):
    session = Session()
    group = session.query(Squad).all()
    for item in group:
        order = Order()
        order.text = 'К битве готовсь!'
        order.chat_id = item.chat_id
        order.date = datetime.now()
        order.confirmed_msg = 0
        session.add(order)
        session.commit()
        markup = generate_ok_markup(order.id, 0)
        msg = send_order(bot, order.text, 0, order.chat_id, markup)
        try:
            msg = msg.result().result()
            bot.request.post(bot.base_url + '/pinChatMessage',
                             {'chat_id': order.chat_id, 'message_id': msg.message_id,
                              'disable_notification': False})
        except Exception as e:
            print(e)


@run_async
def ready_to_battle_result(bot, job_queue):
    session = Session()
    group = session.query(Squad).all()
    full_attack = 0
    full_defence = 0
    full_text = ''
    for item in group:
        order = session.query(Order).filter_by(chat_id=item.chat_id, text='К битве готовсь!').order_by(Order.date.desc()).first()
        if order is not None:
            attack = 0
            defence = 0
            for clear in order.cleared:
                if clear.user.character:
                    attack += clear.user.character.attack
                    defence += clear.user.character.defence
            text = '{} бойцов отряда {} к битве готовы!\n{}⚔ {}🛡'.format(len(order.cleared),
                                                                          item.squad_name, attack, defence)
            send_async(bot, chat_id=item.chat_id, text=text)
            full_text += text + '\n'
            full_attack += attack
            full_defence += defence
    send_async(bot, chat_id=-1001139179731, text=full_text + 'Суммарная планируемая атака и защита на битву: {}⚔ {}🛡'
               .format(full_attack, full_defence))


def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("admin", admin_panel))
    dp.add_handler(CommandHandler("help", help_msg))
    dp.add_handler(CommandHandler("ping", ping))
    dp.add_handler(CommandHandler("set_trigger", set_trigger))
    dp.add_handler(CommandHandler("add_trigger", add_trigger))
    dp.add_handler(CommandHandler("del_trigger", del_trigger))
    dp.add_handler(CommandHandler("list_triggers", list_triggers))
    dp.add_handler(CommandHandler("set_welcome", set_welcome))
    dp.add_handler(CommandHandler("enable_welcome", enable_welcome))
    dp.add_handler(CommandHandler("disable_welcome", disable_welcome))
    dp.add_handler(CommandHandler("show_welcome", show_welcome))
    dp.add_handler(CommandHandler("add_admin", set_admin))
    dp.add_handler(CommandHandler("add_global_admin", set_global_admin))
    dp.add_handler(CommandHandler("del_global_admin", del_global_admin))
    dp.add_handler(CommandHandler("add_super_admin", set_super_admin))
    dp.add_handler(CommandHandler("del_admin", del_admin))
    dp.add_handler(CommandHandler("list_admins", list_admins))
    dp.add_handler(CommandHandler("kick", kick))
    dp.add_handler(CommandHandler("enable_trigger", enable_trigger_all))
    dp.add_handler(CommandHandler("disable_trigger", disable_trigger_all))
    dp.add_handler(CommandHandler("me", char_show))
    dp.add_handler(CommandHandler("check_bot_in_chats", check_bot_in_chats))

    dp.add_handler(CommandHandler("add_squad", add_squad))
    dp.add_handler(CommandHandler("del_squad", del_squad))
    dp.add_handler(CommandHandler("enable_thorns", enable_thorns))
    dp.add_handler(CommandHandler("disable_thorns", disable_thorns))
    dp.add_handler(CommandHandler("set_squad_name", set_squad_name))
    dp.add_handler(CommandHandler("set_invite_link", set_invite_link))
    dp.add_handler(CommandHandler("find", find_by_username))

    dp.add_handler(CallbackQueryHandler(callback_query, pass_chat_data=True))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.status_update, welcome))
    # dp.add_handler(MessageHandler(Filters.text, manage_text, pass_chat_data=True))
    dp.add_handler(MessageHandler(Filters.all, manage_all, pass_chat_data=True))

    # log all errors
    dp.add_error_handler(error)

    updater.job_queue.run_daily(ready_to_battle, time(hour=7, minute=50))
    updater.job_queue.run_daily(ready_to_battle_result, time(hour=7, minute=55))
    updater.job_queue.run_daily(ready_to_battle, time(hour=11, minute=50))
    updater.job_queue.run_daily(ready_to_battle_result, time(hour=11, minute=55))
    updater.job_queue.run_daily(ready_to_battle, time(hour=15, minute=50))
    updater.job_queue.run_daily(ready_to_battle_result, time(hour=15, minute=55))
    updater.job_queue.run_daily(ready_to_battle, time(hour=19, minute=50))
    updater.job_queue.run_daily(ready_to_battle_result, time(hour=19, minute=55))
    updater.job_queue.run_daily(ready_to_battle, time(hour=23, minute=50))
    updater.job_queue.run_daily(ready_to_battle_result, time(hour=23, minute=55))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
