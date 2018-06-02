import logging

from core.functions.inline_keyboard_handling import (generate_group_manage,
                                                     generate_groups_manage)
from core.texts import *
from core.types import user_allowed, Session, Item, UserStockHideSetting, User, UserExchangeOrder
from core.utils import send_async
from telegram import Bot, Update, ParseMode

from cwmq.handler.profiles import request_trade_terminal

session = Session()

def get_snipe_settings(user):
    logging.warning("Getting UserExchangeOrder for %s", user.id)
    if not user:
        # TODO: Message?
        return

    text = ""
    if not user.sniping_settings:
        text = "_Nothing configured yet._"
        return text
    else:
        for order in user.sniping_settings.all():
            if order.limit:
                text += SNIPE_BUY_LIMITED.format(order.limit, order.item.name, order.item.cw_id, order.max_price)
            else:
                text += SNIPE_BUY_UNLIMITED.format(order.item.name, order.item.cw_id, order.max_price)

    return text

def get_autohide_settings(user):
    logging.warning("Getting UserStockHideSetting for %s", user.id)
    if not user:
        # TODO: Message?
        return

    text = ""
    if not user.hide_settings:
        text = "_Nothing configured yet._"
        return text
    else:
        for order in user.hide_settings.order_by("priority").all():
            if not order.max_price:
                text += HIDE_BUY_UNLIMITED.format(order.priority, order.item.name, order.item.cw_id)
            else:
                text += HIDE_BUY_LIMITED.format(order.priority, order.item.name, order.item.cw_id, order.max_price)

    return text


@user_allowed
def hide_gold_info(bot: Bot, update: Update):
    logging.warning("hide_gold_info called by %s", update.message.chat.id)

    user = session.query(User).filter_by(id=update.message.chat.id).first()

    if not user.is_api_trade_allowed:
        request_trade_terminal(bot, user.id)
        return

    text = get_autohide_settings(user)
    send_async(
        bot,
        chat_id=update.message.chat.id,
        text=HIDE_WELCOME.format(text),
        parse_mode=ParseMode.MARKDOWN,
    )

