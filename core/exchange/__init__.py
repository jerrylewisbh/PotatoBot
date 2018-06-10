import logging

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


@command_handler()
def list_items(bot: Bot, update: Update, user: User, **kwargs):
    args = None
    if "args" in kwargs:
        args = kwargs["args"]

    logging.warning("list_items called by %s", update.message.chat.id)

    text = ITEM_LIST

    items = Session.query(Item).filter(Item.tradable == True).order_by(Item.cw_id).all()
    text += "Tradable items:\n"
    for item in items:
        text += "`{} {}\n`".format(pad_string(item.cw_id, 5), pad_string(item.name, 5))

    items = Session.query(Item).filter(Item.tradable == False).order_by(Item.cw_id).all()
    text += "\nNot tradable via Exchange or new items:\n"
    for item in items:
        text += "`{} {}\n`".format(pad_string(item.cw_id, 5), pad_string(item.name, 5))

    send_async(
        bot,
        chat_id=update.message.chat.id,
        text=text,
        parse_mode=ParseMode.MARKDOWN,
    )


