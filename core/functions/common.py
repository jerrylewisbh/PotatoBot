import logging
import uuid
from config import WEB_LINK
from datetime import datetime
from enum import Enum

from core.enums import HEAVY_ITEMS, STOCK_WHITELIST
from core.functions.reply_markup import (generate_admin_markup,
                                         generate_user_markup)
from core.functions.triggers import trigger_decorator
from core.state import GameState, get_game_state
from core.texts import *
from core.types import (Admin, AdminType, Auth, SquadMember, Stock, User,
                        admin_allowed, user_allowed, Session)
from core.utils import add_user, send_async
from telegram import Bot, ParseMode, Update

LOGGER = logging.getLogger(__name__)

session = Session()

class StockType(Enum):
    Stock = 0
    TradeBot = 1


def error(bot: Bot, update, error, **kwargs):
    """ Error handling """
    LOGGER.error("An error (%s) occurred: %s"
                 % (type(error), error.message))


@user_allowed
def start(bot: Bot, update: Update):
    add_user(update.message.from_user, session)
    if update.message.chat.type == 'private':
        send_async(bot, chat_id=update.message.chat.id, text=MSG_START_WELCOME, parse_mode=ParseMode.HTML)


@admin_allowed(adm_type=AdminType.GROUP)
def admin_panel(bot: Bot, update: Update):
    if update.message.chat.type == 'private':
        admin = session.query(Admin).filter_by(user_id=update.message.from_user.id).all()
        full_adm = False
        for adm in admin:
            if adm.admin_type <= AdminType.FULL.value:
                full_adm = True
        send_async(bot, chat_id=update.message.chat.id, text=MSG_ADMIN_WELCOME,
                   reply_markup=generate_admin_markup(full_adm))


@user_allowed
def user_panel(bot: Bot, update: Update):
    if update.message.chat.type == 'private':
        admin = session.query(Admin).filter_by(user_id=update.message.from_user.id).all()
        send_async(bot, chat_id=update.message.chat.id, text=MSG_START_WELCOME, parse_mode=ParseMode.HTML,
                   reply_markup=generate_user_markup(user_id=update.message.from_user.id))


@admin_allowed()
def kick(bot: Bot, update: Update):
    bot.leave_chat(update.message.chat.id)


@trigger_decorator
def help_msg(bot: Bot, update):
    admin_user = session.query(Admin).filter_by(user_id=update.message.from_user.id).all()
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


@admin_allowed(adm_type=AdminType.GROUP)
def ping(bot: Bot, update: Update):
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
    if item_name.lower() in HEAVY_ITEMS:
        return 2
    else:
        return 1


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


def stock_compare_text(old_stock, new_stock):
    """ Compare stock... """
    if old_stock:
        resources_old, resources_new = stock_split(old_stock, new_stock)
        resource_diff_add, resource_diff_del = get_diff(resources_new, resources_old)
        msg = MSG_STOCK_COMPARE_HARVESTED
        if len(resource_diff_add):
            for key, val in resource_diff_add:
                if key.lower() in STOCK_WHITELIST:
                    msg += MSG_STOCK_COMPARE_FORMAT.format(key, val)
        else:
            msg += MSG_EMPTY
        msg += MSG_STOCK_COMPARE_LOST
        if len(resource_diff_del):
            for key, val in resource_diff_del:
                if key.lower() in STOCK_WHITELIST:
                    msg += MSG_STOCK_COMPARE_FORMAT.format(key, val)
        else:
            msg += MSG_EMPTY
        return msg

    return None


def stock_compare(session, user_id, new_stock_text):
    """ Save new stock into database and compare it with the newest already saved.
    """

    old_stock = session.query(Stock).filter_by(user_id=user_id,
                                               stock_type=StockType.Stock.value).order_by(Stock.date.desc()).first()
    new_stock = Stock()
    new_stock.stock = new_stock_text
    new_stock.stock_type = StockType.Stock.value
    new_stock.user_id = user_id
    new_stock.date = datetime.now()
    session.add(new_stock)
    session.commit()

    if old_stock:
        return stock_compare_text(old_stock.stock, new_stock.stock)

    return None


