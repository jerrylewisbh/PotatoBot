import redis
from sqlalchemy import func
from telegram import Update, ParseMode

from config import REDIS_SERVER, REDIS_PORT
from core.bot import MQBot
from core.decorators import command_handler
from core.db import Session
from core.model import User, Item, ItemType

from core.utils import send_long_message

Session()

LIMIT_SNIPES = 5
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
        text += "`{}` {}\n".format(item.cw_id or '', item.name)
    text += footer

    return text


@command_handler(
    allow_group=True,
    allow_private=True,
)
def list_items_res(bot: MQBot, update: Update, user: User):
    text = __generate_itemlist(
        "*Resources*\n",
        "\nSee /items for additional things.",
        (Item.item_type == ItemType.RES, )
    )
    send_long_message(
        bot,
        chat_id=update.message.chat.id,
        text=text,
        parse_mode=ParseMode.MARKDOWN,
    )

@command_handler(
    allow_group=True,
    allow_private=True,
)
def list_items(bot: MQBot, update: Update, user: User):
    text = "List Items by type:\n\n" \
           "/items_res - Resources\n" \
           "/items_alch - Alchemist herbs\n" \
           "/items_misc - Miscellaneous stuff\n" \
            "/items_other - Everything else\n"

    send_long_message(
        bot,
        chat_id=update.message.chat.id,
        text=text,
    )

@command_handler(
    allow_group=True,
    allow_private=True,
)
def list_items_other(bot: MQBot, update: Update, user: User):
    text = __generate_itemlist(
        "*Other items:*\n",
        "\nSee /items for additional things.",
        (Item.item_type == ItemType.OTHER,)
    )
    send_long_message(
        bot,
        chat_id=update.message.chat.id,
        text=text,
        parse_mode=ParseMode.MARKDOWN,
    )

@command_handler(
    allow_group=True,
    allow_private=True,
)
def list_items_misc(bot: MQBot, update: Update, user: User):
    text = __generate_itemlist(
        "*Misc items:*\n",
        "\nSee /items for additional things.",
        (Item.item_type == ItemType.MISC,)
    )
    send_long_message(
        bot,
        chat_id=update.message.chat.id,
        text=text,
        parse_mode=ParseMode.MARKDOWN,
    )

@command_handler(
    allow_group=True,
    allow_private=True,
)
def list_items_alch(bot: MQBot, update: Update, user: User):
    text = __generate_itemlist(
        "*Alchemy items:*\n",
        "\nSee /items for additional things.",
        (Item.item_type == ItemType.ALCH,)
    )
    send_long_message(
        bot,
        chat_id=update.message.chat.id,
        text=text,
        parse_mode=ParseMode.MARKDOWN,
    )


@command_handler(
    allow_group=True,
    allow_private=True,
)
def list_items_ignored(bot: MQBot, update: Update, user: User):
    text = __generate_itemlist(
        "*Ignored items:*\n",
        "\nSee /items for additional things.",
        (Item.item_type == ItemType.IGNORE,)
    )
    send_long_message(
        bot,
        chat_id=update.message.chat.id,
        text=text,
        parse_mode=ParseMode.MARKDOWN,
    )


@command_handler(
    allow_group=True,
    allow_private=True,
)
def list_items_unknown(bot: MQBot, update: Update, user: User):
    text = __generate_itemlist(
        "*Items missing a Chatwars Item ID:*\n",
        "\nSee /items for additional things.",
        (Item.item_type.is_(None), )
    )
    send_long_message(
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
