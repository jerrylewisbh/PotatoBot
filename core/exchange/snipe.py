import logging

from sqlalchemy import func
from telegram import Bot, ParseMode, Update

from core.decorators import command_handler
from core.exchange import LIMIT_ORDER_AMOUNT, LIMIT_SNIPES, get_item_by_cw_id
from core.texts import *
from core.types import Session, User, UserExchangeOrder
from core.utils import send_async
from cwmq import wrapper


def __get_snipe_settings(user: User):
    logging.warning("Getting UserExchangeOrder for %s", user.id)

    settings = user.sniping_settings.all()
    if not settings:
        return "_Nothing configured yet / All orders completed._"
    else:
        text = ""
        for order in settings:
            if order.outstanding_order:
                text += SNIPE_BUY_MULTIPLE.format(
                    order.initial_order,
                    order.item.name,
                    order.item.cw_id,
                    order.max_price,
                    order.outstanding_order
                )
            else:
                text += SNIPE_BUY_ONE.format(order.item.name, order.item.cw_id, order.max_price)
        return text


@command_handler(
    squad_only=True
)
def sniping_info(bot: Bot, update: Update, user: User, **kwargs):
    args = None
    if "args" in kwargs:
        args = kwargs["args"]

    logging.warning("sniping_info called by %s", update.message.chat.id)

    user = Session.query(User).filter_by(id=update.message.chat.id).first()
    if not user.is_api_trade_allowed:
        logging.info("TradeTerminal is not allowed for user_id=%s. Sniping not possible. Requesting access", user.id)
        wrapper.request_trade_terminal_access(bot, user)
        return

    current_settings = __get_snipe_settings(user)
    text = SNIPE_WELCOME.format(current_settings)

    if user.setting_automated_sniping and user.sniping_suspended:
        text += "\n\n" + SNIPE_SUSPENDED_NOTICE

    send_async(
        bot,
        chat_id=update.message.chat.id,
        text=text,
        parse_mode=ParseMode.MARKDOWN,
    )


