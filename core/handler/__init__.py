import logging

from telegram import Bot, Update
from telegram.ext import run_async

from config import CWBOT_ID
from core.decorators import command_handler
from core.state import get_game_state, GameState
from core.types import User, Session, Squad, Admin
from functions.order_groups import add_group
from functions.orders import order
from functions.profile import user_panel
from functions.quest import parse_quest
from functions.report import fwd_report
from functions.triggers import trigger_show


# noinspection PyCallingNonCallable
@run_async
@command_handler(
    allow_channel=True,
    allow_group=True,
    allow_private=True
)
def manage_all(bot: Bot, update: Update, user: User, chat_data, job_queue):#
    if update.effective_message.chat.type == "channel":
        fwd_report(bot, update)
    elif update.effective_message.chat.type in ['group', 'supergroup']:
        squad = Session.query(Squad).filter_by(chat_id=update.message.chat.id).first()

        admin = Session.query(Admin).filter(
            Admin.user_id == update.message.from_user.id and
            Admin.admin_group in [update.message.chat.id, 0]).first()

        logging.debug("SILENCE STATE: State: {}, Squad: {}, Admin: {}".format(
            get_game_state(),
            squad.squad_name if squad else 'NO SQUAD',
            admin,
        ))

        if squad and squad.silence_enabled and not admin and GameState.BATTLE_SILENCE in get_game_state():
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
            order(bot, update, user, chat_data=chat_data)
        elif update.message.text:
            if update.message.forward_from and update.message.forward_from.id == CWBOT_ID:
                parse_quest(bot, update, user)
            elif 'wait_group_name' in chat_data and chat_data['wait_group_name']:
                add_group(bot, update, user, chat_data=chat_data)
            elif not is_admin:
                user_panel(bot, update)
            else:
                order(bot, update, user, chat_data=chat_data)
        elif not is_admin:
            user_panel(bot, update)
        else:
            order(bot, update, user, chat_data=chat_data)
