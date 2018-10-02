from datetime import datetime

import re
from sqlalchemy import collate
from telegram import Update, ParseMode

from config import CWBOT_ID
from core.bot import MQBot
from core.db import Session, new_item
from core.decorators import command_handler
from core.model import User, Item, Stock, GuildStock, ItemType
from core.texts import *
from core.utils import send_async
from functions.common import get_diff, __get_item_by_cw_id, StockType
from functions.exchange import __get_item_worth
from functions.reply_markup import generate_user_markup


def generate_gstock_requests(query):
    query = query.split()
    requested_item = None
    results = []
    quantity = 1

    if len(query) >= 3 and query[1].isdigit():
        quantity = int(query[1])
        requested_item = " ".join(query[2:])
    elif len(query) >= 2:
        requested_item = " ".join(query[1:])

    if requested_item:
        items = Session.query(Item).filter(
            Item.name.ilike("%" + requested_item + "%")).limit(20).all()

        for item in items:
            if item.cw_id:
                results.append({"label": query[0] + " " + str(quantity) + " " + item.name,
                                "command": "/g_" + query[0] + " " + item.cw_id + " " + str(quantity)})

        return results

def __withdraw(bot: MQBot, update: Update, user: User, stock_type: ItemType):
    text = GUILD_WITHDRAW

    latest_stock = Session.query(GuildStock).filter(
        GuildStock.stock_type == stock_type,
    ).order_by(GuildStock.date).first()

    if not latest_stock:
        send_async(
            bot,
            chat_id=update.message.chat.id,
            text=MSG_INFO_NO_GUILDSTOCK,
            reply_markup=generate_user_markup(user_id=update.message.from_user.id)
        )
        return

    stock_split = latest_stock.stock.splitlines()
    regex = re.compile("(?P<itemId>[a-zA-Z0-9]+) (?P<item>.+)(?: x (?P<count>[0-9]+))")
    for line in stock_split[1:]:
        hit = regex.search(line)
        item = __get_item_by_cw_id(hit.group("itemId"))
        if item:
            text += "\n[{} ({}x)](https://t.me/share/url?url={} {} {})".format(
                item.name, hit.group("count"), "/g_withdraw", hit.group("itemId"), hit.group("count")
            )

    send_async(
        bot,
        chat_id=update.message.chat.id,
        text=text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=generate_user_markup(user_id=update.message.from_user.id)
    )

@command_handler()
def withdraw_res(bot: MQBot, update: Update, user: User):
    __withdraw(bot, update, user, ItemType.RES)

@command_handler()
def withdraw_alch(bot: MQBot, update: Update, user: User):
    __withdraw(bot, update, user, ItemType.ALCH)

@command_handler()
def withdraw_misc(bot: MQBot, update: Update, user: User):
    __withdraw(bot, update, user, ItemType.MISC)

@command_handler()
def withdraw_other(bot: MQBot, update: Update, user: User):
    __withdraw(bot, update, user, ItemType.OTHER)

@command_handler()
def withdraw_info(bot: MQBot, update: Update, user: User):
    send_async(
        bot,
        chat_id=update.message.chat.id,
        text=GUILD_WITHDRAW_HELP,
        parse_mode=ParseMode.HTML,
        reply_markup=generate_user_markup(user_id=update.message.from_user.id)
    )


@command_handler()
def deposit(bot: MQBot, update: Update, user: User):
    text = GUILD_DEPOSIT

    for line in user.stock.stock.splitlines():
        find = re.search(r"(?P<item>.+)(?: \((?P<count>[0-9]+)\))", line)
        if find:
            db_item = Session.query(Item).filter(
                Item.name == collate(find.group("item"), 'utf8mb4_unicode_520_ci')
            ).first()
            if not db_item:
                db_item = new_item(find.group("item"), False)
            if db_item and db_item.cw_id:
                text += "\n[{} ({}x)](https://t.me/share/url?url={} {} {})".format(
                    db_item.name, find.group("count"), "/g_deposit", db_item.cw_id, find.group("count")
                )

    send_async(
        bot,
        chat_id=update.message.chat.id,
        text=text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=generate_user_markup(user_id=update.message.from_user.id)
    )


