import json
import logging

from sqlalchemy import func

from config import CC_EXCHANGE_ORDERS
from core.functions.common import MSG_DEAL_SOLD
from core.functions.reply_markup import generate_user_markup
from core.texts import SNIPED_ITEM
from core.types import Session, User, UserExchangeOrder, Item
from cwmq import Publisher
from telegram import ParseMode

Session()

p = Publisher()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def deals_handler(channel, method, properties, body, dispatcher):
    logger.debug('Received message # %s from %s: %s', method.delivery_tag, properties.app_id, body)
    data = json.loads(body)

    try:
        if data and "sellerId" in data:
            user = Session.query(User).filter_by(api_user_id=data['sellerId']).first()

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
            user = Session.query(User).filter_by(api_user_id=data['buyerId']).first()

            if user and user.setting_automated_sniping and not user.sniping_suspended:
                logger.warning("[Snipe] Snipe-Check for %s", user.id)
                # Check if we have a sniping order for this item + user
                item = Session.query(Item).filter(func.lower(Item.name) == data['item'].lower()).first()
                if not item:
                    logging.warning("[Snipe] Unknown item %s", data['item'])
                    channel.basic_ack(method.delivery_tag)
                    return

                logging.warning("[Snipe] Item: %s (%s/%s)", item.name, item.id, item.cw_id)

                order = Session.query(UserExchangeOrder).filter(
                    UserExchangeOrder.user == user,
                    UserExchangeOrder.item == item).first()
                if not order:
                    # Nothing to do...
                    logging.warning("[Snipe] No order from %s for %s", user.id, item.cw_id)
                    channel.basic_ack(method.delivery_tag)
                    return

                if data['price'] > order.max_price:
                    logging.warning("[Snipe] Price does not match price of order! Order Price=%s, Price=%s, User=%s", order.max_price, data['price'], user.id)
                    channel.basic_ack(method.delivery_tag)
                    return

                outstanding_count = order.outstanding_order - data['qty']
                if outstanding_count < 0:
                    logging.warning("outstanding_count < 0 for %s", user.id)

                if outstanding_count == 0:
                    # Order is completed!
                    logging.warning("[Snipe] Order for %s from %s and price %s is completed!", order.item.name, user.id, order.max_price)
                    logging.warning("[Snipe] Deleting %s", order)
                    Session.delete(order)
                    Session.commit()
                elif outstanding_count > 0:
                    order.outstanding_order = outstanding_count
                    logging.warning("[Snipe] Order for %s from %s and price %s now only needs %s items!", order.item.name, user.id,
                                    order.max_price, order.outstanding_order)
                    Session.add(order)
                    Session.commit()

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

                # Send me copies for testing and debugging
                DBG_PREPEND = "For '@{}': ".format(user.username or "<<emptyusername>>")
                if CC_EXCHANGE_ORDERS:
                    dispatcher.bot.send_message(
                        CC_EXCHANGE_ORDERS,
                        DBG_PREPEND + SNIPED_ITEM.format(data['item'],
                                           (data['price'] * data['qty']),
                                           data['qty'],
                                           data['price'],
                                           data['sellerCastle'],
                                           data['sellerName']),
                        #reply_markup=generate_user_markup(user.id),
                        reply_markup=None,
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
            Session.rollback()
        except BaseException:
            logging.exception("Can't do rollback")

        logging.exception("Exception in MQ handler occured!")
