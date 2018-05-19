import datetime
import json
import logging

from telegram import ParseMode

from core.enums import CASTLE_MAP
from core.functions.common import stock_compare_forwarded, stock_compare
from core.functions.profile import get_required_xp
from core.state import get_game_state, GameState
from cwmq import Publisher

from homeassistant.components.notify import telegram

from core.types import Session, User, Character

session = Session()
p = Publisher()

def mq_handler(channel, method, properties, body, dispatcher):
    logging.info('Received message # %s from %s: %s', method.delivery_tag, properties.app_id, body)
    data = json.loads(body)

    # Get user details if possible...
    user = None
    if data and "payload" in data and data["payload"] and "userId" in data['payload']:
        user = session.query(User).filter_by(id=data['payload']['userId']).first()

    if "action" not in data:
        if data['payload']['operation'] in ("GetUserProfile", "GetStock"):
            logging.info("authAdditionalOperation - Response")
            if data['result'] == "Ok" and user:
                # Since we're stateless we have to temporarily save the action and request_id
                user.api_request_id = data['uuid']
                user.api_grant_operation = data['payload']['operation']
                session.add(user)
                session.commit()
            else:
                logging.error("TODO!? %r, %r", data, user)
        else:
            logging.warning("TODO: %r", data)
    elif data['action'] == "grantToken" and data['result'] == "Ok":
        user.api_token = data['payload']['token']
        session.add(user)
        session.commit()

        logging.info("Added token for chat_id=%s", data['payload']['userId'])
        dispatcher.bot.send_message(
            user.id,
            "👌 First step is complete! Now you will receive another request to allow me access to your profile. Please also forward this code to me.",
        )

        logging.info("Requesting profile access")
        grant_req = {
            "token": user.api_token,
            "action": "authAdditionalOperation",
            "payload": {
                "operation": "GetUserProfile",
            }
        }
        p.publish(grant_req)
    elif data['action'] == "grantAdditionalOperation" and data['result'] == "Ok":
        logging.info("grantAdditionalOperation was successful!")

        # Reset request ID
        user.api_request_id = None

        message = ""
        if user.api_grant_operation == "GetUserProfile":
            message = "👌 Second step is complete! Now as a last step please allow me access to your stock. Please also forward this code to me."
            user.is_api_profile_allowed = True
            user.api_grant_operation = "requestStock"

            grant_req = {
                "token": user.api_token,
                "action": "authAdditionalOperation",
                "payload": {
                    "operation": "GetStock",
                }
            }
            p.publish(grant_req)
        elif user.api_grant_operation == "GetStock":
            message = "👌 All set up now! Thank you!"
            user.api_grant_operation = None # We don't need this code anymore!
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
            message
            #reply_markup=_get_keyboard(user)
        )

     # Profile requests...
    elif data['action'] == "requestProfile":
        if data['result'] == "InvalidToken":
            # Revoked token?
            # TODO: Inform user?
            logging.warning("InvalidToken response for token %s", data['payload']['token'])

            # We have to get the user from by token since userId is not published and user is None currently...
            user = session.query(User).filter_by(api_token=data['payload']['token']).first()

            if user:
                dispatcher.bot.send_message(
                    user.id,
                    "It seems I'm unable to access your profile. Did you /revoke your permission?",
                )
                # TODO: Keyboard refresh?

                # Remove api settings...
                user.is_api_stock_allowed = False
                user.is_api_profile_allowed = False
                user.api_token = None
                session.add(user)
                session.commit()
        elif data['result'] == "Forbidden":
            logging.warning("User has not granted Profile/Stock access but we have a token. Requesting access")

            text = "Seems like I don't have permission to access your profile yet. You'll get a request from me " \
                   "please forward this code to me!"

            dispatcher.bot.send_message(
                user.id,
                text
            )
            # TODO: Keyboard update?

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
            #if not user.is_profile_access_granted():
            #    logging.warning("State is wrong? We already have granted persmissions for Profile!")
            #    user.set_profile_access_granted(True)
            #   user.save()

            c = Character()
            c.user_id = user.id
            c.date = datetime.datetime.now()
            c.name = data['payload']['profile']['userName']
            c.prof = CASTLE_MAP[data['payload']['profile']['castle']]
            # data['payload']['profile']['class'] # TODO
            c.pet = None
            c.maxStamina = -1 # TODO?
            c.level = data['payload']['profile']['lvl']
            c.attack = data['payload']['profile']['atk']
            c.defence = data['payload']['profile']['def']
            c.exp = data['payload']['profile']['exp']
            c.needExp = get_required_xp(data['payload']['profile']['lvl']) # TODO
            c.castle = data['payload']['profile']['castle']
            c.gold = data['payload']['profile']['gold']
            c.donateGold = data['payload']['profile']['pouches']
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

            #dispatcher.bot.send_message(
            #    data['payload']['userId'],
            #    "{}".format(data['payload']),
            #    # reply_markup=_get_keyboard(user)
            #)

    elif data['action'] == "requestStock":
        if data['result'] == "InvalidToken":
            # Revoked token?
            # TODO: Inform user?
            logging.warning("InvalidToken response for token %s", data['payload']['token'])

            # We have to get the user from by token since userId is not published and user is None currently...
            user = session.query(User).filter_by(api_token=data['payload']['token']).first()

            if user:
                dispatcher.bot.send_message(
                    user.id,
                    "It seems I'm unable to access your profile. Did you /revoke your permission?",
                )
                # TODO: Keyboard refresh?

                # Remove api settings...
                user.is_api_stock_allowed = False
                user.is_api_profile_allowed = False
                user.api_token = None
                session.add(user)
                session.commit()
        elif data['result'] == "Forbidden":
            logging.warning("User has not granted Profile/Stock access but we have a token. Requesting access")

            text = "Seems like I don't have permission to access your stock yet. You'll get a request from me " \
                   "please forward this code to me!"

            dispatcher.bot.send_message(
                user.id,
                text
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
            logging.info("Stock update for %s...", user.id)

            text = "📦Storage (???/???):\n" # We don't have the overall size (yet) so we enter dummy text...
            for item, count in data['payload']['stock'].items():
                text += "{} ({})\n".format(item, count)

            if get_game_state() != GameState.HOWLING_WIND:
                # Don't send stock change notification when wind is not howling...
                # TODO: This might be too late?!
                return

            stock_info = "<b>Your stock after war:</b> \n\n{}".format(stock_compare(session, user.id, text))

            # Seems we have access although we thought we don't have it...
            #if not user.is_profile_access_granted():
            #    logging.warn("State is wrong? We already have granted persmissions for Profile!")
            #    user.set_profile_access_granted(True)
            #    user.save()

            dispatcher.bot.send_message(
                user.id,
                stock_info,
                parse_mode=ParseMode.HTML
                #reply_markup=_get_keyboard(user)
            )

    # We're done...
    channel.basic_ack(method.delivery_tag)
