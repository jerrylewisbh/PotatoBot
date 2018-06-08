import json
import logging

import redis
from sqlalchemy import func

from config import SUPER_ADMIN_ID, REDIS_SERVER, REDIS_PORT, REDIS_TTL
from core.functions.common import MSG_API_INCOMPLETE_SETUP, \
    MSG_DISABLED_TRADING
from core.types import Session, Item, UserExchangeOrder
from cwmq import Publisher, wrapper

Session()
p = Publisher()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

r = redis.StrictRedis(host=REDIS_SERVER, port=REDIS_PORT, db=0)

def offers_handler(channel, method, properties, body, dispatcher):
    p = Publisher()

    logger.debug('Received message # %s from %s: %s', method.delivery_tag, properties.app_id, body)
    data = json.loads(body)

    try:
        item = Session.query(Item).filter(func.lower(Item.name) == data['item'].lower()).first()
        if not item:
            # Create items we do not yet know in the database....
            item = Item()
            item.name = data['item']
            item.tradable = True
            Session.add(item)
            Session.commit()

            dispatcher.bot.send_message(
                SUPER_ADMIN_ID,
                "New item '{}' discovered on exchange!".format(data['item']),
            )
        logging.debug("%s/%s: %s", item.id, item.cw_id, item.name)

        # No orders...
        orders = item.user_orders.order_by(UserExchangeOrder.id).all()
        if not orders:
            channel.basic_ack(method.delivery_tag)
            return

        for order in orders:
            logging.info("Order #%s - item='%s' - user_id='%s', is_api_trade_allowed='%s', setting_automated_sniping='%s', sniping_suspended='%s'", order.id, order.item.name, order.user.id, order.user.is_api_trade_allowed, order.user.setting_automated_sniping, order.user.sniping_suspended)

            if data['price'] > order.max_price:
                # Done...
                logging.info("Price '%s' for '%s' is greater than max_price '%s'", data['price'], order.item.name, order.max_price)
                continue # Next order!
            elif not order.user.is_api_trade_allowed or not order.user.setting_automated_sniping or order.user.sniping_suspended:
                logging.info(
                    "Trade disabled for %s (API: '%s'/ Setting: '%s' / Suspended: '%s')",
                    order.user.id,
                    order.user.is_api_trade_allowed,
                    order.user.setting_automated_sniping,
                    order.user.sniping_suspended,
                )
                continue # Next order!

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
            except:
                pass

            if data['qty'] >= order_limit:
                quantity = order_limit
            elif data['qty'] < order_limit:
                quantity = data['qty']

            # Let's try to fullfil this order
            try:
                wrapper.want_to_buy(order.user, item.cw_id, quantity, data['price'])
                # Store the ordered item + qty in REDIS
                r.set(user_item_key, quantity, ex=REDIS_TTL)
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
                logging.warning("Missing permissions for User '%s'.", order.user.id)
                # Not requesting it since this might spam a user every 5 minutes...
            except wrapper.APIMissingUserException:
                logging.error("No/Invalid user for create_want_to_uy specified")
            except wrapper.APIWrongItemCode as ex:
                logging.error("Wrong item code was given: %s", ex)
            except wrapper.APIWrongSettings:
                logging.error("User has disabled all trade settings but you tried to create a Buy-Order")

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
