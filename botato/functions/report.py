import logging

from datetime import datetime
from telegram import Update
from telegram.error import BadRequest, TimedOut

from config import FWD_CHANNEL
from core.bot import MQBot
from core.db import Session
from core.decorators import command_handler
from core.enums import AdminType, MessageType
from core.model import Group, User, Order
from core.texts import *
from core.utils import update_group, send_async
from functions.order import OrderDraft, __send_order

Session()


@command_handler(
    allow_group=True,
    min_permission=AdminType.GROUP
)
def enable_report_fwd(bot: MQBot, update: Update, user: User):
    if update.message.chat.type in ['group', 'supergroup']:
        group = update_group(update.message.chat)
        group.fwd_minireport = True
        Session.add(group)
        Session.commit()
        send_async(bot, chat_id=update.message.chat.id, text=MSG_MINI_REPORT_FWD_ENABLED)


@command_handler(
    allow_group=True,
    min_permission=AdminType.GROUP
)
def disable_report_fwd(bot: MQBot, update: Update, user: User):
    if update.message.chat.type in ['group', 'supergroup']:
        group = update_group(update.message.chat)
        group.fwd_minireport = False
        Session.add(group)
        Session.commit()
        send_async(bot, chat_id=update.message.chat.id, text=MSG_MINI_REPORT_FWD_DISABLED)


def fwd_report(bot: MQBot, update: Update):
    logging.info("fwd_report called")
    if not update.channel_post or (update.effective_chat and update.effective_chat.id != FWD_CHANNEL):
        # No channel post or wrong channel: Done!
        return
    if not update.channel_post.text or not update.channel_post.text.startswith("⛳️Battle results"):
        # Nothing to do...
        return

    fwd_group = Session.query(Group).filter(
        Group.fwd_minireport.is_(True),
        Group.bot_in_group.is_(True),
        Group.id != FWD_CHANNEL
    ).all()

    for group in fwd_group:
        logging.debug("Forwarding report to '%s/%s'", group.id, group.title)

        if group.id == FWD_CHANNEL:
            logging.error("Forwarding battle reports is enabled for forward channel, this is a really bad idea!")
            continue

        try:
            bot.forward_message(
                chat_id=group.id,
                from_chat_id=FWD_CHANNEL,
                message_id=update.channel_post.message_id
            )

            # Send "after battle" notification to these groups...
            if group.squad and group.squad.reminders_enabled:
                new_order = Order()
                new_order.text = MSG_MAIN_SEND_REPORTS
                new_order.chat_id = group.id,
                new_order.date = datetime.now()
                new_order.confirmed_msg = 0
                Session.add(new_order)
                Session.commit()

                # Temporary object... TODO: Move this directly to DB?
                o = OrderDraft()
                o.pin = True
                o.order = new_order.text
                o.type = MessageType.TEXT
                o.button = False

                __send_order(
                    bot=bot,
                    order=o,
                    chat_id=new_order.chat_id,
                    markup=None
                )

        except BadRequest:
            logging.warning("BadRequest raised for fwd to '%s/%s'", group.id, group.title)
        except TimedOut:
            logging.warning("TimedOut raised for fwd to '%s/%s'", group.id, group.title)