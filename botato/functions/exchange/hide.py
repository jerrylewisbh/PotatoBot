import math

import logging
import re
import redis
from sqlalchemy import collate
from telegram import ParseMode, Update

from config import REDIS_PORT, REDIS_SERVER
from core.bot import MQBot
from core.utils import send_async
from core.decorators import command_handler
from core.texts import *
from core.db import Session, new_item
from core.model import User, Item, UserStockHideSetting
from cwmq import wrapper
from functions.exchange import get_item_by_cw_id, __get_item_worth


def __get_autohide_settings(user):
    logging.info("Getting UserStockHideSetting for %s", user.id)

    settings = user.hide_settings.all()
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

        latest_known_prices = list(map(int, latest_known_prices))
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

    text = HIDE_WELCOME.format(__get_autohide_settings(user))
    print(text)
    send_async(
        bot,
        chat_id=update.message.chat.id,
        text=text,
        parse_mode=ParseMode.MARKDOWN,
    )


@command_handler(
    squad_only=True
)
def hide_items(bot: MQBot, update: Update, user: User, **kwargs):
    args = None
    if "args" in kwargs:
        args = kwargs["args"]

    # Manually triggered hide....
    logging.info("hide_items called by %s", user.id)
    if not user.is_api_trade_allowed:
        wrapper.request_trade_terminal_access(bot, user)
        return

    set_hide_mode(user)
    send_async(
        bot,
        chat_id=update.message.chat.id,
        text=HIDE_STARTED,
        parse_mode=ParseMode.MARKDOWN,
    )

    autohide(user)


@command_handler()
def hide_list(bot: MQBot, update: Update, user: User):
    logging.info("hide_list called by user_id='%s'", user.id)
    """ Generate a forwardable list of items to hide... """
    if user.is_api_stock_allowed:
        wrapper.update_stock(user)

    if not user.stock:
        return

    text = HIDE_LIST

    item_list = []
    for line in user.stock.stock.splitlines():
        find = re.search(r"(?P<item>.+)(?: \((?P<count>[0-9]+)\))", line)
        if find:
            db_item = Session.query(Item).filter(
                Item.name == collate(find.group("item"), 'utf8mb4_unicode_520_ci')
            ).first()
            if not db_item:
                db_item = new_item(find.group("item"), False)
                if not db_item:
                    # Still nothing?
                    continue

            count = int(find.group("count"))
            if db_item.cw_id:
                # We might have to split orders if weight > 1000
                order_count = 1
                max_weight = 1000 / db_item.weight
                if count > max_weight:
                    lot_size = int(max_weight)
                    order_count = int(math.ceil(count / max_weight))
                else:
                    lot_size = count

                worth = __get_item_worth(db_item.name)
                if not worth:
                    continue
                for x in range(0, order_count):
                    if order_count == 1:
                        link = "\n[{}](https://t.me/share/url?url=/wts_{}_{}_1000) {} x {} = {}💰".format(
                            db_item.name,
                            db_item.cw_id,
                            lot_size,
                            count,
                            worth,
                            (worth * count)
                        )
                    elif x == order_count - 1:
                        remaining = int(count % max_weight)
                        link = "\n[{}](https://t.me/share/url?url=/wts_{}_{}_1000) {} x {} = {}💰 ({}/{})".format(
                            db_item.name,  # Name
                            db_item.cw_id,  # Command: Item ID
                            remaining,  # Command: Number of items
                            remaining,  # Number of items
                            worth,  # Worth
                            remaining * worth,  # Overall worth
                            x + 1,  # Batch X
                            order_count,  # ... of Y
                        )
                    else:
                        link = "\n[{}](https://t.me/share/url?url=/wts_{}_{}_1000) {} x {} = {}💰 ({}/{})".format(
                            db_item.name,  # Name
                            db_item.cw_id,  # Command: Item ID
                            lot_size,  # Command: Number of items
                            lot_size,  # Number of items
                            worth,  # Worth
                            (worth * lot_size),  # Overall worth
                            x + 1,  # Batch X
                            order_count,  # ... of Y
                        )
                    item_list.append((worth, link))

    for item in sorted(item_list, key=lambda y: y[0], reverse=True):
        text += item[1]

    if not item_list:
        text += MSG_EMPTY

    send_async(
        bot,
        chat_id=update.message.chat.id,
        text=text,
        parse_mode=ParseMode.MARKDOWN,
    )


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
    squad_only=True
)
def auto_hide(bot: MQBot, update: Update, user: User, **kwargs):
    args = None
    if "args" in kwargs:
        args = kwargs["args"]
    logging.info("[Hide] auto_hide called by %s - args='%s'", update.message.chat.id, args)

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
            "[Hide] New stock-hiding option by user_id='%s', priority='%s', cw_id='%s', max_price='%s'",
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