@command_handler(
    squad_only=True
)
def sniping_remove(bot: Bot, update: Update, user: User, **kwargs):
    args = None
    if "args" in kwargs:
        args = kwargs["args"]

    logging.warning("sniping_remove called by %s - args='%s'", update.message.chat.id, args)
    if len(args) != 1:
        send_async(
            bot,
            chat_id=update.message.chat.id,
            text=SNIPE_WRONG_ARGS_SR,
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    item = get_item_by_cw_id(args[0])
    if not item:
        send_async(
            bot,
            chat_id=update.message.chat.id,
            text=SNIPE_WRONG_ITEM.format(args[0]),
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    user = Session.query(User).filter_by(id=update.message.chat.id).first()
    if not user:
        send_async(
            bot,
            chat_id=update.message.chat.id,
            text=SNIPE_WRONG_ARGS_SR,
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    ueo = Session.query(UserExchangeOrder).filter(
        UserExchangeOrder.user == user,
        UserExchangeOrder.item == item
    ).first()

    if ueo:
        logging.warning("Remove sniping order for item %s and user %s", item.name, user.id)
        Session.delete(ueo)
        Session.commit()

        send_async(
            bot,
            chat_id=update.message.chat.id,
            text=SNIPE_REMOVED.format(item.name),
            parse_mode=ParseMode.MARKDOWN,
        )


@command_handler(
    squad_only=True
)
def sniping_resume(bot: Bot, update: Update, user: User):
    logging.warning("sniping_resume called by %s", update.message.chat.id)
    user = Session.query(User).filter_by(id=update.message.chat.id).first()

    if not user:
        send_async(
            bot,
            chat_id=update.message.chat.id,
            text=SNIPE_WRONG_ARGS_SR,
            parse_mode=ParseMode.MARKDOWN,
        )
        return
    elif not user.sniping_suspended:
        send_async(
            bot,
            chat_id=update.message.chat.id,
            text=SNIPE_NOT_SUSPENDED,
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    user.sniping_suspended = False
    Session.add(user)
    Session.commit()

    send_async(
        bot,
        chat_id=update.message.chat.id,
        text=SNIPE_CONTINUED,
        parse_mode=ParseMode.MARKDOWN,
    )


@command_handler(
    squad_only=True
)
def sniping(bot: Bot, update: Update, user: User, **kwargs):
    args = None
    if "args" in kwargs:
        args = kwargs["args"]
    logging.warning("[Sniping] called by %s - args='%s'", update.message.chat.id, args)

    user = Session.query(User).filter_by(id=update.message.chat.id).first()
    if not user:
        # TODO: Check again if this is OK!
        return

    # A user can directly enter snipe-commands. Check permissions and stop with processing.
    if not user.is_api_trade_allowed:
        logging.info(
            "[Sniping] TradeTerminal is not allowed user_id=%s. Sniping/Options are not possible. Requesting access",
            user.id
        )
        wrapper.request_trade_terminal_access(bot, user)
        return
    elif not user.setting_automated_sniping:
        logging.debug("[Sniping] user_id='%s' has not enabled sniping", user.id)
        send_async(
            bot,
            chat_id=update.message.chat.id,
            text=SNIPE_DISABLED,
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    if len(args) < 1 or len(args) > 3:
        logging.debug("[Sniping] user_id='%s' has sent wrong arguments for sniping", user.id)
        send_async(
            bot,
            chat_id=update.message.chat.id,
            text=SNIPE_WRONG_ARGS,
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    initial_order = 1
    if len(args) == 3:
        try:
            initial_order = int(args[2])
        except Exception:
            logging.debug("[Sniping] user_id='%s' has specified an invalid initial order", user.id)
            send_async(
                bot,
                chat_id=update.message.chat.id,
                text=SNIPE_WRONG_LIMIT,
                parse_mode=ParseMode.MARKDOWN,
            )
            return

    max_price = None
    try:
        max_price = int(args[1])
    except Exception:
        logging.warning("[Sniping] Invalid max_price=%s from user_id=%s", args[1], user.id)
        send_async(
            bot,
            chat_id=update.message.chat.id,
            text=SNIPE_WRONG_ARGS,
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    item = get_item_by_cw_id(args[0])
    if not item:
        logging.debug("[Sniping] user_id='%s' requested sniping for item id='%s'", user.id, args[0])
        send_async(
            bot,
            chat_id=update.message.chat.id,
            text=SNIPE_WRONG_ITEM.format(args[0]),
            parse_mode=ParseMode.MARKDOWN,
        )
        return
    elif not item.tradable:
        logging.debug("[Sniping] user_id='%s' tried to trade untradable item cw_id='%s'", user.id, item.cw_id)
        send_async(
            bot,
            chat_id=update.message.chat.id,
            text=SNIPE_ITEM_NOT_TRADABLE.format(item.cw_id),
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    num_ueo = Session.query(func.count(UserExchangeOrder.id)).filter(
        UserExchangeOrder.user == user
    ).scalar()

    if num_ueo >= LIMIT_SNIPES:
        logging.debug("[Sniping] user_id='%s' has too many active snipes!", user.id)
        send_async(
            bot,
            chat_id=update.message.chat.id,
            text=SNIPE_LIMIT_EXCEEDED.format(LIMIT_SNIPES),
            parse_mode=ParseMode.MARKDOWN,
        )
        return
    if initial_order > LIMIT_ORDER_AMOUNT:
        logging.debug("[Sniping] user_id='%s' wants to buy too many things!", user.id)
        send_async(
            bot,
            chat_id=update.message.chat.id,
            text=SNIPE_INITIAL_ORDER_EXCEEDED.format(LIMIT_ORDER_AMOUNT),
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    ueo = Session.query(UserExchangeOrder).filter(
        UserExchangeOrder.user == user,
        UserExchangeOrder.item == item
    ).first()

    if not ueo:
        logging.info(
            "[Sniping] user_id='%s' created new order intial_order='%s', max_price='%s', item='%s'",
            user.id,
            initial_order,
            max_price,
            item.cw_id,
        )
        ueo = UserExchangeOrder()
    else:
        logging.info(
            "[Sniping] user_id='%s' updated order to intial_order='%s', max_price='%s', item='%s'",
            user.id,
            initial_order,
            max_price,
            item.cw_id,
        )

    ueo.user = user
    ueo.initial_order = initial_order
    ueo.outstanding_order = initial_order
    ueo.max_price = max_price
    ueo.item = item
    Session.add(ueo)
    Session.commit()

    send_async(
        bot,
        chat_id=update.message.chat.id,
        text=SNIPE_WELCOME.format(__get_snipe_settings(user)),
        parse_mode=ParseMode.MARKDOWN,
    )
