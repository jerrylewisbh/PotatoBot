import random
from datetime import datetime
from enum import Enum

from sqlalchemy import collate
from telegram import ParseMode, Update

from config import CWBOT_ID, CASTLE_CHAT_ID
from core.bot import MQBot
from core.db import Session, new_item
from core.decorators import command_handler
from core.enums import AdminType
from core.model import User, Admin, Stock, Item
from core.state import GameState, get_game_state
from core.texts import *
from core.utils import send_async, send_long_message
from functions.admin import __get_user_info
from functions.exchange import __get_item_worth

Session()


class StockType(Enum):
    Stock = 0
    TradeBot = 1


@command_handler()
def help_msg(bot: MQBot, update, user: User):
    admin_user = Session.query(Admin).filter_by(user_id=update.message.from_user.id).all()
    global_adm = False
    for adm in admin_user:
        if adm.admin_type <= AdminType.FULL.value:
            global_adm = True
            break
    if global_adm:
        send_long_message(bot, chat_id=update.message.chat.id, text=MSG_HELP_GLOBAL_ADMIN, parse_mode=ParseMode.HTML)
    elif len(admin_user) != 0:
        send_long_message(bot, chat_id=update.message.chat.id, text=MSG_HELP_GROUP_ADMIN, parse_mode=ParseMode.HTML)
    else:
        send_long_message(bot, chat_id=update.message.chat.id, text=MSG_HELP_USER, parse_mode=ParseMode.HTML)


@command_handler(
    allow_channel=True,
    allow_group=True,
    allow_private=True,
)
def roll(bot: MQBot, update, user: User, **kwargs):
    if update.effective_chat.id == CASTLE_CHAT_ID:
        return

    # Defaults
    dices = 1
    sides = 6

    args = None
    if "args" in kwargs:
        args = kwargs["args"]

    if len(args) == 1:
        parts = args[0].split("d")
        if len(parts) == 2:
            try:
                dices = int(parts[0])
            except:
                pass

            try:
                sides = int(parts[1])
            except:
                pass

    results = ""
    sum = 0

    if dices > 20 or sides > 120 or dices < 1 or sides < 1:
        send_async(
            bot,
            chat_id=update.message.chat.id,
            text="Be reasonable...",
            parse_mode=ParseMode.HTML
        )
        return

    for _ in range(0, dices):
        value = random.randint(1, sides)
        results += "\n{}".format(value)
        sum += value

    sum_text = ""
    if dices > 1:
        sum_text = "<i>Sum: {}</i>".format(sum)

    send_async(
        bot,
        chat_id=update.message.chat.id,
        text="<b>🎲 {} rolled {} dice with {} sides each ({}d{}):</b>\n{}\n\n{}".format(user.first_name, dices, sides, dices, sides, results, sum_text),
        parse_mode=ParseMode.HTML
    )


@command_handler()
def help_intro(bot: MQBot, update, user: User):
    send_async(bot, chat_id=update.message.chat.id, text=MSG_HELP_INTRO, parse_mode=ParseMode.HTML)

@command_handler(
    squad_only=True
)
def tools(bot: MQBot, update, user: User):
    send_async(bot, chat_id=update.message.chat.id, text=MSG_HELP_TOOLS, parse_mode=ParseMode.HTML)

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
        new_item(item_name, False)
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

    return resources_old, resources_new


def __get_item(item_name):
    return Session.query(Item).filter(
        Item.name == collate(item_name, 'utf8mb4_unicode_520_ci')
    ).first()


def __get_item_by_cw_id(cw_id):
    return Session.query(Item).filter(
        Item.cw_id == cw_id
    ).first()


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
                    if item.tradable and gain_worth:
                        running_total += (gain_worth * val)
                        msg += MSG_STOCK_COMPARE_W_PRICE.format(key, val, gain_worth, (gain_worth * val))
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
                    hits += 1
                    loss_worth = __get_item_worth(item.name)
                    if item.tradable and loss_worth:
                        running_total += (loss_worth * val)
                        msg += MSG_STOCK_COMPARE_W_PRICE.format(key, val, loss_worth, (loss_worth * val))
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
def stock_compare_forwarded(bot: MQBot, update: Update, user: User, chat_data: dict):
    # If user-stock is automatically updated via API do not allow reports during SILENCE
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
    min_permission=AdminType.FULL,
)
def user_info(bot: MQBot, update: Update, user: User):
    """ Check one ban """

    username = update.message.text.split(' ', 1)[1]
    username = username.replace('@', '')
    info_user = Session.query(User).filter_by(username=username).first()
    if not info_user:
        try:
            # If we found no match, try to find by user_Id
            info_user = Session.query(User).filter(User.id == int(username)).first()
        except ValueError:
            pass

    if not info_user:
        # Compare permissions between ban user and user who requests it. Only if they are not equal we allow that!
        send_async(
            bot,
            chat_id=update.message.chat_id,
            text="User is unknown!"
        )
    else:
        send_async(
            bot,
            chat_id=update.message.chat_id,
            text=__get_user_info(bot, info_user),
            parse_mode=ParseMode.HTML,
        )


