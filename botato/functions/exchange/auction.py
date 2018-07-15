import logging

from telegram import Update, ParseMode

from core.bot import MQBot
from core.db import Session
from core.decorators import command_handler
from core.model import User
from core.texts import *
from core.utils import send_async

Session()

def __get_auction_settings(user):
    logging.info("Getting UserStockHideSetting for %s", user.id)

    settings = user.hide_settings.order_by("priority").all()
    if not settings:
        return "_Nothing configured yet / All orders completed._"
    else:
        text = ""
        for order in settings:
            if not order.max_price:
                text += HIDE_BUY_UNLIMITED.format(order.priority, order.item.name, order.item.cw_id)
            else:
                text += HIDE_BUY_LIMITED.format(order.priority, order.item.name, order.item.cw_id, order.max_price)
        return text

@command_handler(
    squad_only=True
)
def hide_gold_info(bot: MQBot, update: Update, user: User):
    logging.info("hide_gold_info called by %s", update.message.chat.id)

    user = Session.query(User).filter_by(id=update.message.chat.id).first()

    if not user.is_api_trade_allowed:
        logging.info(
            "TradeTerminal is not allowed for user_id=%s. Gold hiding not possible. Requesting access",
            user.id
        )
        wrapper.request_trade_terminal_access(bot, user)
        return

    if not user.setting_automated_hiding:
        logging.info(
            "setting_automated_hiding is not enabled for user_id=%s.",
            user.id
        )
        send_async(
            bot,
            chat_id=update.message.chat.id,
            text=HIDE_DISABLED,
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    text = __get_autohide_settings(user)
    send_async(
        bot,
        chat_id=update.message.chat.id,
        text=HIDE_WELCOME.format(text),
        parse_mode=ParseMode.MARKDOWN,
    )
