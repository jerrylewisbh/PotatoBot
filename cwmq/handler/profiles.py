import datetime
import json
import logging

from config import BOT_ONE_STEP_API
from core.enums import CASTLE_MAP, CLASS_MAP
from core.functions.common import (MSG_API_REQUIRE_ACCESS_PROFILE,
                                   MSG_API_REQUIRE_ACCESS_STOCK,
                                   MSG_API_REVOKED_PERMISSIONS,
                                   MSG_API_SETUP_STEP_1_COMPLETE,
                                   MSG_API_SETUP_STEP_2_COMPLETE,
                                   stock_compare, MSG_API_REQUIRE_ACCESS_TRADE)
from core.functions.profile import get_required_xp
from core.functions.reply_markup import generate_user_markup
from core.types import Character, Session, User
from cwmq import Publisher, wrapper
from sqlalchemy.exc import InterfaceError, InvalidRequestError
from telegram import ParseMode, Bot

session = Session()
p = Publisher()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def profile_handler(channel, method, properties, body, dispatcher):
    logger.info('Received message # %s from %s: %s', method.delivery_tag, properties.app_id, body)
    data = json.loads(body)

    try:
        # Code to just flush everything out...
        # channel.basic_ack(method.delivery_tag)
        # return

        # Get user details if possible...
        user = None
        try:
            if data and "payload" in data and data["payload"] and "userId" in data['payload']:
                user = session.query(User).filter_by(id=data['payload']['userId']).first()
        except (InterfaceError, InvalidRequestError):
            logging.warning("Request/Interface Error occured, doing rollback and trying again...")
            session.rollback()
            user = session.query(User).filter_by(id=data['payload']['userId']).first()

        if "action" not in data:
            if data['payload']['operation'] in ("GetUserProfile", "GetStock", "TradeTerminal"):
                logger.info("authAdditionalOperation - Response")
                if data['result'] == "Ok" and user:
                    # Since we're stateless we have to temporarily save the action and request_id
                    user.api_request_id = data['uuid']
                    user.api_grant_operation = data['payload']['operation']
                    session.add(user)
                    session.commit()
                else:
                    logger.error("TODO!? %r, %r", data, user)
            else:
                logger.warning("TODO: %r", data)
        elif data['action'] == "grantToken" and data['result'] == "Ok":
            user.api_token = data['payload']['token']
            user.api_user_id = data['payload']['id']

            # Botato is granted this all in one step!
            if BOT_ONE_STEP_API:
                user.is_api_profile_allowed = True
                user.is_api_stock_allowed = True
                user.is_api_trade_allowed = True

            session.add(user)
            session.commit()

            logger.info("Added token for chat_id=%s", data['payload']['userId'])
            dispatcher.bot.send_message(
                user.id,
                MSG_API_SETUP_STEP_1_COMPLETE,
                reply_markup=generate_user_markup(user.id)
            )

            p.publish({
                "token": user.api_token,
                "action": "requestProfile"
            })

            # grant_req = {
            #    "token": user.api_token,
            #    "action": "authAdditionalOperation",
            #    "payload": {
            #        "operation": "GetUserProfile",
            #    }
            #}
            # p.publish(grant_req)
        elif data['action'] == "grantAdditionalOperation" and data['result'] == "Ok":
            logger.info("grantAdditionalOperation was successful!")

            # Reset request ID
            user.api_request_id = None

            message = ""
            if user.api_grant_operation == "TradeTerminal":
                user.is_api_trade_allowed = True
                user.api_grant_operation = None
                message = MSG_API_SETUP_STEP_2_COMPLETE
                grant_req = {
                    "token": user.api_token,
                    "action": "authAdditionalOperation",
                    "payload": {
                        "operation": "TradeTerminal",
                    }
                }
                p.publish(grant_req)
            elif user.api_grant_operation == "GetUserProfile":
                user.is_api_profile_allowed = True
                user.api_grant_operation = None
                message = MSG_API_SETUP_STEP_2_COMPLETE
                grant_req = {
                    "token": user.api_token,
                    "action": "authAdditionalOperation",
                    "payload": {
                        "operation": "GetStock",
                    }
                }
                p.publish(grant_req)
            elif user.api_grant_operation == "GetStock":
                message = MSG_API_SETUP_STEP_2_COMPLETE
                user.api_grant_operation = None  # We don't need this code anymore!
                user.is_api_stock_allowed = True

                p.publish({
                    "token": user.api_token,
                    "action": "requestProfile"
                })
                p.publish({
                    "token": user.api_token,
                    "action": "requestStock"
                })

            session.add(user)
            session.commit()

            dispatcher.bot.send_message(
                user.id,
                message,
                reply_markup=generate_user_markup(user.id)
            )

         # Profile requests...
        elif data['action'] == "requestProfile":
            if data['result'] == "InvalidToken":
                # Revoked token?
                user = session.query(User).filter_by(api_token=data['payload']['token']).first()
                api_access_revoked(dispatcher.bot, user)
            elif data['result'] == "Forbidden":
                logger.warning("User has not granted Profile/Stock access but we have a token. Requesting access")

                dispatcher.bot.send_message(
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
            elif data['result'] == "Ok":
                # Seems we have access although we thought we don't have it...
                # if not user.is_profile_access_granted():
                #    logger.warning("State is wrong? We already have granted persmissions for Profile!")
                #    user.set_profile_access_granted(True)
                #   user.save()

                if not user:
                    # Shouldn't happen!?
                    channel.basic_ack(method.delivery_tag)
                    return

                c = Character()
                c.user_id = user.id
                c.date = datetime.datetime.now()
                guildTag = "[" + data['payload']['profile']['guild_tag'] + "]" if 'guild_tag' in data['payload'][
                    'profile'] and data['payload']['profile']['guild_tag'] else ''
                c.name = guildTag + data['payload']['profile']['userName']
                c.prof = CASTLE_MAP[data['payload']['profile']['castle']]
                c.characterClass = CLASS_MAP.get(data['payload']['profile']['class'], "Unknown class")
                c.pet = None
                c.maxStamina = -1  # TODO?
                c.level = data['payload']['profile']['lvl']
                c.attack = data['payload']['profile']['atk']
                c.defence = data['payload']['profile']['def']
                c.exp = data['payload']['profile']['exp']
                c.needExp = get_required_xp(data['payload']['profile']['lvl'])
                c.castle = data['payload']['profile']['castle']
                c.gold = data['payload']['profile']['gold']
                c.donateGold = data['payload']['profile']['pouches'] if 'pouches' in data['payload']['profile'] else 0
                session.add(c)
                session.commit()

                """
                  {castle}{userName}
                  🏅Level: {lvl}
                  ⚔Atk: {atk} 🛡Def: {def}
                  🔥Exp: {exp}
                  🔋Stamina: {stamina}
                  💧Mana: {mana}
                  💰{gold} 👝{pouches}
                  🏛Class info: {class}
                """
        elif data['action'] == "requestStock":
            if data['result'] == "InvalidToken":
                # Revoked token?
                user = session.query(User).filter_by(api_token=data['payload']['token']).first()
                api_access_revoked(dispatcher.bot, user)
            elif data['result'] == "Forbidden":
                logger.warning("User has not granted Profile/Stock access but we have a token. Requesting access")

                dispatcher.bot.send_message(
                    user.id,
                    MSG_API_REQUIRE_ACCESS_STOCK,
                    reply_markup=generate_user_markup(user.id)
                )
                # TODO: Keyboard update?

                grant_req = {
                    "token": user.api_token,
                    "action": "authAdditionalOperation",
                    "payload": {
                        "operation": "GetStock"
                    }
                }
                p.publish(grant_req)
            elif data['result'] == "Ok":
                if not user:
                    # Shouldn't happen!?
                    channel.basic_ack(method.delivery_tag)
                    return
                logger.info("Stock update for %s...", user.id)

                # FixMe: Filled stock slots is currently not tracked. Maybe calculate it?
                text = "📦Storage (???/???):\n"  # We don't have the overall size (yet) so we enter dummy text...
                for item, count in data['payload']['stock'].items():
                    text += "{} ({})\n".format(item, count)

                stock_info = "<b>Your stock after war:</b> \n\n{}".format(stock_compare(session, user.id, text))

                # if get_game_state() != GameState.HOWLING_WIND:
                #    # Don't send stock change notification when wind is not howling...
                #    # TODO: This might be too late?!
                #
                channel.basic_ack(method.delivery_tag)  # Acknowledge manually
                # FIXME: DO NOT SEND STOCK CHANGE FOR THE TIME BEEING
                return

                dispatcher.bot.send_message(
                    user.id,
                    stock_info,
                    parse_mode=ParseMode.HTML,
                    reply_markup=generate_user_markup(user.id)
                )
        elif data['action'] == "wantToBuy":
            if data['result'] == "InvalidToken":
                # Revoked token?
                user = session.query(User).filter_by(api_token=data['payload']['token']).first()
                api_access_revoked(dispatcher.bot, user)
            elif data['result'] == "Forbidden":
                wrapper.request_trade_terminal(dispatcher.bot, user)
            elif data['result'] == "Ok":
                # Do we need to track OK results for buy orders?
                pass

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


def api_access_revoked(bot: Bot, user):
    if user:
        logger.info("Revoking settings for user %s and token %s", user.id, user.api_token)
        # We have to get the user from by token since userId is not published and user is None currently...

        # Remove api settings...
        user.is_api_stock_allowed = False
        user.is_api_profile_allowed = False
        user.is_api_trade_allowed = False
        user.api_token = None
        session.add(user)
        session.commit()

        bot.send_message(
            user.id,
            MSG_API_REVOKED_PERMISSIONS,
            reply_markup=generate_user_markup(user.id)
        )


