import json
import logging

from sqlalchemy import func

from core.functions.common import MSG_DEAL_SOLD
from core.functions.reply_markup import generate_user_markup
from core.texts import SNIPED_ITEM
from core.types import Session, User, UserExchangeOrder, Item
from cwmq import Publisher
from telegram import ParseMode

session = Session()
p = Publisher()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def deals_handler(channel, method, properties, body, dispatcher):
    logger.debug('Received message # %s from %s: %s', method.delivery_tag, properties.app_id, body)
    data = json.loads(body)

    try:
        if data and "sellerId" in data:
            user = session.query(User).filter_by(api_user_id=data['sellerId']).first()

            if user and user.setting_automated_deal_report:
                dispatcher.bot.send_message(
                    user.id,
                    MSG_DEAL_SOLD.format(data['item'],
                                         (data['price'] * data['qty']),
                                         data['qty'],
                                         data['price'],
                                         data['buyerCastle'],
                                         data['buyerName']),
                    reply_markup=generate_user_markup(user.id),
                    parse_mode=ParseMode.HTML,
                )
        if data and "buyerId" in data:
            user = session.query(User).filter_by(api_user_id=data['buyerId']).first()

            if user and user.setting_automated_sniping:
                logger.warning("Snipe-Check for %s", user.id)
                # Check if we have a sniping order for this item + user
                item = session.query(Item).filter(func.lower(Item.name) == data['item'].lower()).first()
                if not item:
                    logging.warning("Unknown item %s", data['item'])
                    channel.basic_ack(method.delivery_tag)
                    return

                logging.warning(item.name)
                order = session.query(UserExchangeOrder).filter(User.id == user.id, Item.id == item.id).first()
                if not order:
                    # Nothing to do...
                    logging.warning("No order from %s for %s", user.id, item.cw_id)
                    channel.basic_ack(method.delivery_tag)
                    return

                if order.max_price != data['price']:
                    logging.warning("Price does not match price of order! Order=%s, Price=%s, User=%s", order.max_price, data['price'], user.id)
                    channel.basic_ack(method.delivery_tag)
                    return

                outstanding_count = order.limit - data['qty']
                if outstanding_count < 0:
                    logging.warning("outstanding_count < 0 for %s", user.id)

                if outstanding_count == 0:
                    # Order is completed!
                    logging.warning("Order for %s from %s and price %s is completed!", order.item.name, user.id, order.max_price)
                    session.delete(order)
                    session.commit()
                elif outstanding_count > 0:
                    order.limit = outstanding_count
                    logging.warning("Order for %s from %s and price %s now only needs %s items!", order.item.name, user.id,
                                    order.max_price, order.limit)
                    session.add(order)
                    session.commit()

                dispatcher.bot.send_message(
                    user.id,
                    SNIPED_ITEM.format(data['item'],
                                        (data['price'] * data['qty']),
                                        data['qty'],
                                        data['price'],
                                        data['sellerCastle'],
                                        data['sellerName']),
                    reply_markup=generate_user_markup(user.id),
                    parse_mode=ParseMode.HTML,
                )

        # We're done...
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
