import logging

from sqlalchemy import func
from telegram import Bot, Update, ParseMode

from core.decorators import command_handler
from core.texts import *
from core.types import Session, Item, User
from core.utils import send_async, pad_string

Session()

LIMIT_SNIPES = 3
LIMIT_ORDER_AMOUNT = 50


def get_item_by_cw_id(cw_id):
    item = Session.query(Item).filter(Item.cw_id == cw_id).first()
    return item

def __generate_itemlist(intro: str, footer: str, filter):
    items = Session.query(Item).filter(
        *filter
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
def list_items(bot: Bot, update: Update, user: User):
    text = __generate_itemlist(
        "*Tradable items:*\n",
        "\nFor a list of additional items that can only be traded in via Auction see /items\_other",
        (Item.tradable == True, Item.cw_id != None)
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
def list_items_other(bot: Bot, update: Update, user: User):
    text = __generate_itemlist(
        "*Items not tradable via Exchange or new items:*\n",
        "\nFor a list of additional items that can be traded in the Exchange see /items",
        (Item.tradable == False, Item.cw_id != None)
    )
    send_async(
        bot,
        chat_id=update.message.chat.id,
        text=text,
        parse_mode=ParseMode.MARKDOWN,
    )

@command_handler()
def list_items_unknown(bot: Bot, update: Update, user: User):
    text = __generate_itemlist(
        "*Items missing a Chatwars Item ID:*\n",
        "",
        (Item.cw_id == None,)
    )
    send_async(
        bot,
        chat_id=update.message.chat.id,
        text=text,
        parse_mode=ParseMode.MARKDOWN,
    )
