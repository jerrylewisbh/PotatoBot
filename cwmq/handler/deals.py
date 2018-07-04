import json
import logging

from sqlalchemy import func
from telegram import ParseMode

from config import CC_EXCHANGE_ORDERS, LOG_LEVEL_MQ
from core.texts import *
from core.types import Item, Session, User, UserExchangeOrder, new_item
from cwmq import Publisher
from functions.exchange.hide import append_hide_result, autohide, get_hide_mode
from functions.reply_markup import generate_user_markup

Session()

p = Publisher()

logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL_MQ)

def deals_handler(channel, method, properties, body, dispatcher):
    logger.debug('Received message # %s from %s: %s', method.delivery_tag, properties.app_id, body)
    data = json.loads(body)

    try:
        if data and "sellerId" in data:
            user = Session.query(User).filter_by(api_user_id=data['sellerId']).first()
            __handle_sold(user, data, channel, method, dispatcher)
        if data and "buyerId" in data:
            user = Session.query(User).filter_by(api_user_id=data['buyerId']).first()
            if user:
                __handle_snipes(user, data, channel, method, dispatcher)
                __handle_hides(user, data, channel, method, dispatcher)

        # We're done...
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


def __handle_hides(user, data, channel, method, dispatcher):
    hide_mode = get_hide_mode(user)
    if not hide_mode or data['qty'] != 1:
        logger.debug("[Deals/Hide] user_id='%s' not in hide-mode or qty!=1", user.id)
        return

    hide_results = append_hide_result(
        user,
        HIDE_BOUGHT.format(data['item'], data['price'])
    )
    autohide(user)  # Continue users auto-hiding


def __handle_sold(user, data, channel, method, dispatcher):
    if user and user.setting_automated_deal_report and not user.is_banned:
        logging.info("[Deals/Hide] Sending user_id='%s' SOLD message", user.id)
        dispatcher.bot.send_message(
            user.id,
            MSG_DEAL_SOLD.format(
                data['item'],
                (data['price'] * data['qty']),
                data['qty'],
                data['price'],
                data['buyerCastle'],
                data['buyerName']
            ),
            reply_markup=generate_user_markup(user.id),
            parse_mode=ParseMode.HTML,
        )


def __handle_snipes(user, data, channel, method, dispatcher):
    if user.setting_automated_sniping and not user.sniping_suspended and not user.is_banned:
        logger.info("[Snipe] Snipe-Check for %s", user.id)
        # Check if we have a sniping order for this item + user
        item = Session.query(Item).filter(func.lower(Item.name) == data['item'].lower()).first()
        if not item:
            logger.info("[Snipe] Unknown item %s", data['item'])
            new_item(data["item"], True)
            return

        logger.info("[Snipe] Item: %s (%s/%s)", item.name, item.id, item.cw_id)

        order = Session.query(UserExchangeOrder).filter(
            UserExchangeOrder.user == user,
            UserExchangeOrder.item == item).first()
        if not order:
            # Nothing to do...
            logger.info("[Snipe] No order from %s for %s", user.id, item.cw_id)
            return

        if data['price'] > order.max_price:
            logger.info("[Snipe] Price does not match price of order! Order Price=%s, Price=%s, User=%s",
                            order.max_price, data['price'], user.id)
            return

        outstanding_count = order.outstanding_order - data['qty']
        if outstanding_count < 0:
            logger.info("outstanding_count < 0 for %s", user.id)

        if outstanding_count == 0:
            # Order is completed!
            logger.info("[Snipe] Order for %s from %s and price %s is completed!", order.item.name, user.id,
                            order.max_price)
            logger.info("[Snipe] Deleting %s", order)
            Session.delete(order)
            Session.commit()
        elif outstanding_count > 0:
            order.outstanding_order = outstanding_count
            logger.info("[Snipe] Order for %s from %s and price %s now only needs %s items!", order.item.name,
                            user.id,
                            order.max_price, order.outstanding_order)
            Session.add(order)
            Session.commit()

        dispatcher.bot.send_message(
            user.id,
            SNIPED_ITEM.format(
                data['item'],
                (data['price'] * data['qty']),
                data['qty'],
                data['price'],
                data['sellerCastle'],
                data['sellerName']
            ),
            reply_markup=generate_user_markup(user.id),
            parse_mode=ParseMode.HTML,
        )

        # Send me copies for testing and debugging
        dbg_prepend = "For '@{}': ".format(user.username or "<<emptyusername>>")
        if CC_EXCHANGE_ORDERS:
            dispatcher.bot.send_message(
                CC_EXCHANGE_ORDERS,
                dbg_prepend + SNIPED_ITEM.format(data['item'],
                                                 (data['price'] * data['qty']),
                                                 data['qty'],
                                                 data['price'],
                                                 data['sellerCastle'],
                                                 data['sellerName']),
                # reply_markup=generate_user_markup(user.id),
                reply_markup=None,
                parse_mode=ParseMode.HTML,
            )
