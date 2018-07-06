import re
from telegram import Bot, Update, ParseMode

from config import CWBOT_ID
from core.bot import MQBot
from core.decorators import command_handler
from core.texts import GUILD_WITHDRAW, GUILD_DEPOSIT, GUILD_WITHDRAW_HELP
from core.types import Session, Item, User, new_item
from core.utils import send_async
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


@command_handler()
def withdraw_help(bot: MQBot, update: Update, user: User):
    send_async(
        bot,
        chat_id=update.message.chat.id,
        text=GUILD_WITHDRAW_HELP,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=generate_user_markup(user_id=update.message.from_user.id)
    )


@command_handler(
    forward_from=CWBOT_ID
)
def withdraw(bot: MQBot, update: Update, user: User):
    text = GUILD_WITHDRAW

    for line in update.message.text.splitlines():
        find = re.search(r"(?P<itemId>[a-zA-Z0-9]+) (?P<item>.+)(?: x (?P<count>[0-9]+))", line)
        if find:
            db_item = Session.query(Item).filter(Item.name == find.group("item")).first()
            if not db_item:
                db_item = new_item(find.group("item"), False)
            if db_item:
                text += "\n[{} ({}x)](https://t.me/share/url?url={} {} {})".format(
                    db_item.name, find.group("count"), "/g_withdraw", find.group("itemId"), find.group("count")
                )

    send_async(
        bot,
        chat_id=update.message.chat.id,
        text=text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=generate_user_markup(user_id=update.message.from_user.id)
    )


@command_handler()
def deposit(bot: MQBot, update: Update, user: User):
    text = GUILD_DEPOSIT

    for line in user.stock.stock.splitlines():
        find = re.search(r"(?P<item>.+)(?: \((?P<count>[0-9]+)\))", line)
        if find:
            db_item = Session.query(Item).filter(Item.name == find.group("item")).first()
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
