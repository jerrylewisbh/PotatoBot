import logging
from config import REDIS_PORT, REDIS_SERVER, REDIS_TTL

import redis
from telegram import Bot, ParseMode, Update

from core.decorators import command_handler
from core.exchange import get_item_by_cw_id
from core.texts import *
from core.types import Session, User, UserStockHideSetting
from core.utils import send_async
from cwmq import wrapper


def __get_autohide_settings(user):
    logging.warning("Getting UserStockHideSetting for %s", user.id)

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


def get_best_fulfillable_order(user):
    if user.character.gold == 0:
        return  # We're already done!

    for setting in user.hide_settings.all():
        # Note: It might be wiser to handle sniping overall first and then handle hiding. But digest for sniping
        # is only used as a fallback so we are probably fine and time is not that much of the essence...
        # __handle_hide_orders(digest_item, item, order, r, dispatcher)
        logging.debug("[Hide] user_id='%s' - P%s: cw_id='%s'", user.id, setting.priority, setting.item.cw_id)

        r = redis.StrictRedis(host=REDIS_SERVER, port=REDIS_PORT, db=0)
        # Get latest known prices for items...
        latest_known_prices = r.lrange(setting.item.name, 0, -1)

        logging.debug("[Hide] Checking latest prices for cw_id='%s', name='%s", setting.item.cw_id, setting.item.name)
        if not latest_known_prices:
            # We don't know the prices so we will continue...
            logging.debug(
                "[Hide] No known last prices for cw_id='%s', name='%s",
                setting.item.cw_id,
                setting.item.name
            )
            continue

        min_price = int(min(latest_known_prices))

        logging.debug("[Hide] Setting: max_price='%s' latest_known_min_price='%s'", setting.max_price, min_price)
        if not setting.max_price or (setting.max_price and (int(min(latest_known_prices)) <= setting.max_price)):
            logging.info(
                "[Hide] Found matching order for cw_id='%s' for with P%s '%s' user-specified limit is '%s'",
                user.id,
                setting.priority,
                setting.item.cw_id,
                setting.max_price,
            )
            if user.character.gold >= min_price:
                logging.info(
                    "[Hide] user_id='%s' can afford cw_id='%s' for price='%s'",
                    user.id,
                    setting.item.cw_id,
                    min_price
                )
                return setting.item.cw_id
    return None


def autohide(user: User):
    logging.info("[Hide] user_id='%s' is currently in HIDE MODE", user.id)

    wrapper.update_profile(user)  # Refresh profile!
    cw_id = get_best_fulfillable_order(user)
    if cw_id:
        # Calculate order based on users latest gold Information...
        logging.info("[Hide] issuing wtb for user_id='%s' and cw_id='%s'", user.id, cw_id)
        wrapper.want_to_buy(
            user,
            cw_id,
            1,  # Only 1 piece
            1,  # 1g buy cheapest option avail.,
            False,  # Do not match exact and fail
        )
    else:
        logging.info("[Hide] No more fulfillable orders found for user_id='%s'!", user.id)


"""
Hide.py:
- DONE: Setze User in HIDE mode
- DONE: Hole neues Profil mit Gold

digest.py
- Errechne die zu kaufenden Items wenn user in hide mode für erste erfüllbare order...

deals.py
- summiere ausgeführte orders für hide-user auf und speichere im redis...

profile.py
- wenn insufficient funds kommt: Ignorieren wenn user im hide-mode ist
    -> Triggere erneute prüfung der prios und führe nächste erfüllbare order aus
    -> wenn nix mehr ansteht beende hiding

"""

@command_handler(
    testing_only=True
)
def hide_gold_info(bot: Bot, update: Update, user: User):
    logging.warning("hide_gold_info called by %s", update.message.chat.id)

    user = Session.query(User).filter_by(id=update.message.chat.id).first()

    if not user.is_api_trade_allowed:
        logging.info(
            "TradeTerminal is not allowed for user_id=%s. Gold hiding not possible. Requesting access",
            user.id
        )
        wrapper.request_trade_terminal_access(bot, user)
        return

    text = __get_autohide_settings(user)
    send_async(
        bot,
        chat_id=update.message.chat.id,
        text=HIDE_WELCOME.format(text),
        parse_mode=ParseMode.MARKDOWN,
    )


@command_handler(
    testing_only=True
)
def hide_items(bot: Bot, update: Update, user: User, **kwargs):
    args = None
    if "args" in kwargs:
        args = kwargs["args"]

    # Manually triggered hide....
    logging.info("hide_items called by %s", user.id)
    if not user or not user.is_tester and not user.is_api_trade_allowed:
        logging.info("No user, not a tester or no trade API")
        return

    set_hide_mode(user)
    send_async(
        bot,
        chat_id=update.message.chat.id,
        text=HIDE_STARTED,
        parse_mode=ParseMode.MARKDOWN,
    )

    autohide(user)


def exit_hide_mode(user):
    logging.debug("[Hide] user_id='%s' exiting hide_mode", user.id)
    r = redis.StrictRedis(host=REDIS_SERVER, port=REDIS_PORT, db=0)
    hide_key = "HIDE_{}".format(user.id)
    r.delete(hide_key)


