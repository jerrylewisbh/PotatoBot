import logging

from core.bot import MQBot
from core.texts import *
from core.db import Session
from core.model import User, Item
from cwmq import Publisher
from functions.reply_markup import generate_user_markup

Session()
p = Publisher()


class APIInvalidTokenException(Exception):
    pass


class APIMissingAccessRightsException(Exception):
    pass


class APIMissingUserException(Exception):
    pass


class APIWrongItemCode(Exception):
    pass


class APIWrongSettings(Exception):
    pass


def update_stock(user):
    if not user:
        raise APIMissingUserException("User is 'None'")
    elif not user.api_token:
        raise APIInvalidTokenException("User has no API token")
    elif not user.is_api_profile_allowed:
        raise APIMissingAccessRightsException("User has not given permission for stock")

    p.publish({
        "token": user.api_token,
        "action": "requestStock"
    })


def update_profile(user):
    if not user:
        raise APIMissingUserException("User is 'None'")
    elif not user.api_token:
        raise APIInvalidTokenException("User has no API token")
    elif not user.is_api_profile_allowed:
        raise APIMissingAccessRightsException("User has not given permission for profile")

    p.publish({
        "token": user.api_token,
        "action": "requestProfile"
    })


def want_to_buy(user: User, item_code, quantity, price, exact_price=True):
    if not user:
        raise APIMissingUserException("User is 'None'")
    elif not user.api_token:
        raise APIInvalidTokenException("User has no API token")
    elif not user.is_api_trade_allowed:
        raise APIMissingAccessRightsException("User has not given permission for trade")
    elif not user.setting_automated_hiding and not user.setting_automated_sniping:
        raise APIWrongSettings("User has disabled sniping and hiding. Trading is not allowed.")

    if not item_code:
        raise APIWrongItemCode("Item code '{}' is invalid".format(item_code))

    item = Session.query(Item).filter(Item.cw_id == item_code).first()
    if not item:
        raise APIWrongItemCode("Item code '{}' is invalid".format(item_code))

    wtb_req = {
        "token": user.api_token,
        "action": "wantToBuy",
        "payload": {
            "itemCode": item.cw_id,
            "quantity": quantity,
            "price": price,
            "exactPrice": exact_price
        }
    }
    p.publish(wtb_req)


def request_trade_terminal_access(bot: MQBot, user: User):
    if not user:
        return

    logging.info("User has not granted Trade access but we have a token. Requesting access")
    bot.send_message(
        user.id,
        MSG_API_REQUIRE_ACCESS_TRADE,
        reply_markup=generate_user_markup(user.id)
    )
    grant_req = {
        "token": user.api_token,
        "action": "authAdditionalOperation",
        "payload": {
            "operation": "TradeTerminal"
        }
    }
    p.publish(grant_req)


def request_stock_access(bot: MQBot, user: User):
    if not user:
        return

    bot.send_message(
        user.id,
        MSG_API_REQUIRE_ACCESS_STOCK,
        reply_markup=generate_user_markup(user.id)
    )

    grant_req = {
        "token": user.api_token,
        "action": "authAdditionalOperation",
        "payload": {
            "operation": "GetStock"
        }
    }
    p.publish(grant_req)


def request_profile_access(bot: MQBot, user: User):
    if not user:
        return

    bot.send_message(
        user.id,
        MSG_API_REQUIRE_ACCESS_PROFILE,
        reply_markup=generate_user_markup(user.id)
    )

    grant_req = {
        "token": user.api_token,
        "action": "authAdditionalOperation",
        "payload": {
            "operation": "GetUserProfile"
        }
    }
    p.publish(grant_req)
