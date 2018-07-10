import json
import logging

import redis
from sqlalchemy import func

from config import REDIS_PORT, REDIS_SERVER, REDIS_TTL, LOG_LEVEL_MQ
from core.types import (Item, Session, UserExchangeOrder)
from cwmq import Publisher, wrapper
from functions.common import (MSG_API_INCOMPLETE_SETUP,
                              MSG_DISABLED_TRADING)

Session()

p = Publisher()

logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL_MQ)


def digest_handler(channel, method, properties, body, dispatcher):
    logger.debug('New message # %s from %s: %s', method.delivery_tag, properties.app_id, body)
    data = json.loads(body)

    try:
        r = redis.StrictRedis(host=REDIS_SERVER, port=REDIS_PORT, db=0)
        for digest_item in data:
            # TODO: Approx. every 5 Minutes we get a new digest. So we could expire after 300 seconds...?
            r.delete(digest_item['name'])
            r.lpush(digest_item['name'], *digest_item['prices'])

            # Look for sniping orders in case we missed a new or old deal that matches...
            item = Session.query(Item).filter(func.lower(Item.name) == digest_item['name'].lower()).first()
            if not item:
                continue  # Don't know that item...

            orders = item.user_orders.order_by(UserExchangeOrder.id).all()
            for order in orders:
                __handle_snipe_orders(digest_item, item, order, r, dispatcher)

        # We're done...
        channel.basic_ack(method.delivery_tag)
    except Exception:
        try:
            # Acknowledge if possible...
            channel.basic_ack(method.delivery_tag)
        except Exception:
            logging.exception("Can't acknowledge message")

        try:
            Session.rollback()
        except BaseException:
            logging.exception("Can't do rollback")

        logging.exception("Exception in MQ handler occured!")


def __handle_snipe_orders(digest_item, item: Item, order: UserExchangeOrder, redis_connection, dispatcher):
    logging.info(
        "[Snipe] Order #%s - item='%s' - user_id='%s', is_api_trade_allowed='%s', setting_automated_sniping='%s'",
        order.id, order.item.name, order.user.id, order.user.is_api_trade_allowed,
        order.user.setting_automated_sniping)

    lowest_price = min(digest_item['prices'])

    if order.max_price not in digest_item['prices']:
        # Done...
        logging.debug("Targeted price '%s' for '%s' is not in digest list", order.max_price, order.item.name)
        return  # Next order!
    elif not order.user.is_api_trade_allowed or not order.user.setting_automated_sniping or order.user.sniping_suspended:
        logging.info(
            "Trade disabled for %s (API: '%s'/ Setting: '%s' / Suspended: '%s')",
            order.user.id,
            order.user.is_api_trade_allowed,
            order.user.setting_automated_sniping,
            order.user.sniping_suspended,
        )
        return  # Next order!

    # Look in redis if there is a recent order. If yes, at maximum order the still outstanding items
    # This is to avoid over-buying on race-conditions. Redis Keys are expired after xx seconds (See: config)
    user_item_key = "{}_{}".format(order.user.id, item.cw_id)
    recently_ordered = redis_connection.get(user_item_key)
    order_limit = order.outstanding_order
    try:
        recently_ordered = int(recently_ordered)
        if recently_ordered and order.outstanding_order > recently_ordered:
            order_limit = recently_ordered - order_limit.outstanding_order
    except BaseException:
        pass

    avail_qty = 0
    for price in digest_item['prices']:
        if price <= order.max_price:
            avail_qty += 1

    quantity = order_limit
    if avail_qty < order_limit:
        quantity = avail_qty

    # Let's try to fullfil this order
    try:
        wrapper.want_to_buy(order.user, item.cw_id, quantity, order.max_price)
        # Store the ordered item + qty in REDIS
        redis_connection.set(user_item_key, quantity, ex=REDIS_TTL)
    except wrapper.APIInvalidTokenException:
        # This really shouldn't happen unless the DB is messed up :-/
        logging.warning("No API ID, incomplete setup. Informing user and disabling trade.")

        u = order.user
        u.setting_automated_sniping = False
        Session.add(u)
        Session.commit()

        dispatcher.bot.send_message(
            order.user.id,
            MSG_API_INCOMPLETE_SETUP + MSG_DISABLED_TRADING,
        )
    except wrapper.APIMissingAccessRightsException:
        logging.warning("Missing permissions for User '%s'", order.user.id)
        # Not requesting it since this might spam a user every 5 minutes...
    except wrapper.APIMissingUserException:
        logging.error("No/Invalid user for create_want_to_uy specified")
    except wrapper.APIWrongItemCode as ex:
        logging.error("Wrong item code was given: %s", ex)
    except wrapper.APIWrongSettings:
        logging.error("User has disabled all trade settings but you tried to create a Buy-Order")
