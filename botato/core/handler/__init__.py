import logging
from telegram import Update
from telegram.ext import run_async

from config import CWBOT_ID
from core.bot import MQBot
from core.decorators import command_handler
from core.state import get_game_state, GameState
from core.db import Session
from core.model import User, Admin, Squad, Group
from functions import order
from functions.order.groups import add
from functions import profile
from functions.quest.handler import parse_quest
from functions.report import fwd_report
from functions.triggers import trigger_show


# noinspection PyCallingNonCallable
@run_async
@command_handler(
    allow_channel=True,
    allow_group=True,
    allow_private=True
)
def manage_all(bot: MQBot, update: Update, user: User, chat_data, job_queue):
    if update.effective_message.chat.type == "channel":
        fwd_report(bot, update)
    elif update.effective_message.chat.type in ['group', 'supergroup']:
        group = Session.query(Group).filter(Group.id == update.message.chat.id).first()

        admin = Session.query(Admin).filter(
            Admin.user_id == update.message.from_user.id and
            Admin.group_id in [update.message.chat.id, None]).first()

        logging.debug("SILENCE STATE: State: {}, Group: {}, Admin: {}".format(
            get_game_state(),
            group.id if group else 'NO GROUP',
            admin,
        ))

        if group and group.silence_enabled and not admin and GameState.BATTLE_SILENCE in get_game_state():
            bot.delete_message(
                update.message.chat.id,
                update.message.message_id
            )

        if update.message.text:
            trigger_show(bot, update)

    elif update.effective_message.chat.type == 'private':
        admin = Session.query(Admin).filter_by(user_id=update.message.from_user.id).all()
        is_admin = False
        for _ in admin:
            is_admin = True
            break

        if 'order_wait' in chat_data and chat_data['order_wait']:
            order.manage(bot, update, user, chat_data=chat_data)
        elif update.message.text:
            if update.message.forward_from and update.message.forward_from.id == CWBOT_ID:
                parse_quest(bot, update, user)
            elif 'wait_group_name' in chat_data and chat_data['wait_group_name']:
                add(bot, update, user, chat_data=chat_data)
            elif not is_admin:
                profile.user_panel(bot, update)
            else:
                order.manage(bot, update, user, chat_data=chat_data)
        elif not is_admin:
            profile.user_panel(bot, update)
        else:
            order.manage(bot, update, user, chat_data=chat_data)