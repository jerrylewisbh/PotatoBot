import logging

from telegram import Bot, Update, ParseMode

from core.decorators import command_handler
from core.exchange import get_item_by_cw_id
from core.texts import HIDE_BUY_UNLIMITED, HIDE_BUY_LIMITED, HIDE_WELCOME, HIDE_WRONG_ARGS, HIDE_WRONG_ITEM, \
    HIDE_REMOVED, HIDE_WRONG_LIMIT, HIDE_WRONG_PRIORITY, HIDE_ITEM_NOT_TRADABLE
from core.types import User, Session, UserStockHideSetting
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
    return

    args = None
    if "args" in kwargs:
        args = kwargs["args"]

    # Manually triggered hide....
    logging.info("hide_items called by %s", user.id)
    if not user or not user.is_tester and not user.is_api_trade_allowed:
        logging.info("No user, not a tester or no trade API")
        return

    #r = redis.StrictRedis(host=REDIS_SERVER, port=REDIS_PORT, db=0)
    #hide_key = "{}_HIDE".format(user.id)
    #r.set(hide_key, quests, ex=REDIS_TTL)

    # Request a profile update to get information about how much gold a user has.
    # This should complete in a few seconds. And we just schedule a the rest in a few seconds
    wrapper.update_profile(user)


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
