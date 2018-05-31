import json
import logging

from core.functions.common import MSG_DEAL_SOLD
from core.functions.reply_markup import generate_user_markup
from core.types import Session, User
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
