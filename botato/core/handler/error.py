import logging

from telegram import TelegramError
from telegram.error import Unauthorized, BadRequest, TimedOut, NetworkError, ChatMigrated

from core.bot import MQBot
from core.db import Session
from core.model import Group, User
from functions.user.util import disable_api_functions


def error_callback(bot: MQBot, update, error, **kwargs):
    """ Error handling """
    try:
        raise error
    except Unauthorized:
        if update.message.chat_id:
            # Group?
            group = Session.query(Group).filter(Group.id == update.message.chat_id).first()
            if group is not None:
                group.bot_in_group = False
                Session.add(group)
                Session.commit()

            # remove update.message.chat_id from conversation list
            user = Session.query(User).filter(User.id == update.message.chat_id).first()
            if user:
                logging.info(
                    "Unauthorized for user_id='%s'. Disabling API settings so that we don't contact the user in the future",
                    user.id)
                disable_api_functions(user)
            else:
                logging.warning(
                    "Unauthorized occurred: %s. We should probably remove user chat_id='%s' from bot.",
                    error.message,
                    update.message.chat_id,
                    exc_info=True
                )
    except BadRequest:
        # handle malformed requests - read more below!
        logging.error("BadRequest occurred: %s", error.message, exc_info=True)
    except TimedOut:
        # handle slow connection problems
        logging.info("TimedOut: Ignoring this message")
    except NetworkError:
        # handle other connection problems

        logging.error("NetworkError occurred: %s", error.message, exc_info=True)
    except ChatMigrated as e:
        # the chat_id of a group has changed, use e.new_chat_id instead
        logging.warning(
            "ChatMigrated occurred: %s",
            error.message,
            exc_info=True
        )
    except TelegramError:
        # handle all other telegram related errors
        logging.error("TelegramError occurred: %s", error.message, exc_info=True)
    except Exception:
        print("START ##################################################")
        print(error)
        print("END ####################################################")