def set_hide_mode(user):
    logging.debug("[Hide] user_id='%s' entering hide_mode", user.id)
    r = redis.StrictRedis(host=REDIS_SERVER, port=REDIS_PORT, db=0)
    # Mark user for 360 seconds as "in Hiding Mode". This way we can detect buy-actions, etc.
    # and one message about his actions, etc. We also use this information to trigger the actual hiding when new
    # digest list comes in.
    hide_key = "HIDE_{}".format(user.id)
    r.set(hide_key, user.id, ex=360)


def get_hide_mode(user):
    r = redis.StrictRedis(host=REDIS_SERVER, port=REDIS_PORT, db=0)
    hide_key = "HIDE_{}".format(user.id)
    state = True if r.get(hide_key) else False

    logging.debug("[Hide] user_id='%s' hide_mode='%s'", user.id, state)
    return state


def append_hide_result(user, text):
    logging.debug("[Hide] user_id='%s' appending text='%s'", user.id, text)
    r = redis.StrictRedis(host=REDIS_SERVER, port=REDIS_PORT, db=0)
    hide_key = "RESULT_HIDE_{}".format(user.id)

    r.append(hide_key, text)
    r.expire(hide_key, 360)

    return r.get(hide_key)


def get_hide_result(user):
    r = redis.StrictRedis(host=REDIS_SERVER, port=REDIS_PORT, db=0)
    hide_key = "RESULT_HIDE_{}".format(user.id)
    hide_result_text = r.get(hide_key)
    logging.debug("[Hide] user_id='%s' getting text='%s'", user.id, hide_result_text)
    if not hide_result_text:
        return ""
    return hide_result_text


@command_handler(
    testing_only=True
)
def auto_hide(bot: Bot, update: Update, user: User, **kwargs):
    args = None
    if "args" in kwargs:
        args = kwargs["args"]
    logging.warning("[Hide] auto_hide called by %s - args='%s'", update.message.chat.id, args)

    if len(args) < 1 or len(args) > 3:
        send_async(
            bot,
            chat_id=update.message.chat.id,
            text=HIDE_WRONG_ARGS,
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    item = get_item_by_cw_id(args[0])
    if not item:
        logging.debug("[Hide] Wrong cw_id='%s' was given by user_id='%s'", args[0], user.id)
        send_async(
            bot,
            chat_id=update.message.chat.id,
            text=HIDE_WRONG_ITEM.format(args[0]),
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    if len(args) == 1:
        logging.debug("[Hide] One argument, assuming delete")
        orders = Session.query(UserStockHideSetting).filter(
            UserStockHideSetting.user == user,
            UserStockHideSetting.item == item
        ).delete()
        Session.commit()

        send_async(
            bot,
            chat_id=update.message.chat.id,
            text=HIDE_REMOVED.format(item.name),
            parse_mode=ParseMode.MARKDOWN,
        )

        return

    max_price = None
    if len(args) == 3:
        logging.debug("[Hide] Three arguments, assuming UPPER max_price")
        try:
            max_price = int(args[2])
        except Exception:
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
    except Exception:
        logging.debug("[Hide] Invalid cw_id was given by user_id='%s'", user.id)
        send_async(
            bot,
            chat_id=update.message.chat.id,
            text=HIDE_WRONG_PRIORITY,
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    item = get_item_by_cw_id(args[0])
    if not item:
        logging.debug("[Hide] Wrong cw_id='%s' was given by user_id='%s'", args[0], user.id)
        send_async(
            bot,
            chat_id=update.message.chat.id,
            text=HIDE_WRONG_ITEM.format(args[0]),
            parse_mode=ParseMode.MARKDOWN,
        )
        return
    elif not item.tradable:
        logging.debug("[Hide] CW item is with cw_id='%s' given by user_id='%s' is not tradable", user.id, args[0])
        send_async(
            bot,
            chat_id=update.message.chat.id,
            text=HIDE_ITEM_NOT_TRADABLE.format(args[0]),
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    user = Session.query(User).filter_by(id=update.message.chat.id).first()
    if not user or not item or not priority:
        logging.debug("[Hide] Wrong arguments user_id='%s', args='%s'", user.id, args)
        send_async(
            bot,
            chat_id=update.message.chat.id,
            text=HIDE_WRONG_ARGS,
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    ushs = Session.query(UserStockHideSetting).filter(
        UserStockHideSetting.user == user,
        UserStockHideSetting.priority == priority
    ).first()

    if not ushs:
        logging.info(
            "New stock-hiding option by user_id='%s', priority='%s', cw_id='%s', max_price='%s'",
            user.id,
            priority,
            item.cw_id,
            max_price
        )
        ushs = UserStockHideSetting()

    ushs.user = user
    ushs.priority = priority
    ushs.item = item
    ushs.max_price = max_price
    Session.add(ushs)
    Session.commit()

    send_async(
        bot,
        chat_id=update.message.chat.id,
        text=HIDE_WELCOME.format(__get_autohide_settings(user)),
        parse_mode=ParseMode.MARKDOWN,
    )
