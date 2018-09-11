import json
import logging

from sqlalchemy import func, collate
from telegram import ParseMode

from config import CC_EXCHANGE_ORDERS, LOG_LEVEL_MQ, MQ_TESTING
from core.texts import *
from core.db import Session, new_item
from core.model import User, Item, UserExchangeOrder
from cwmq import Publisher
from functions.exchange.hide import append_hide_result, autohide, get_hide_mode
from functions.reply_markup import generate_user_markup

Session()

p = Publisher()

logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL_MQ)


def auction_digest_handler(channel, method, properties, body, dispatcher):
    logger.debug('Received message # %s from %s: %s', method.delivery_tag, properties.app_id, body)
    data = json.loads(body)

    try:
        for auction_lot in data:
            __handle_lot(auction_lot, channel, method, dispatcher)

        # We're done...
        if not MQ_TESTING:
            channel.basic_ack(method.delivery_tag)
    except Exception:
        try:
            # Acknowledge if possible...
            if not MQ_TESTING:
                channel.basic_ack(method.delivery_tag)
        except Exception:
            logger.exception("Can't acknowledge message")

        try:
            Session.rollback()
        except BaseException:
            logger.exception("Can't do rollback")

        logger.exception("Exception in MQ handler occured!")


def __handle_lot(auction_lot, channel, method, dispatcher):
    print(auction_lot)

    if "itemName" in auction_lot:
        item = Session.query(Item).filter(
            Item.name == collate(auction_lot['itemName'], 'utf8mb4_unicode_520_ci')
        ).first()

    if not item:
        item = new_item(auction_lot['itemName'], True)
        if not item:
            # Still nothing?
            return

    for watch_items in item.user_watchlist:
        print(watch_items)


    #autohide(user)  # Continue users auto-hiding

