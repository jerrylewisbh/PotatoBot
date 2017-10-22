# -*- coding: utf-8 -*-

from datetime import datetime, time, timedelta
import json
import logging
import re

from sqlalchemy import func, tuple_
from telegram import (
    Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
)
from telegram.ext import (
    Updater, CommandHandler, MessageHandler,
    Filters, CallbackQueryHandler
)
from telegram.ext.dispatcher import run_async
from telegram.error import TelegramError

from config import TOKEN, GOVERNMENT_CHAT, CASTLE
from core.commands import ADMIN_COMMAND_STATUS, ADMIN_COMMAND_RECRUIT, ADMIN_COMMAND_ORDER, ADMIN_COMMAND_SQUAD_LIST, \
    ADMIN_COMMAND_GROUPS, ADMIN_COMMAND_FIRE_UP, USER_COMMAND_ME, USER_COMMAND_BUILD, USER_COMMAND_CONTACTS, \
    USER_COMMAND_SQUAD, USER_COMMAND_STATISTICS, USER_COMMAND_TOP, USER_COMMAND_SQUAD_REQUEST, USER_COMMAND_BACK, \
    TOP_COMMAND_ATTACK, TOP_COMMAND_DEFENCE, TOP_COMMAND_EXP, STATISTICS_COMMAND_EXP, USER_COMMAND_SQUAD_LEAVE
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
    delete_msg, delete_user,
    user_panel)
from core.functions.inline_keyboard_handling import (
    callback_query, send_status, send_order, QueryType
)
from core.functions.order_groups import group_list, add_group
from core.functions.pin import pin, not_pin_all, pin_all, silent_pin
from core.functions.profile import char_update, char_show, find_by_username, report_received, build_report_received, \
    repair_report_received
from core.functions.squad import (
    add_squad, del_squad, set_invite_link, set_squad_name,
    enable_thorns, disable_thorns,
    squad_list, squad_request, list_squad_requests,
    open_hiring, close_hiring, remove_from_squad, add_to_squad,
    leave_squad, squad_about)
from core.functions.statistics import statistic_about, exp_statistic
from core.functions.top import top_about, attack_top, exp_top, def_top
from core.functions.triggers import (
    set_trigger, add_trigger, del_trigger, list_triggers, enable_trigger_all,
    disable_trigger_all, trigger_show,
    set_global_trigger, add_global_trigger, del_global_trigger
)
from core.functions.welcome import (
    welcome, set_welcome, show_welcome, enable_welcome, disable_welcome
)
from core.regexp import PROFILE, HERO, REPORT, BUILD_REPORT, REPAIR_REPORT
from core.texts import (
    MSG_SQUAD_READY, MSG_FULL_TEXT_LINE, MSG_FULL_TEXT_TOTAL,
    MSG_MAIN_INLINE_BATTLE, MSG_MAIN_READY_TO_BATTLE, MSG_IN_DEV, MSG_UPDATE_PROFILE, MSG_SQUAD_DELETE_OUTDATED)
from core.types import Session, Order, Squad, Admin, user_allowed, Character, SquadMember
from core.utils import add_user, send_async

from sqlalchemy.exc import SQLAlchemyError

