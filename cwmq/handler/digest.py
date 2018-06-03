import json
import logging

import redis
from sqlalchemy import func

from config import SUPER_ADMIN_ID, REDIS_SERVER, REDIS_PORT, REDIS_TTL
from core.functions.common import MSG_DEAL_SOLD, MSG_API_INCOMPLETE_SETUP, MSG_DISABLED_TRADING
from core.functions.reply_markup import generate_user_markup
from core.texts import SNIPED_ITEM
from core.types import Session, User, UserExchangeOrder, Item
from cwmq import Publisher, wrapper
from telegram import ParseMode

Session()

p = Publisher()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def digest_handler(channel, method, properties, body, dispatcher):
    logger.info('New message # %s from %s: %s', method.delivery_tag, properties.app_id, body)
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
                continue # Don't know that item...

            orders = item.user_orders.order_by(UserExchangeOrder.id).all()
            for order in orders:
                logging.info(
                    "Order #%s - item='%s' - user_id='%s', is_api_trade_allowed='%s', setting_automated_sniping='%s'",
                    order.id, order.item.name, order.user.id, order.user.is_api_trade_allowed,
                    order.user.setting_automated_sniping)

                lowest_price = min(digest_item['prices'])

                if order.max_price not in digest_item['prices']:
                    # Done...
                    logging.info("Targeted price '%s' for '%s' is not in digest list", order.max_price, order.item.name)
                    continue  # Next order!
                elif not order.user.is_api_trade_allowed or not order.user.setting_automated_sniping:
                    logging.info(
                        "Trade disabled for %s ('%s'/'%s')",
                        order.user.id,
                        order.user.is_api_trade_allowed,
                        order.user.setting_automated_sniping
                    )
                    continue  # Next order!

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

                avail_qty = 0
                for price in data['prices']:
                    if price <= order.max_price:
                        avail_qty += 1

                if avail_qty >= order_limit:
                    quantity = order_limit
                elif avail_qty < order_limit:
                    quantity = avail_qty

                # Let's try to fullfil this order
                try:
                    wrapper.want_to_buy(order.user, item.cw_id, quantity, order.max_price)
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
                    wrapper.request_trade_terminal_access(dispatcher.bot, order.user)
                except wrapper.APIMissingUserException:
                    logging.error("No/Invalid user for create_want_to_uy specified")
                except wrapper.APIWrongItemCode as ex:
                    logging.error("Wrong item code was given: %s", ex)
                except wrapper.APIWrongSettings:
                    logging.error("User has disabled all trade settings but you tried to create a Buy-Order")

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
