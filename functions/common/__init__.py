import logging
from datetime import datetime
from enum import Enum

import redis
from sqlalchemy import func
from telegram import Bot, ParseMode, Update, TelegramError

from config import CWBOT_ID, REDIS_SERVER, REDIS_PORT
from core.decorators import command_handler
from core.state import GameState, get_game_state
from core.texts import *
from core.texts import MSG_ALREADY_BANNED, MSG_NO_REASON, MSG_USER_BANNED, MSG_YOU_BANNED, MSG_BAN_COMPLETE, \
    MSG_USER_UNKNOWN, MSG_REASON_TRAITOR, MSG_YOU_UNBANNED, MSG_USER_UNBANNED, MSG_USER_NOT_BANNED
from core.types import Admin, AdminType, Stock, User, Session, Item, Ban, SquadMember, Squad, UserExchangeOrder, \
    UserStockHideSetting
from core.utils import send_async
from functions.reply_markup import (generate_admin_markup)
from functions.triggers import trigger_decorator

Session()


class StockType(Enum):
    Stock = 0
    TradeBot = 1


def error(bot: Bot, update, error, **kwargs):
    """ Error handling """
    logging.error("An error (%s) occurred: %s", (type(error), error.message))


@command_handler(
    min_permission=AdminType.GROUP,
    allow_private=True
)
def admin_panel(bot: Bot, update: Update, user: User):
    if update.message.chat.type == 'private':
        admin = Session.query(Admin).filter_by(user_id=update.message.from_user.id).all()
        full_adm = False
        for adm in admin:
            if adm.admin_type <= AdminType.FULL.value:
                full_adm = True
        send_async(bot, chat_id=update.message.chat.id, text=MSG_ADMIN_WELCOME,
                   reply_markup=generate_admin_markup(full_adm))


@command_handler(
    min_permission=AdminType.NOT_ADMIN,
    allow_private=False,
    allow_group=True
)
def kick(bot: Bot, update: Update, user: User):
    bot.leave_chat(update.message.chat.id)


@command_handler()
def help_msg(bot: Bot, update, user: User):
    admin_user = Session.query(Admin).filter_by(user_id=update.message.from_user.id).all()
    global_adm = False
    for adm in admin_user:
        if adm.admin_type <= AdminType.FULL.value:
            global_adm = True
            break
    if global_adm:
        send_async(bot, chat_id=update.message.chat.id, text=MSG_HELP_GLOBAL_ADMIN)
    elif len(admin_user) != 0:
        send_async(bot, chat_id=update.message.chat.id, text=MSG_HELP_GROUP_ADMIN)
    else:
        send_async(bot, chat_id=update.message.chat.id, text=MSG_HELP_USER)


@command_handler(
    min_permission=AdminType.GROUP,
    allow_private=True,
    allow_group=True
)
def ping(bot: Bot, update: Update, user: User):
    send_async(bot, chat_id=update.message.chat.id, text=MSG_PING.format(update.message.from_user.username))


def get_diff(dict_one, dict_two):
    resource_diff_add = {}
    resource_diff_del = {}
    for key, val in dict_one.items():
        if key in dict_two:
            diff_count = dict_one[key] - dict_two[key]
            if diff_count > 0:
                resource_diff_add[key] = diff_count
            elif diff_count < 0:
                resource_diff_del[key] = diff_count
        else:
            resource_diff_add[key] = val
    for key, val in dict_two.items():
        if key not in dict_one:
            resource_diff_del[key] = -val
    resource_diff_add = sorted(resource_diff_add.items(), key=lambda x: x[0])
    resource_diff_del = sorted(resource_diff_del.items(), key=lambda x: x[0])
    return resource_diff_add, resource_diff_del


def get_weight_multiplier(item_name):
    item = __get_item(item_name)
    if not item:
        logging.warning("Could not find item %s in database! Guessing weight = 1", item_name)
        return 1

    return item.weight


def get_weighted_diff(dict_one, dict_two):
    """ Same as get_diff but accounts for item weight """
    resource_diff_add = {}
    resource_diff_del = {}

    for key, val in dict_one.items():
        weight_multiplier = get_weight_multiplier(key)
        if key in dict_two:
            diff_count = dict_one[key] - dict_two[key]
            if diff_count > 0:
                resource_diff_add[key] = diff_count * weight_multiplier
            elif diff_count < 0:
                resource_diff_del[key] = diff_count * weight_multiplier
        else:
            resource_diff_add[key] = val * weight_multiplier
    for key, val in dict_two.items():
        weight_multiplier = get_weight_multiplier(key)
        if key not in dict_one:
            resource_diff_del[key] = -val * weight_multiplier
    resource_diff_add = sorted(resource_diff_add.items(), key=lambda x: x[0])
    resource_diff_del = sorted(resource_diff_del.items(), key=lambda x: x[0])
    return resource_diff_add, resource_diff_del


