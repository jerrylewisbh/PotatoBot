# -*- coding: utf-8 -*-
import logging
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from core.functions.orders import order, orders
from core.functions.admins import list_admins, admins_for_users, set_admin, del_admin
from core.functions.common import help_msg, ping, start, error, kick, admin_panel, stock_compare, trade_compare
from core.functions.inline_keyboard_handling import callback_query, send_status
from core.functions.triggers import set_trigger, add_trigger, del_trigger, list_triggers, enable_trigger_all, \
    disable_trigger_all, trigger_show
from core.functions.welcome import welcome, set_welcome, show_welcome, enable_welcome, disable_welcome
from core.functions.order_groups import group_list, add_group
from core.utils import add_user
from config import TOKEN
from core.regexp import profile
import re
from core.functions.profile import char_update, char_show
from core.functions.squad import add_squad, del_squad, set_invite_link, set_squad_name, enable_thorns, disable_thorns
from core.functions.activity import day_activity, week_activity, battle_activity

last_welcome = 0
logging.basicConfig(level=logging.WARNING,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def manage_text(bot: Bot, update: Update, chat_data):
    add_user(update.message.from_user)
    if update.message.chat.type in ['group', 'supergroup', 'channel']:
        if str(update.message.text).upper().startswith('Приветствие:'.upper()):
            set_welcome(bot, update)
        elif update.message.text.upper() == 'Помощь'.upper():
            help_msg(bot, update)
        elif update.message.text.upper() == 'Покажи приветствие'.upper():
            show_welcome(bot, update)
        elif update.message.text.upper() == 'Включи приветствие'.upper():
            enable_welcome(bot, update)
        elif update.message.text.upper() == 'Выключи приветствие'.upper():
            disable_welcome(bot, update)
        elif str(update.message.text).upper().startswith('Затриггерь:'.upper()):
            set_trigger(bot, update)
        elif str(update.message.text).upper().startswith('Разтриггерь:'.upper()):
            del_trigger(bot, update)
        elif update.message.text.upper() == 'Список триггеров'.upper():
            list_triggers(bot, update)
        elif update.message.text.upper() == 'Список админов'.upper():
            list_admins(bot, update)
        elif update.message.text.upper() == 'Пинг'.upper():
            ping(bot, update)
        elif update.message.text.upper() == 'Статистика за день'.upper():
            day_activity(bot, update)
        elif update.message.text.upper() == 'Статистика за неделю'.upper():
            week_activity(bot, update)
        elif update.message.text.upper() == 'Статистика за бой'.upper():
            battle_activity(bot, update)
        elif update.message.text.upper() == 'Разрешить триггерить всем'.upper():
            enable_trigger_all(bot, update)
        elif update.message.text.upper() == 'Запретить триггерить всем'.upper():
            disable_trigger_all(bot, update)
        elif update.message.text.upper() in ['Админы'.upper(), 'офицер'.upper()]:
            admins_for_users(bot, update)
        trigger_show(bot, update)
    elif update.message.chat.type == 'private':
        if update.message.text.upper() == 'Статус'.upper():
            send_status(bot, update)
        elif update.message.text.upper() in ['Приказы'.upper(), 'пин'.upper()]:
            orders(bot, update, chat_data)
        elif update.message.text.upper() == 'Группы'.upper():
            group_list(bot, update)
        elif update.message.forward_from and update.message.forward_from.id == 265204902 and \
                update.message.text.startswith('📦Содержимое склада'):
            stock_compare(bot, update, chat_data)
        elif update.message.forward_from and update.message.forward_from.id == 278525885 and \
                '📦Твой склад с материалами:' in update.message.text:
            trade_compare(bot, update, chat_data)
        elif 'wait_group_name' in chat_data and chat_data['wait_group_name']:
            add_group(bot, update, chat_data)
        elif update.message.forward_from and update.message.forward_from.id == 265204902 and \
                re.search(profile, update.message.text):
            char_update(bot, update)
        else:
            order(bot, update, chat_data)


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
    dp.add_handler(CommandHandler("del_admin", del_admin))
    dp.add_handler(CommandHandler("list_admins", list_admins))
    dp.add_handler(CommandHandler("kick", kick))
    dp.add_handler(CommandHandler("enable_trigger", enable_trigger_all))
    dp.add_handler(CommandHandler("disable_trigger", disable_trigger_all))
    dp.add_handler(CommandHandler("me", char_show))

    dp.add_handler(CommandHandler("add_squad", add_squad))
    dp.add_handler(CommandHandler("del_squad", del_squad))
    dp.add_handler(CommandHandler("enable_thorns", enable_thorns))
    dp.add_handler(CommandHandler("disable_thorns", disable_thorns))
    dp.add_handler(CommandHandler("set_squad_name", set_squad_name))
    dp.add_handler(CommandHandler("set_invite_link", set_invite_link))

    dp.add_handler(CallbackQueryHandler(callback_query, pass_chat_data=True))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.status_update, welcome))
    dp.add_handler(MessageHandler(Filters.text, manage_text, pass_chat_data=True))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
