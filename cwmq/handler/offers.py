import json
import logging

import redis
from sqlalchemy import func

from config import SUPER_ADMIN_ID, REDIS_SERVER, REDIS_PORT, REDIS_TTL
from core.functions.common import MSG_DEAL_SOLD, MSG_API_REVOKED_PERMISSIONS, MSG_API_INCOMPLETE_SETUP, \
    MSG_DISABLED_TRADING
from core.functions.reply_markup import generate_user_markup
from core.types import Session, User, Item, UserExchangeOrder
from cwmq import Publisher, wrapper
from telegram import ParseMode

from cwmq.handler.profiles import api_access_revoked

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
            logging.info("Order #%s - item='%s' - user_id='%s', is_api_trade_allowed='%s', setting_automated_sniping='%s'", order.id, order.item.name, order.user.id, order.user.is_api_trade_allowed, order.user.setting_automated_sniping)

            if order.max_price != data['price']:
                # Done...
                logging.info("Price '%s' does not match max_price '%s' or trade is not enabled '%s'/'%s'", data['price'], order.max_price, order.user.is_api_trade_allowed, order.user.setting_automated_sniping)
                continue # Next order!
            elif not order.user.is_api_trade_allowed or not order.user.setting_automated_sniping:
                logging.info(
                    "Trade disabled for %s ('%s'/'%s')",
                    order.user.id,
                    order.user.is_api_trade_allowed,
                    order.user.setting_automated_sniping
                )
                continue # Next order!

            # TODO: On bot startup try to fullfil orders...
            remainings = order.limit

            # Look in redis if there is a recent order. If yes, at maximum order the still outstanding items
            # This is to avoid over-buying on race-conditions. Redis Keys are expired after xx seconds (See: config)
            user_item_key = "{}_{}".format(order.user.id, item.cw_id)
            recently_ordered = r.get(user_item_key)
            order_limit = order.limit
            try:
                recently_ordered = int(recently_ordered)
                if recently_ordered and order.limit > recently_ordered:
                    order_limit = recently_ordered - order_limit.limit
            except:
                pass

            if data['qty'] >= order_limit:
                quantity = order_limit
            elif data['qty'] < order_limit:
                quantity = data['qty']

            # Let's try to fullfil this order
            try:
                buy_order = wrapper.create_want_to_buy(order.user, item.cw_id, quantity, order.max_price)
                logging.warning("I will publish: %s", buy_order)
                p.publish(buy_order)

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
                logging.warning("Missing permissions for User '%s', requesting it.", order.user.id)
                wrapper.request_trade_terminal(dispatcher.bot, order.user)
            except wrapper.APIMissingUserException:
                logging.error("No/Invalid user for create_want_to_uy specified")
            except wrapper.APIWrongItemCode as ex:
                logging.error("Wrong item code was given: %s", ex)
            except wrapper.APIMissingAccessRightsException:
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