@user_allowed
def auto_hide(bot: Bot, update: Update, args=None):
    logging.warning("auto_hide called by %s - args='%s'", update.message.chat.id, args)
    if update.message.chat.type != 'private':
        return

    if len(args) < 1 or len(args) > 3:
        send_async(
            bot,
            chat_id=update.message.chat.id,
            text=HIDE_WRONG_ARGS,
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    limit = None
    if len(args) == 3:
        logging.warning("Three arguments, assuming UPPER limit")
        try:
            limit = int(args[2])
        except:
            send_async(
                bot,
                chat_id=update.message.chat.id,
                text=HIDE_WRONG_LIMIT,
                parse_mode=ParseMode.MARKDOWN,
            )
            return

    priority = None
    try:
        priority = int(args[1])
    except:
        send_async(
            bot,
            chat_id=update.message.chat.id,
            text=HIDE_WRONG_PRIORITY,
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    item = session.query(Item).filter(Item.cw_id == args[0]).first()
    if not item:
        send_async(
            bot,
            chat_id=update.message.chat.id,
            text=HIDE_WRONG_ITEM.format(args[0]),
            parse_mode=ParseMode.MARKDOWN,
        )
        return
    elif not item.tradable:
        send_async(
            bot,
            chat_id=update.message.chat.id,
            text=HIDE_ITEM_NOT_TRADABLE.format(args[0]),
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    user = session.query(User).filter_by(id=update.message.chat.id).first()
    if not user or not item or not priority:
        send_async(
            bot,
            chat_id=update.message.chat.id,
            text=HIDE_WRONG_ARGS,
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    ushs = session.query(UserStockHideSetting).filter(
        UserStockHideSetting.user == user,
        UserStockHideSetting.priority == priority
    ).first()

    if not ushs:
        logging.warning("New StockHideSetting")
        ushs = UserStockHideSetting()

    ushs.user = user
    ushs.priority = priority
    ushs.item = item
    ushs.max_price = limit
    session.add(ushs)
    session.commit()


    send_async(
        bot,
        chat_id=update.message.chat.id,
        text=HIDE_WELCOME.format(get_autohide_settings(user)),
        parse_mode=ParseMode.MARKDOWN,
    )

@user_allowed
def sniping_info(bot: Bot, update: Update):
    logging.warning("sniping_info called by %s", update.message.chat.id)

    user = session.query(User).filter_by(id=update.message.chat.id).first()
    if not user.is_api_trade_allowed:
        request_trade_terminal(bot, user.id)
        return

    text = get_snipe_settings(user)
    send_async(
        bot,
        chat_id=update.message.chat.id,
        text=SNIPE_WELCOME.format(text),
        parse_mode=ParseMode.MARKDOWN,
    )

@user_allowed
def sniping_remove(bot: Bot, update: Update, args=None):
    logging.warning("sniping_remove called by %s - args='%s'", update.message.chat.id, args)
    if len(args) != 1:
        send_async(
            bot,
            chat_id=update.message.chat.id,
            text=SNIPE_WRONG_ARGS_SR,
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    item = session.query(Item).filter(Item.cw_id == args[0]).first()
    if not item:
        send_async(
            bot,
            chat_id=update.message.chat.id,
            text=SNIPE_WRONG_ITEM.format(args[0]),
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    user = session.query(User).filter_by(id=update.message.chat.id).first()
    if not user:
        send_async(
            bot,
            chat_id=update.message.chat.id,
            text=SNIPE_WRONG_ARGS_SR,
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    ueo = session.query(UserExchangeOrder).filter(
        UserExchangeOrder.user == user,
        UserExchangeOrder.item == item
    ).first()

    if ueo:
        logging.warning("Remove sniping order for item %s and user %s", item.name, user.id)
        session.delete(ueo)
        session.commit()

        send_async(
            bot,
            chat_id=update.message.chat.id,
            text=SNIPE_REMOVED.format(item.name),
            parse_mode=ParseMode.MARKDOWN,
        )


@user_allowed
def sniping(bot: Bot, update: Update, args=None):
    logging.warning("snipe called by %s - args='%s'", update.message.chat.id, args)
    if update.message.chat.type != 'private':
        return

    if len(args) < 1 or len(args) > 3:
        send_async(
            bot,
            chat_id=update.message.chat.id,
            text=SNIPE_WRONG_ARGS,
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    limit = 1
    if len(args) == 3:
        try:
            limit = int(args[2])
        except:
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
    except:
        send_async(
            bot,
            chat_id=update.message.chat.id,
            text=SNIPE_WRONG_ARGS,
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    item = session.query(Item).filter(Item.cw_id == args[0]).first()
    if not item:
        send_async(
            bot,
            chat_id=update.message.chat.id,
            text=SNIPE_WRONG_ITEM.format(args[0]),
            parse_mode=ParseMode.MARKDOWN,
        )
        return
    elif not item.tradable:
        send_async(
            bot,
            chat_id=update.message.chat.id,
            text=SNIPE_ITEM_NOT_TRADABLE.format(args[0]),
            parse_mode=ParseMode.MARKDOWN,
        )
        return


    user = session.query(User).filter_by(id=update.message.chat.id).first()
    if not user or not item or not limit:
        send_async(
            bot,
            chat_id=update.message.chat.id,
            text=SNIPE_WRONG_ARGS,
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    ueo = session.query(UserExchangeOrder).filter(
        UserExchangeOrder.user == user,
        UserExchangeOrder.item == item
    ).first()

    if not ueo:
        logging.warning("New UserExchangeOrder")
        ueo  = UserExchangeOrder()

    ueo.user = user
    ueo.limit = limit
    ueo.max_price = max_price
    ueo.item = item
    session.add(ueo)
    session.commit()

    send_async(
        bot,
        chat_id=update.message.chat.id,
        text=SNIPE_WELCOME.format(get_snipe_settings(user)),
        parse_mode=ParseMode.MARKDOWN,
    )
