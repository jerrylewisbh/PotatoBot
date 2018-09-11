import logging
from sqlalchemy import func

from telegram import Update, ParseMode

from core.bot import MQBot
from core.utils import send_async
from core.db import Session
from core.decorators import command_handler
from core.model import User, UserExchangeOrder, UserAuctionWatchlist
from core.texts import *
from functions.exchange import get_item_by_cw_id

Session()

def __get_auction_settings(user):
    logging.info("Getting UserAuctionWatchlist for %s", user.id)

    settings = user.auction_settings.all()
    if not settings:
        return "_Nothing configured yet_"
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
    user = Session.query(User).filter_by(id=update.message.chat.id).first()

    text = AUCTION_WELCOME.format(__get_auction_settings(user))
    send_async(
        bot,
        chat_id=update.message.chat.id,
        text=text,
        parse_mode=ParseMode.MARKDOWN,
    )

@command_handler(
    squad_only=True
)
def watch(bot: MQBot, update: Update, user: User, **kwargs):
    args = None
    if "args" in kwargs:
        args = kwargs["args"]
    logging.info("[Watch] called by %s - args='%s'", update.message.chat.id, args)

    user = Session.query(User).filter_by(id=update.message.chat.id).first()
    if not user:
        # TODO: Check again if this is OK!
        return

    if len(args) < 1 or len(args) > 3:
        logging.debug("[Watch] user_id='%s' has sent wrong arguments for sniping", user.id)
        send_async(
            bot,
            chat_id=update.message.chat.id,
            text=SNIPE_WRONG_ARGS,
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    initial_order = 1
    if len(args) == 3:
        try:
            initial_order = int(args[2])
        except Exception:
            logging.debug("[Watch] user_id='%s' has specified an invalid initial order", user.id)
            send_async(
                bot,
                chat_id=update.message.chat.id,
                text=SNIPE_WRONG_LIMIT,
                parse_mode=ParseMode.MARKDOWN,
            )
            return

    max_price = None
    try:
        max_price = int(args[1])
    except Exception:
        logging.info("[Watch] Invalid max_price=%s from user_id=%s", args[1], user.id)
        send_async(
            bot,
            chat_id=update.message.chat.id,
            text=SNIPE_WRONG_ARGS,
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    item = get_item_by_cw_id(args[0])
    if not item:
        logging.debug("[Watch] user_id='%s' requested sniping for item id='%s'", user.id, args[0])
        send_async(
            bot,
            chat_id=update.message.chat.id,
            text=SNIPE_WRONG_ITEM.format(args[0]),
            parse_mode=ParseMode.MARKDOWN,
        )
        return
    elif not item.auctionable:
        logging.debug("[Watch] user_id='%s' tried to watch unauctionable item cw_id='%s'", user.id, item.cw_id)
        send_async(
            bot,
            chat_id=update.message.chat.id,
            text=AUCTION_ITEM_NOT_TRADABLE.format(item.cw_id),
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    uaw = Session.query(UserAuctionWatchlist).filter(
        UserExchangeOrder.user == user,
        UserExchangeOrder.item == item
    ).first()
    if not uaw:
        logging.info(
            "[Watch] user_id='%s' created new order intial_order='%s', max_price='%s', item='%s'",
            user.id,
            initial_order,
            max_price,
            item.cw_id,
        )
        uaw = UserAuctionWatchlist()
    else:
        logging.info(
            "[Watch] user_id='%s' updated order to intial_order='%s', max_price='%s', item='%s'",
            user.id,
            initial_order,
            max_price,
            item.cw_id,
        )

    uaw.user = user
    uaw.initial_order = initial_order
    uaw.outstanding_order = initial_order
    uaw.max_price = max_price
    uaw.item = item
    Session.add(uaw)
    Session.commit()

    send_async(
        bot,
        chat_id=update.message.chat.id,
        text=AUCTION_WELCOME.format(__get_auction_settings(user)),
        parse_mode=ParseMode.MARKDOWN,
    )
