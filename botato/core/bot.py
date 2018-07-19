#!/usr/bin/env python3
# encoding=utf-8

"""
MessageQueue usage example with @queuedmessage decorator.
"""
import logging

import telegram.bot
from sqlalchemy.exc import SQLAlchemyError
from telegram import TelegramError
from telegram.error import Unauthorized, BadRequest, TimedOut, ChatMigrated, NetworkError
from telegram.ext import messagequeue as mq

from core.db import Session
from core.model import User, UserExchangeOrder, UserStockHideSetting, Group
from functions.user.util import disable_api_functions


class MQBot(telegram.bot.Bot):
    """A subclass of Bot which delegates send method handling to MQ"""

    def __init__(self, *args, is_queued_def=True, mqueue=None, **kwargs):
        super(MQBot, self).__init__(*args, **kwargs)
        # below 2 attributes should be provided for decorator usage
        self._is_messages_queued_default = is_queued_def
        self._msg_queue = mqueue or mq.MessageQueue()

    def __del__(self):
        try:
            self._msg_queue.stop()
        except BaseException:
            pass
        super(MQBot, self).__del__()

    @mq.queuedmessage
    def send_message(self, *args, **kwargs):
        """Wrapped method would accept new `queued` and `isgroup`
        OPTIONAL arguments"""

        try:
            return super(MQBot, self).send_message(*args, **kwargs)
        except Unauthorized as ex:
            if "chat_id" in kwargs:
                user = Session.query(User).filter(User.id == kwargs['chat_id']).first()
                if user:
                    logging.info(
                        "Unauthorized for user_id='%s'. Disabling API settings so that we don't contact the user in the future",
                        user.id)
                    # This is a clone of another function but we have to avoid import-loops
                    # Disable API settings but keep his api credentials until user revokes them herself/himself.
                    user.setting_automated_sniping = False
                    user.setting_automated_hiding = False
                    user.setting_automated_report = False
                    user.setting_automated_deal_report = False
                    # Remove all his settings...
                    Session.query(UserExchangeOrder).filter(UserExchangeOrder.user_id == user.id).delete()
                    Session.query(UserStockHideSetting).filter(UserStockHideSetting.user_id == user.id).delete()
                    Session.add(user)
                    Session.commit()
                    return

                group = Session.query(Group).filter(Group.id == kwargs['chat_id']).first()
                if group:
                    group.bot_in_group = False
                    try:
                        Session.add(group)
                        Session.commit()
                        logging.warning(
                            "Bot is no longer member of chat_id='%s', disabling group", kwargs['chat_id']
                        )
                    except SQLAlchemyError:
                        Session.rollback()
                        logging.warning(
                            "Rollback while setting group.bot_in_group = False for chat_id='%s'", kwargs['chat_id']
                        )
                    return

                logging.warning(
                    "Unauthorized occurred: %s. We should probably remove chat_id='%s' from bot.",
                    ex.message,
                    kwargs['chat_id'],
                    exc_info=True
                )

            # Otherwise raise exception
            raise ex
        except ChatMigrated as ex:
            if "chat_id" in kwargs:
                group = Session.query(Group).filter(Group.id == kwargs['chat_id']).first()
                if group:
                    group.bot_in_group = False
                    try:
                        Session.add(group)
                        Session.commit()
                        logging.warning(
                            "chat_id='%s' migrated to chat_id='%s', disabling old group",
                            ex.new_chat_id, kwargs['chat_id']
                        )
                    except SQLAlchemyError:
                        Session.rollback()
                        logging.warning(
                            "Rollback while setting group.bot_in_group = False for chat_id='%s'", kwargs['chat_id']
                        )
                    return
            raise ex
        except TimedOut as ex:
            logging.warning("TimedOut: Ignoring this message")
        except BadRequest as ex:
            logging.error(
                "BadRequest for: user_id='%s', text='%s', error_msg='%s'",
                kwargs['chat_id'] if 'chat_id' in kwargs else '<unknown_chat_id>',
                kwargs['text'] if 'text' in kwargs else '<no_text>',
                ex.message,
            )


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
        logging.warning("TimedOut: Ignoring this message")
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


