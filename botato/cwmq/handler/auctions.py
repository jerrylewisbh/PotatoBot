from datetime import datetime

import json
import logging
import redis

from sqlalchemy import func, collate
from telegram import ParseMode

from config import CC_EXCHANGE_ORDERS, LOG_LEVEL_MQ, MQ_TESTING, REDIS_SERVER, REDIS_PORT
from core.texts import *
from core.db import Session, new_item
from core.model import User, Item, UserExchangeOrder, UserAuctionWatchlist
from core.utils import send_async
from cwmq import Publisher
from functions.exchange.hide import append_hide_result, autohide, get_hide_mode
from functions.reply_markup import generate_user_markup

Session()

p = Publisher()

logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL_MQ)


def auction_digest_handler(channel, method, properties, body, dispatcher):
    logger.info('[Auction Digest] Received message # %s from %s: %s', method.delivery_tag, properties.app_id, body)
    data = json.loads(body)

    try:
        for auction_lot in data:
            __handle_lot(dispatcher.bot, auction_lot, channel, method, dispatcher)

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


def __handle_lot(bot, auction_lot, channel, method, dispatcher):
    logging.debug("Handling: %s", auction_lot)

    if "itemName" in auction_lot:
        item = Session.query(Item).filter(
            Item.name == collate(auction_lot['itemName'], 'utf8mb4_unicode_520_ci')
        ).first()

    if not item:
        item = new_item(auction_lot['itemName'], True)
        if not item:
            # Still nothing?
            return

    if not item.auctionable:
        logging.warning("%s is now auctionable!", item.name)
        item.auctionable = True
        Session.add(item)
        Session.commit()

    r = redis.StrictRedis(host=REDIS_SERVER, port=REDIS_PORT, db=0)
    watchlist_items = Session.query(UserAuctionWatchlist).filter(
        UserAuctionWatchlist.item_id == item.id
    ).all()

    for watchlist_item in watchlist_items:
        state_key = 'notify_au_{}'.format(auction_lot['lotId'])
        notify_state = r.lrange(state_key, 0, -1)
        if notify_state:
            notify_state = list(map(int, notify_state))

        try:
            end = datetime.strptime(auction_lot['endAt'], "%Y-%m-%dT%H:%M:%S.%fZ")
        except ValueError:
            try:
                end = datetime.strptime(auction_lot['endAt'], "%Y-%m-%dT%H:%M:%SZ")
            except:
                logging.warning("Can't parse endAt: %s", auction_lot['endAt'])
                return
        if not notify_state or watchlist_item.user.id not in notify_state:
            if not watchlist_item.max_price or watchlist_item.max_price <= auction_lot['price']:
                send_async(
                    bot,
                    chat_id=watchlist_item.user.id,
                    text=AUCTION_NOTIFICATION.format(
                        auction_lot['itemName'],
                        auction_lot['sellerCastle'],
                        auction_lot['sellerName'],
                        auction_lot['price'],
                        auction_lot['buyerCastle'] if 'buyerCastle' in auction_lot else '',
                        end.strftime("%Y-%m-%d - %H:%M:%S UTC"),
                        auction_lot['lotId']
                    ),
                )

                if not notify_state:
                    r.lpush(state_key, watchlist_item.user.id)
                    r.expire(state_key, 60 * 60 * 24 * 7)  # Delete after a week...
                else:
                    r.lpush(state_key, watchlist_item.user.id)
        else:
            logging.debug("User already notified!")

