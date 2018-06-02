import json
import logging

import redis
from sqlalchemy import func

from config import SUPER_ADMIN_ID, REDIS_SERVER, REDIS_PORT, REDIS_TTL
from core.functions.common import MSG_DEAL_SOLD
from core.functions.reply_markup import generate_user_markup
from core.types import Session, User, Item, UserExchangeOrder
from cwmq import Publisher
from telegram import ParseMode

session = Session()
p = Publisher()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

r = redis.StrictRedis(host=REDIS_SERVER, port=REDIS_PORT, db=0)

def offers_handler(channel, method, properties, body, dispatcher):
    p = Publisher()

    logger.info('Received message # %s from %s: %s', method.delivery_tag, properties.app_id, body)
    data = json.loads(body)

    try:
        item = session.query(Item).filter(func.lower(Item.name) == data['item'].lower()).first()
        if not item:
            # Create items we do not yet know in the database....
            item = Item()
            item.name = data['item']
            item.tradable = True
            session.add(item)
            session.commit()

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


        logging.info("We've got orders for %s!", item.name)
        for order in orders:
            logging.debug("Order %s", order.id)
            if order.max_price == data['price']:
                # We have a match...
                remainings = order.limit

                # TODO: On bot startup try to fullfil orders...

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

                order = {
                  "token": order.user.api_token,
                  "action": "wantToBuy",
                  "payload": {
                    "itemCode": item.cw_id,
                    "quantity": quantity,
                    "price": order.max_price,
                    "exactPrice": True
                   }
                }
                logging.warning("I would publish: %s", order)

                p.publish(order)

                # Store the ordered item + qty in REDIS
                r.set(user_item_key, quantity, ex=REDIS_TTL)

        channel.basic_ack(method.delivery_tag)

    except Exception:
        try:
            # Acknowledge if possible...
            channel.basic_ack(method.delivery_tag)
        except Exception:
            logging.exception("Can't acknowledge message")

        try:
            session.rollback()
        except BaseException:
            logging.exception("Can't do rollback")

        logging.exception("Exception in MQ handler occured!")
