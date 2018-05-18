import json
import logging

from cwmq import Publisher

from homeassistant.components.notify import telegram

from core.types import Session, User

session = Session()
p = Publisher()

def mq_handler(channel, method, properties, body, dispatcher):
    logging.warning("GOT RESPONSE")
    logging.warning(dispatcher)
    logging.warning(body)

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

        session.add(user)
        session.commit()

        dispatcher.bot.send_message(
            user.id,
            message
            #reply_markup=_get_keyboard(user)
        )
    elif data['action'] == "requestProfile" and data['result'] == "InvalidToken":
        # Revoked token?
        # TODO: Inform user?
        logging.warning("InvalidToken response for token %s", data['payload']['token'])

        # We have to get the user from by token since userId is not published :(
        #user = _users.get_user_by_token(data['payload']['token'])

        #if user.get_id():
        #    dispatcher.bot.send_message(
        #        user.get_id(),
        #        "It seems I'm unable to access your profile. Did you /revoke your permission?",
        #    )
        #    # TODO: WEITER?!
            # User(data['userId']).delete()
    elif data['action'] == "requestProfile" and data['result'] == "Ok":
        # Seems we have access although we thought we don't have it...
        if not user.is_profile_access_granted():
            logging.warn("State is wrong? We already have granted persmissions for Profile!")
            user.set_profile_access_granted(True)
            user.save()

        if data['payload']['profile']['castle'] != "🥔" and user.get_id() not in []:
            user.set_ban(True)
            user.save()

            dispatcher.bot.send_message(
                data['payload']['userId'],
                "*Sorry, wrong castle! Try again after switch!*",
                parse_mode=telegram.ParseMode.MARKDOWN,
                #reply_markup=_get_keyboard(user)
            )
            return

        message = """*Your Profile:*
    {castle}{userName} 
    🏅Level: {lvl}
    ⚔Atk: {atk} 🛡Def: {def}
    🔥Exp: {exp} 
    🔋Stamina: {stamina}
    💧Mana: {mana}
    💰{gold} 👝{pouches}
    🏛Class info: {class}"""

        dispatcher.bot.send_message(
            data['payload']['userId'],
            message.format(**data['payload']['profile']),
            parse_mode=telegram.ParseMode.MARKDOWN,
            #reply_markup=_get_keyboard(user)
        )
    elif data['action'] == "requestStock" and data['result'] == "Ok":
        logging.info("Stock update for %s...", user.get_id())

        # Seems we have access although we thought we don't have it...
        if not user.is_profile_access_granted():
            logging.warn("State is wrong? We already have granted persmissions for Profile!")
            user.set_profile_access_granted(True)
            user.save()

        old_stock = user.get_stock()

        user.set_stock(data['payload']['stock'])
        user.save()

        #stock_diff = get_stock_changes(user.get_stock(), old_stock)

        # logging.warn("OLD_STOCK: %s", old_stock)
        # logging.warn("NEW_STOCK: %s", user.get_stock())
        # logging.warn("DIFF: %s", stock_diff)

        text = "*Your current stock:*\n"
        for item, count in user.get_stock().items():
            text += "{} ({})\n".format(item, count)

        #if stock_diff and (stock_diff['gained'] or stock_diff['lost']):
        #    text += "\n\n*Stock changes since last update:*"#

        #if stock_diff['gained']:
        #    text += "\n\n_Gained:_\n"
        #for item, gain in stock_diff['gained'].items():
        #    text += "{} ({})\n".format(item, gain)
        #if stock_diff['lost']:
        #    text += "\n\n_Lost:_\n"
        #for item, loss in stock_diff['lost'].items():
        #    text += "{} ({})\n".format(item, loss)

        dispatcher.bot.send_message(
            user.get_id(),
            text,
            parse_mode=telegram.ParseMode.MARKDOWN,
            #reply_markup=_get_keyboard(user)
        )
    elif data['action'] in ["requestProfile", "requestStock"] and data['result'] == "Forbidden":
        logging.warning("User has not granted Profile/Stock access but we have a token. Requesting access")

        dispatcher.bot.send_message(
            user.get_id(),
            "Seems like I don't have permission to access your profile/stock yet. You'll get a request from me. Please the code you'll receive back!"
        )

        grant_req = {
            "token": user.get_token(),
            "action": "authAdditionalOperation",
            "payload": {
                "operation": data['payload']['requiredOperation'],
            }
        }
        #q_out.publish(grant_req)

    # We're done...
    channel.basic_ack(method.delivery_tag)