def get_stock_type(stock_string):
    if not stock_string:
        return None

    # Just extract the first item (or try so) to determine stock type
    split_stock = stock_string.split('\n', maxsplit=3)
    if len(split_stock) > 1:
        split_stock = split_stock[1]
    else:
        return

    item = re.search(r"(?P<cw_id>\w+) ([\w\W]+) x ([0-9]*)", split_stock)
    cw_id = item.group("cw_id")

    item = Session.query(Item).filter(Item.cw_id == cw_id).first()

    if item:
        return item.item_type


def stock_split(old_stock, new_stock):
    """ Split stock text... """
    resources_old = {}
    resources_new = {}
    strings = old_stock.splitlines()

    old_stock_split = old_stock.splitlines()
    regex = re.compile("(?P<itemId>[a-zA-Z0-9]+) (?P<item>.+)(?: x (?P<count>[0-9]+))")
    for line in old_stock_split[1:]:
        hit = regex.search(line)
        resources_old[hit.group("itemId")] = int(hit.group("count"))

    new_stock_split = new_stock.splitlines()
    for line in new_stock_split[1:]:
        hit = regex.search(line)
        resources_new[hit.group("itemId")] = int(hit.group("count"))

    return resources_old, resources_new


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
                item = __get_item_by_cw_id(key)
                if item:
                    gain_worth = __get_item_worth(item.name)
                    hits += 1
                    if item.tradable and gain_worth:
                        running_total += (gain_worth * val)
                        msg += MSG_STOCK_COMPARE_W_PRICE.format(item.name, val, gain_worth, (gain_worth * val))
                    else:
                        msg += MSG_STOCK_COMPARE_WO_PRICE.format(item.name, val)
        if hits == 0:
            msg += MSG_EMPTY

        msg += MSG_STOCK_COMPARE_LOST
        hits = 0
        if len(resource_diff_del):
            for key, val in resource_diff_del:
                item = __get_item_by_cw_id(key)
                if item:
                    hits += 1
                    loss_worth = __get_item_worth(item.name)
                    if item.tradable and loss_worth:
                        running_total += (loss_worth * val)
                        msg += MSG_STOCK_COMPARE_W_PRICE.format(item.name, val, loss_worth, (loss_worth * val))
                    else:
                        msg += MSG_STOCK_COMPARE_WO_PRICE.format(item.name, val)
        if hits == 0:
            msg += MSG_EMPTY

        if running_total != 0:
            msg += MSG_STOCK_OVERALL_CHANGE.format(running_total)

        return msg

    return None


def stock_compare(user_id, new_stock_text):
    """ Save new stock into database and compare it with the newest already saved.
    """

    stock_type = get_stock_type(new_stock_text)

    old_stock = Session.query(GuildStock).filter(
        GuildStock.user_id == user_id,
        GuildStock.stock_type == stock_type.value
    ).order_by(GuildStock.date.desc())

    old_stock = old_stock.first()

    new_stock = GuildStock()
    new_stock.stock = new_stock_text
    new_stock.stock_type = stock_type
    new_stock.user_id = user_id
    new_stock.date = datetime.now()
    Session.add(new_stock)
    Session.commit()

    if old_stock:
        return stock_compare_text(old_stock.stock, new_stock.stock)


@command_handler(
    forward_from=CWBOT_ID
)
def stock_compare_forwarded_guild(bot: MQBot, update: Update, user: User, chat_data: dict):
    cmp_result = stock_compare(update.message.from_user.id, update.message.text)
    if cmp_result:
        send_async(bot, chat_id=update.message.chat.id, text=cmp_result, parse_mode=ParseMode.HTML)
    else:
        send_async(bot, chat_id=update.message.chat.id, text=MSG_STOCK_COMPARE_WAIT, parse_mode=ParseMode.HTML)
