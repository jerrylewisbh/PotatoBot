import json
import logging

import redis
from sqlalchemy import func

from config import REDIS_PORT, REDIS_SERVER, REDIS_TTL, LOG_LEVEL_MQ
from core.types import Item, Session, UserExchangeOrder, new_item
from cwmq import Publisher, wrapper
from functions.common import (MSG_API_INCOMPLETE_SETUP,
                              MSG_DISABLED_TRADING)

Session()
p = Publisher()

logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL_MQ)

r = redis.StrictRedis(host=REDIS_SERVER, port=REDIS_PORT, db=0)


def offers_handler(channel, method, properties, body, dispatcher):
    Publisher()

    logger.debug('Received message # %s from %s: %s', method.delivery_tag, properties.app_id, body)
    data = json.loads(body)

    try:
        item = Session.query(Item).filter(
            func.lower(Item.name) == data['item'].lower()
        ).first()

        if not item:
            item = new_item(data['item'], True)
            if not item:
                # Still nothing...
                return
        logger.debug("%s/%s: %s", item.id, item.cw_id, item.name)

        # No orders...
        orders = item.user_orders.filter(
            UserExchangeOrder.max_price >= data['price']
        ).order_by(UserExchangeOrder.id).all()
        if not orders:
            channel.basic_ack(method.delivery_tag)
            return

        for order in orders:
            logger.info(
                "Order #%s - item='%s' - user_id='%s', is_api_trade_allowed='%s', setting_automated_sniping='%s', sniping_suspended='%s'",
                order.id,
                order.item.name,
                order.user.id,
                order.user.is_api_trade_allowed,
                order.user.setting_automated_sniping,
                order.user.sniping_suspended)

            if data['price'] > order.max_price:
                # Done...
                logger.info("Price '%s' for '%s' is greater than max_price '%s'",
                             data['price'], order.item.name, order.max_price)
                continue  # Next order!
            elif not order.user.is_api_trade_allowed or not order.user.setting_automated_sniping or order.user.sniping_suspended:
                logger.info(
                    "Trade disabled for %s (API: '%s'/ Setting: '%s' / Suspended: '%s')",
                    order.user.id,
                    order.user.is_api_trade_allowed,
                    order.user.setting_automated_sniping,
                    order.user.sniping_suspended,
                )
                continue  # Next order!

            # TODO: On bot startup try to fullfil orders...

            # Look in redis if there is a recent order. If yes, at maximum order the still outstanding items
            # This is to avoid over-buying on race-conditions. Redis Keys are expired after xx seconds (See: config)
            user_item_key = "{}_{}".format(order.user.id, item.cw_id)
            recently_ordered = r.get(user_item_key)
            order_limit = order.outstanding_order
            try:
                recently_ordered = int(recently_ordered)
                if recently_ordered and order.outstanding_order > recently_ordered:
                    order_limit = recently_ordered - order_limit.outstanding_order
            except BaseException:
                pass

            quantity = order_limit
            if data['qty'] < order_limit:
                quantity = data['qty']

            # Let's try to fullfil this order
            try:
                # Store the ordered item + qty in REDIS
                r.set(user_item_key, quantity, ex=REDIS_TTL)

                # Issue them as single buy-orders not as one big one to optimize results...
                for x in range(0, quantity):
                    wrapper.want_to_buy(order.user, item.cw_id, 1, data['price'])
            except wrapper.APIInvalidTokenException:
                # This really shouldn't happen unless the DB is messed up :-/
                logger.warning("No API ID, incomplete setup. Informing user and disabling trade.")

                u = order.user
                u.setting_automated_sniping = False
                Session.add(u)
                Session.commit()

                dispatcher.bot.send_message(
                    order.user.id,
                    MSG_API_INCOMPLETE_SETUP + MSG_DISABLED_TRADING,
                )
            except wrapper.APIMissingAccessRightsException:
                logger.warning("Missing permissions for User '%s'.", order.user.id)
                # Not requesting it since this might spam a user every 5 minutes...
            except wrapper.APIMissingUserException:
                logger.error("No/Invalid user for create_want_to_uy specified")
            except wrapper.APIWrongItemCode as ex:
                logger.error("Wrong item code was given: %s", ex)
            except wrapper.APIWrongSettings:
                logger.error("User has disabled all trade settings but you tried to create a Buy-Order")

        channel.basic_ack(method.delivery_tag)

    except Exception:
        try:
            # Acknowledge if possible...
            channel.basic_ack(method.delivery_tag)
        except Exception:
            logger.exception("Can't acknowledge message")

        try:
            Session.rollback()
        except BaseException:
            logger.exception("Can't do rollback")

        logger.exception("Exception in MQ handler occured!")