def stock_split(old_stock, new_stock):
    """ Split stock text... """
    resources_old = {}
    resources_new = {}
    strings = old_stock.splitlines()
    for string in strings[1:]:
        resource = string.split(' (')
        resource[1] = resource[1][:-1]
        resources_old[resource[0]] = int(resource[1])
    strings = new_stock.splitlines()
    for string in strings[1:]:
        resource = string.split(' (')
        resource[1] = resource[1][:-1]
        resources_new[resource[0]] = int(resource[1])

    return (resources_old, resources_new)


def __get_item(item_name):
    return Session.query(Item).filter(func.lower(Item.name) == item_name.lower()).first()


def stock_compare_text(old_stock, new_stock):
    """ Compare stock... """
    if old_stock:
        resources_old, resources_new = stock_split(old_stock, new_stock)
        resource_diff_add, resource_diff_del = get_diff(resources_new, resources_old)
        msg = MSG_STOCK_COMPARE_HARVESTED
        hits = 0
        running_total = 0
        if len(resource_diff_add):
            for key, val in resource_diff_add:
                item = __get_item(key)
                if item and item.pillagable:
                    gain_worth = __get_item_worth(item.name)
                    hits += 1
                    if item.tradable:
                        running_total += (gain_worth * val)
                        msg += MSG_STOCK_COMPARE_W_PRICE.format(key, gain_worth, val, (gain_worth * val))
                    else:
                        msg += MSG_STOCK_COMPARE_WO_PRICE.format(key, val)
        if hits == 0:
            msg += MSG_EMPTY

        msg += MSG_STOCK_COMPARE_LOST
        hits = 0
        if len(resource_diff_del):
            for key, val in resource_diff_del:
                item = __get_item(key)
                if item and item.pillagable:
                    loss_worth = __get_item_worth(item.name)
                    hits += 1
                    if item.tradable:
                        running_total -= (loss_worth * val)
                        msg += MSG_STOCK_COMPARE_W_PRICE.format(key, loss_worth, val, (loss_worth * val))
                    else:
                        msg += MSG_STOCK_COMPARE_WO_PRICE.format(key, val)
        if hits == 0:
            msg += MSG_EMPTY


        if running_total != 0:
            msg += MSG_STOCK_OVERALL_CHANGE.format(running_total)

        return msg

    return None


def stock_compare(user_id, new_stock_text):
    """ Save new stock into database and compare it with the newest already saved.
    """

    old_stock = Session.query(Stock).filter_by(user_id=user_id,
                                               stock_type=StockType.Stock.value).order_by(Stock.date.desc()).first()
    new_stock = Stock()
    new_stock.stock = new_stock_text
    new_stock.stock_type = StockType.Stock.value
    new_stock.user_id = user_id
    new_stock.date = datetime.now()
    Session.add(new_stock)
    Session.commit()

    if old_stock:
        return stock_compare_text(old_stock.stock, new_stock.stock)

    return None


@command_handler(
    forward_from=CWBOT_ID
)
def stock_compare_forwarded(bot: Bot, update: Update, user: User, chat_data: dict):
    # If user-stock is automatically updated via API do not allow reports during SILENCE
    user = Session.query(User).filter_by(id=update.message.from_user.id).first()

    state = get_game_state()
    if user.is_api_stock_allowed and user.setting_automated_report and GameState.NO_REPORTS in state:
        text = MSG_NO_REPORT_PHASE_BEFORE_BATTLE if GameState.NIGHT in state else MSG_NO_REPORT_PHASE_AFTER_BATTLE
        send_async(
            bot,
            chat_id=update.message.chat.id,
            text=text,
            parse_mode=ParseMode.HTML)
        return

    cmp_result = stock_compare(update.message.from_user.id, update.message.text)
    if cmp_result:
        send_async(bot, chat_id=update.message.chat.id, text=cmp_result, parse_mode=ParseMode.HTML)
    else:
        send_async(bot, chat_id=update.message.chat.id, text=MSG_STOCK_COMPARE_WAIT, parse_mode=ParseMode.HTML)


@command_handler(
    min_permission=AdminType.GROUP,
    allow_private=False,
    allow_group=True
)
def delete_msg(bot: Bot, update: Update):
    bot.delete_message(update.message.reply_to_message.chat_id, update.message.reply_to_message.message_id)
    bot.delete_message(update.message.reply_to_message.chat_id, update.message.message_id)


