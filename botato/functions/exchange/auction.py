import logging

from telegram import Update, ParseMode

from core.bot import MQBot
from core.db import Session
from core.decorators import command_handler
from core.model import User
from core.texts import *
from core.utils import send_async

Session()

def __get_auction_settings(user):
    logging.info("Getting UserAuctionWatchlist for %s", user.id)

    settings = user.hide_settings.order_by("priority").all()
    if not settings:
        return "_Nothing configured yet / All orders completed._"
    else:
        text = ""
        for order in settings:
            if not order.max_price:
                text += AUCTION_NOTIFY_UNLIMITED.format(order.item.name)
            else:
                text += AUCTION_NOTIFY_LIMITED.format(order.item.name, order.max_price)
        return text

@command_handler(
    squad_only=True
)
def auction_info(bot: MQBot, update: Update, user: User):
    logging.info("auction_info called by %s", update.message.chat.id)
    print("BAR")
    user = Session.query(User).filter_by(id=update.message.chat.id).first()

    text = AUCTION_WELCOME.format(__get_auction_settings(user))
    send_async(
        bot,
        chat_id=update.message.chat.id,
        text=text,
        parse_mode=ParseMode.MARKDOWN,
    )