# -----constants----
CWBOT_ID = 265204902
TRADEBOT_ID = 278525885
# -------------------

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
    try:
        bot.delete_message(job.context[0], job.context[1])
    except TelegramError:
        pass


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
        elif text == 'статистика за неделю':
            week_activity(bot, update)
        elif text == 'статистика за бой':
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
        elif update.message.reply_to_message is not None:
            if text == 'пин':
                pin(bot, update)
            elif text == 'сайлентпин':
                silent_pin(bot, update)
            elif text == 'удоли':
                delete_msg(bot, update)
            elif text == 'свали':
                delete_user(bot, update)
            else:
                trigger_show(bot, update)
        elif 'твои результаты в бою:' in text:
            if update.message.forward_from.id == CWBOT_ID:
                report_received(bot, update)
                job_queue.run_once(del_msg, 2, (update.message.chat.id,
                                                update.message.message_id))
        elif 'Ты вернулся со стройки:' in text:
            if update.message.forward_from.id == CWBOT_ID:
                build_report_received(bot, update)
        elif 'Здание отремонтировано:' in text:
            if update.message.forward_from.id == CWBOT_ID:
                repair_report_received(bot, update)
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

            if text == ADMIN_COMMAND_STATUS.lower():
                send_status(bot, update)
            elif text == USER_COMMAND_BACK.lower():
                user_panel(bot, update)
            elif text == USER_COMMAND_SQUAD_REQUEST.lower():
                squad_request(bot, update)
            elif text == ADMIN_COMMAND_RECRUIT.lower():
                list_squad_requests(bot, update)
            elif text == ADMIN_COMMAND_ORDER.lower():
                orders(bot, update, chat_data)
            elif text == ADMIN_COMMAND_SQUAD_LIST.lower():
                squad_list(bot, update)
            elif text == ADMIN_COMMAND_GROUPS.lower():
                group_list(bot, update)
            elif text == ADMIN_COMMAND_FIRE_UP.lower():
                remove_from_squad(bot, update)
            elif text == USER_COMMAND_ME.lower():
                char_show(bot, update)
            elif text == USER_COMMAND_TOP.lower():
                top_about(bot, update)
            elif text == TOP_COMMAND_ATTACK.lower():
                attack_top(bot, update)
            elif text == TOP_COMMAND_DEFENCE.lower():
                def_top(bot, update)
            elif text == TOP_COMMAND_EXP.lower():
                exp_top(bot, update)
            elif text == USER_COMMAND_BUILD.lower():
                send_async(bot,
                           chat_id=update.message.chat.id,
                           text=MSG_IN_DEV,
                           parse_mode=ParseMode.HTML)
            elif text == USER_COMMAND_STATISTICS.lower():
                statistic_about(bot, update)
            elif text == STATISTICS_COMMAND_EXP.lower():
                exp_statistic(bot, update)
            elif text == USER_COMMAND_SQUAD.lower():
                squad_about(bot, update)
            elif text == USER_COMMAND_SQUAD_LEAVE.lower():
                leave_squad(bot, update)
            elif text == USER_COMMAND_CONTACTS.lower():
                send_async(bot,
                           chat_id=update.message.chat.id,
                           text=MSG_IN_DEV,
                           parse_mode=ParseMode.HTML)
            elif 'wait_group_name' in chat_data and chat_data['wait_group_name']:
                add_group(bot, update, chat_data)

            elif update.message.forward_from:
                from_id = update.message.forward_from.id

                if from_id == CWBOT_ID:
                    if text.startswith('📦содержимое склада'):
                        stock_compare(bot, update, chat_data)
                    elif re.search(PROFILE, update.message.text) or re.search(HERO, update.message.text):
                        char_update(bot, update)
                    elif re.search(REPORT, update.message.text):
                        report_received(bot, update)
                    elif re.search(BUILD_REPORT, update.message.text):
                        build_report_received(bot, update)
                    elif re.search(REPAIR_REPORT, update.message.text):
                        repair_report_received(bot, update)
                elif from_id == TRADEBOT_ID:
                    if '📦твой склад с материалами:' in text:
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
            new_order = Order()
            new_order.text = MSG_MAIN_READY_TO_BATTLE
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

            msg = send_order(bot, new_order.text, 0, new_order.chat_id, markup)

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
def ready_to_battle_result(bot: Bot, job_queue):
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
                text=MSG_MAIN_READY_TO_BATTLE).order_by(Order.date.desc()).first()

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
                                                     datetime.now() - timedelta(days=3) > Character.date
                                                     > datetime.now() - timedelta(days=14))
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
                                                     Character.date < datetime.now() - timedelta(days=14)).all()
        members = session.query(SquadMember).filter(SquadMember.user_id in
                                                    [character.user_id for character in characters]).all()
        for member in members:
            session.delete(member)
            send_async(bot,
                       chat_id=member.user_id,
                       text=MSG_SQUAD_DELETE_OUTDATED,
                       parse_mode=ParseMode.HTML)
    except SQLAlchemyError as err:
        bot.logger.error(str(err))
        Session.rollback()


def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    disp = updater.dispatcher

    # on different commands - answer in Telegram
    disp.add_handler(CommandHandler("start", user_panel))
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
    updater.job_queue.run_daily(fresh_profiles,
                                time(hour=7, minute=40))
    updater.job_queue.run_daily(fresh_profiles,
                                time(hour=11, minute=40))
    updater.job_queue.run_daily(fresh_profiles,
                                time(hour=15, minute=40))
    updater.job_queue.run_daily(fresh_profiles,
                                time(hour=19, minute=40))
    updater.job_queue.run_daily(fresh_profiles,
                                time(hour=23, minute=40))

    # Start the Bot
    updater.start_polling()
    # app.run(port=API_PORT)
    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