@command_handler(
    min_permission=AdminType.FULL,
    allow_private=False,
    allow_group=True
)
def delete_user(bot: Bot, update: Update, user: User):
    bot.kickChatMember(update.message.reply_to_message.chat_id, update.message.reply_to_message.from_user.id)
    bot.unbanChatMember(update.message.reply_to_message.chat_id, update.message.reply_to_message.from_user.id)


@command_handler(
    min_permission=AdminType.FULL,
)
def ban(bot: Bot, update: Update, user: User):
    username, reason = update.message.text.split(' ', 2)[1:]
    username = username.replace('@', '')
    user = Session.query(User).filter_by(username=username).first()
    if user:
        banned = Session.query(Ban).filter_by(user_id=user.id).first()
        if banned:
            send_async(bot, chat_id=update.message.chat.id,
                       text=MSG_ALREADY_BANNED.format(banned.to_date, banned.reason))
        else:
            banned = Ban()
            banned.user_id = user.id
            banned.from_date = datetime.now()
            banned.to_date = datetime.max
            banned.reason = reason or MSG_NO_REASON
            member = Session.query(SquadMember).filter_by(user_id=user.id).first()
            if member:
                Session.delete(member)
            admins = Session.query(Admin).filter_by(user_id=user.id).all()
            for admin in admins:
                Session.delete(admin)
            Session.add(banned)
            Session.commit()
            squads = Session.query(Squad).all()
            for squad in squads:
                send_async(bot, chat_id=squad.chat_id, text=MSG_USER_BANNED.format('@' + username))
            send_async(bot, chat_id=user.id, text=MSG_YOU_BANNED.format(banned.reason))
            send_async(bot, chat_id=update.message.chat.id, text=MSG_BAN_COMPLETE)
    else:
        send_async(bot, chat_id=update.message.chat.id, text=MSG_USER_UNKNOWN)


def ban_traitor(bot: Bot, update: Update, user: User):
    user = Session.query(User).filter_by(id=user.id).first()
    if user:
        logging.warning("Banning %s", user.id)
        banned = Ban()
        banned.user_id = user.id
        banned.from_date = datetime.now()
        banned.to_date = datetime.max
        banned.reason = MSG_REASON_TRAITOR
        member = Session.query(SquadMember).filter_by(user_id=user.id).first()
        if member:
            Session.delete(member)
            try:
                bot.restrictChatMember(member.squad_id, member.user_id)
                bot.kickChatMember(member.squad_id, member.user_id)
            except TelegramError as err:
                bot.logger.error(err.message)

        # Disable API settings but keep his api credentials until user revokes them herself/himself.
        user.setting_automated_sniping = False
        user.setting_automated_hiding = False
        user.setting_automated_report = False
        user.setting_automated_deal_report = False

        # Remove all his settings...
        Session.query(UserExchangeOrder).filter(UserExchangeOrder.user_id == user.id).delete()
        Session.query(UserStockHideSetting).filter(UserStockHideSetting.user_id == user.id).delete()

        admins = Session.query(Admin).filter_by(user_id=user.id).all()
        # for admin in admins:
        # Session.delete(admin)

        Session.add(banned)
        Session.add(user)
        Session.commit()
        squads = Session.query(Squad).all()

        #send_async(bot, chat_id=GOVERNMENT_CHAT, text=MSG_USER_BANNED_TRAITOR.format('@' + user.username))


@command_handler(
    min_permission=AdminType.FULL
)
def unban(bot: Bot, update: Update, user: User):
    username = update.message.text.split(' ', 1)[1]
    username = username.replace('@', '')
    user = Session.query(User).filter_by(username=username).first()
    if user:
        banned = Session.query(Ban).filter_by(user_id=user.id).first()
        if banned:
            Session.delete(banned)
            Session.commit()
            send_async(bot, chat_id=user.id, text=MSG_YOU_UNBANNED)
            send_async(bot, chat_id=update.message.chat.id, text=MSG_USER_UNBANNED.format('@' + user.username))
        else:
            send_async(bot, chat_id=update.message.chat.id, text=MSG_USER_NOT_BANNED)
    else:
        send_async(bot, chat_id=update.message.chat.id, text=MSG_USER_UNKNOWN)


def __get_item_worth(item_name):
    r = redis.StrictRedis(host=REDIS_SERVER, port=REDIS_PORT, db=0)
    item_prices = r.lrange(item_name, 0, -1)

    if item_prices:
        return int(min(item_prices))
    return None