@user_allowed(False)
def stock_compare_forwarded(bot: Bot, update: Update, session, chat_data: dict):
    # If user-stock is automatically updated via API do not allow reports during SILENCE
    user = session.query(User).filter_by(id=update.message.from_user.id).first()

    state = get_game_state()
    if user.is_api_stock_allowed and user.setting_automated_report and GameState.NO_REPORTS in state:
        text = MSG_NO_REPORT_PHASE_BEFORE_BATTLE if GameState.NIGHT in state else MSG_NO_REPORT_PHASE_AFTER_BATTLE
        send_async(
            bot,
            chat_id=update.message.chat.id,
            text=text,
            parse_mode=ParseMode.HTML)
        return

    cmp_result = stock_compare(session, update.message.from_user.id, update.message.text)
    if cmp_result:
        send_async(bot, chat_id=update.message.chat.id, text=cmp_result, parse_mode=ParseMode.HTML)
    else:
        send_async(bot, chat_id=update.message.chat.id, text=MSG_STOCK_COMPARE_WAIT, parse_mode=ParseMode.HTML)


@admin_allowed(adm_type=AdminType.GROUP)
def delete_msg(bot: Bot, update: Update):
    bot.delete_message(update.message.reply_to_message.chat_id, update.message.reply_to_message.message_id)
    bot.delete_message(update.message.reply_to_message.chat_id, update.message.message_id)


@admin_allowed()
def delete_user(bot: Bot, update: Update):
    bot.kickChatMember(update.message.reply_to_message.chat_id, update.message.reply_to_message.from_user.id)
    bot.unbanChatMember(update.message.reply_to_message.chat_id, update.message.reply_to_message.from_user.id)


@user_allowed(False)
def trade_compare(bot: Bot, update: Update, session, chat_data: dict):
    old_stock = session.query(Stock).filter_by(user_id=update.message.from_user.id,
                                               stock_type=StockType.TradeBot.value).order_by(Stock.date.desc()).first()
    new_stock = Stock()
    new_stock.stock = update.message.text
    new_stock.stock_type = StockType.TradeBot.value
    new_stock.user_id = update.message.from_user.id
    new_stock.date = datetime.now()
    session.add(new_stock)
    session.commit()
    if old_stock is not None:
        items_old = {}
        items_new = {}
        strings = old_stock.stock.splitlines()
        for string in strings:
            if string.startswith('/add_'):
                item = string.split('   ')[1]
                item = item.split(' x ')
                items_old[item[0]] = int(item[1])
        strings = new_stock.stock.splitlines()
        for string in strings:
            if string.startswith('/add_'):
                item = string.split('   ')[1]
                item = item.split(' x ')
                items_new[item[0]] = int(item[1])
        resource_diff_add, resource_diff_del = get_diff(items_new, items_old)
        msg = MSG_STOCK_COMPARE_HARVESTED
        if len(resource_diff_add):
            for key, val in resource_diff_add:
                msg += MSG_STOCK_COMPARE_FORMAT.format(key, val)
        else:
            msg += MSG_EMPTY
        msg += MSG_STOCK_COMPARE_LOST
        if len(resource_diff_del):
            for key, val in resource_diff_del:
                msg += MSG_STOCK_COMPARE_FORMAT.format(key, val)
        else:
            msg += MSG_EMPTY
        send_async(bot, chat_id=update.message.chat.id, text=msg, parse_mode=ParseMode.HTML)
    else:
        send_async(bot, chat_id=update.message.chat.id, text=MSG_STOCK_COMPARE_WAIT, parse_mode=ParseMode.HTML)


@user_allowed
def web_auth(bot: Bot, update: Update):
    user = add_user(update.message.from_user, session)
    auth = session.query(Auth).filter_by(user_id=user.id).first()
    if auth is None:
        auth = Auth()
        auth.id = uuid.uuid4().hex
        auth.user_id = user.id
        session.add(auth)
        session.commit()
    link = WEB_LINK.format(auth.id)
    send_async(bot, chat_id=update.message.chat.id, text=MSG_PERSONAL_SITE_LINK.format(link),
               parse_mode=ParseMode.HTML, disable_web_page_preview=True)
