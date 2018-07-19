import redis
from sqlalchemy import func
from telegram import Update, ParseMode

from config import REDIS_SERVER, REDIS_PORT
from core.bot import MQBot
from core.decorators import command_handler
from core.db import Session
from core.model import User, Item
from core.utils import pad_string, send_async

Session()

LIMIT_SNIPES = 3
LIMIT_ORDER_AMOUNT = 50


def get_item_by_cw_id(cw_id):
    item = Session.query(Item).filter(Item.cw_id == cw_id).first()
    return item


def __generate_itemlist(intro: str, footer: str, item_filter):
    items = Session.query(Item).filter(
        *item_filter
    ).order_by(func.length(Item.cw_id), Item.cw_id).all()

    text = intro
    for item in items:
        text += "`{}` {}\n".format(pad_string(item.cw_id, 4), item.name)
    text += footer

    return text


@command_handler(
    allow_group=True,
    allow_private=True,
)
def list_items(bot: MQBot, update: Update, user: User):
    text = __generate_itemlist(
        "*Tradable items:*\n",
        "\nFor a list of additional items that can only be traded in via Auction see /items\_other",
        (Item.tradable.is_(True), Item.cw_id.isnot(None))
    )
    send_async(
        bot,
        chat_id=update.message.chat.id,
        text=text,
        parse_mode=ParseMode.MARKDOWN,
    )


@command_handler(
    allow_group=True,
    allow_private=True,
)
def list_items_other(bot: MQBot, update: Update, user: User):
    text = __generate_itemlist(
        "*Items not tradable via Exchange or new items:*\n",
        "\nFor a list of additional items that can be traded in the Exchange see /items",
        (Item.tradable.is_(False), Item.cw_id.isnot(None))
    )
    send_async(
        bot,
        chat_id=update.message.chat.id,
        text=text,
        parse_mode=ParseMode.MARKDOWN,
    )


@command_handler()
def list_items_unknown(bot: MQBot, update: Update, user: User):
    text = __generate_itemlist(
        "*Items missing a Chatwars Item ID:*\n",
        "",
        (Item.cw_id.is_(None),)
    )
    send_async(
        bot,
        chat_id=update.message.chat.id,
        text=text,
        parse_mode=ParseMode.MARKDOWN,
    )


def __get_item_worth(item_name):
    r = redis.StrictRedis(host=REDIS_SERVER, port=REDIS_PORT, db=0)
    item_prices = r.lrange(item_name, 0, -1)
    item_prices = list(map(int, item_prices))

    if item_prices:
        return int(min(item_prices))
    return None
