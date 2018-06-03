import logging

from sqlalchemy import func
from telegram import Bot

from core.functions.reply_markup import generate_user_markup
from core.texts import MSG_API_REQUIRE_ACCESS_TRADE
from core.types import Session, Item
from cwmq import Publisher

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


def create_want_to_buy(user, item_code, quantity, price, exact_price=True):
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

    return {
        "token": user.api_token,
        "action": "wantToBuy",
        "payload": {
            "itemCode": item.cw_id,
            "quantity": quantity,
            "price": price,
            "exactPrice": exact_price
        }
    }

def request_trade_terminal(bot: Bot, user):
    if not user:
        return

    logging.warning("User has not granted Trade access but we have a token. Requesting access")
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
