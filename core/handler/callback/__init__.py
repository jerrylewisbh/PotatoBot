import logging
from telegram import Update, TelegramError, ParseMode
from telegram.ext import run_async, JobQueue

from core.bot import MQBot
from core.decorators import command_handler, create_or_update_user
from core.handler.callback.util import get_callback_action, Action, CallbackAction
from core.types import User
from core.utils import update_group
from functions import group
from functions import order
from functions import profile
from functions.quest import handler as quest_handler
from functions import squad
from functions import user as user_functions
from functions.order import groups as order_group
from functions.squad import admin as squad_admin
from functions.squad.admin import battle_reports_inline
from functions.top import classes as top_class
from functions.top import overall
from functions.top import squad as top_squad


@run_async
@command_handler()
def callback_query(bot: MQBot, update: Update, user: User, chat_data: dict, job_queue: JobQueue):
    try:
        # Update data...
        update_group(update.callback_query.message.chat)
        user = create_or_update_user(update.effective_user)

        logging.debug("New Callback style: %s", update.callback_query.data)
        action = get_callback_action(update.callback_query.data, update.effective_user.id)
        if action and isinstance(action, Action):
            # Order stuff...
            if CallbackAction.ORDER in action.action:
                order.manage(bot, update, user, chat_data=chat_data)
            elif CallbackAction.ORDER_GIVE in action.action:
                order.send_order(bot, update, user, chat_data=chat_data)
            elif CallbackAction.ORDER_CONFIRM in action.action:
                order.inline_order_confirmed(bot, update, user, job_queue)
            # Top
            elif CallbackAction.TOP in action.action:
                # Top Lists....
                if CallbackAction.TOP_FILTER_SQUAD in action.action:
                    logging.info("Inline Query: Calling squad.top")
                    top_squad.top(bot, update, user)
                elif CallbackAction.TOP_FILTER_CLASS in action.action:
                    logging.info("Inline Query: Calling classes.top")
                    top_class.top(bot, update, user)
                else:
                    logging.info("Inline Query: Calling top.top")
                    overall.top(bot, update, user)

            # Quest
            elif CallbackAction.QUEST_LOCATION in action.action:
                quest_handler.set_user_quest_location(bot, update, user)
            elif CallbackAction.FORAY_PLEDGE in action.action:
                quest_handler.set_user_foray_pledge(bot, update, user)

            # Squad...
            elif CallbackAction.SQUAD_INVITE in action.action:
                squad.squad_invite(bot, update, user)
            elif CallbackAction.SQUAD_JOIN in action.action:
                squad.join_squad_request(bot, update, user)
            elif CallbackAction.SQUAD_LEAVE in action.action:
                squad.leave_squad_request(bot, update, user)
            elif CallbackAction.SQUAD_LIST in action.action:
                squad_admin.list_squads(bot, update, user)
            elif CallbackAction.SQUAD_LIST_MEMBERS in action.action:
                squad_admin.list_squad_members(bot, update, user)
            elif CallbackAction.SQUAD_MANAGE in action.action:
                squad_admin.manage(bot, update, user)
            elif CallbackAction.REPORT in action.action:
                battle_reports_inline(bot, update, user)

            # Profile
            elif CallbackAction.HERO_EQUIP in action.action:
                profile.show_equip(bot, update, user)
            elif CallbackAction.HERO_SKILL in action.action:
                profile.show_skills(bot, update, user)
            elif CallbackAction.HERO_STOCK in action.action:
                profile.inline_show_stock(bot, update, user)
            elif CallbackAction.HERO in action.action:
                profile.inline_show_char(bot, update, user)
            elif CallbackAction.SETTING in action.action:
                user_functions.settings(bot, update, user)

            # Order Groups
            elif CallbackAction.ORDER_GROUP in action.action:
                order_group.list(bot, update, user)
            elif CallbackAction.ORDER_GROUP_ADD in action.action:
                order_group.add(bot, update, user, chat_data=chat_data)
            elif CallbackAction.ORDER_GROUP_MANAGE in action.action:
                order_group.manage(bot, update, user)

            # Groups
            elif CallbackAction.GROUP in action.action:
                group.list(bot, update, user)
            elif CallbackAction.GROUP_INFO in action.action:
                group.info(bot, update, user)
            elif CallbackAction.GROUP_MANAGE in action.action:
                group.manage(bot, update, user)
        else:
            logging.warning("Action is not a valid action!")
            bot.edit_message_text(
                text="<i>This message is no longer valid!</i>",
                message_id=update.effective_message.message_id,
                chat_id=update.effective_message.chat.id,
                parse_mode=ParseMode.HTML,
            )
    except TelegramError as e:
        # Ignore Message is not modified errors
        if str(e) != "Message is not modified":
            raise e
