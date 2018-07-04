import json
import logging

from telegram import Bot, Update, TelegramError, ParseMode
from telegram.ext import run_async, JobQueue

from core.decorators import command_handler, create_or_update_user
from core.handler.callback.util import get_callback_action, Action, CallbackAction
from core.texts import MSG_TOP_GENERATING
from core.types import User
from core.utils import update_group

from functions.inline_markup import QueryType
from functions import order_groups
from functions import orders
from functions import profile
from functions import quest

from functions import squad
from functions.squad import admin as squad_admin

from functions.top import overall
from functions.top import squad as top_squad
from functions.top import classes as top_class

from functions.user.util import toggle_sniping, toggle_gold_hiding, toggle_deal_report, toggle_report, disable_api, \
    delete_admin

@run_async
@command_handler()
def callback_query(bot: Bot, update: Update, user:User, chat_data: dict, job_queue: JobQueue):
    try:
        # Update data...
        update_group(update.callback_query.message.chat)
        user = create_or_update_user(update.effective_user)

        # NEW
        if len(update.callback_query.data) == 36:
            logging.info("New Callback style: %s", update.callback_query.data)
            action = get_callback_action(update.callback_query.data, update.effective_user.id)
            if action and isinstance(action, Action):
                print(action)
                print(action.action)
                if CallbackAction.TOP in action.action:
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
                elif CallbackAction.QUEST_LOCATION in action.action:
                    quest.set_user_quest_location(bot, update, user)
                elif CallbackAction.FORAY_PLEDGE in action.action:
                    quest.set_user_foray_pledge(bot, update, user)
                elif CallbackAction.SQUAD_JOIN in action.action:
                    squad.join_squad_request(bot, update, user)
                elif CallbackAction.SQUAD_LEAVE in action.action:
                    squad.leave_squad_request(bot, update, user)
                elif CallbackAction.SQUAD_LIST in action.action:
                    squad_admin.list_squads(bot, update, user)
                elif CallbackAction.SQUAD_LIST_MEMBERS in action.action:
                    squad_admin.list_squad_members(bot, update, user)
                elif CallbackAction.HERO_EQUIP in action.action:
                    profile.show_equip(bot, update, user)
                elif CallbackAction.HERO_SKILL in action.action:
                    profile.show_skills(bot, update, user)
                elif CallbackAction.HERO_STOCK in action.action:
                    profile.inline_show_stock(bot, update, user)
                elif CallbackAction.HERO in action.action:
                    profile.inline_show_char(bot, update, user)
                else:
                    logging.warning("Unknown callback?")
            else:
                logging.warning("Action is not a valid action!")
                bot.edit_message_text(
                    text="<i>This message is no longer valid!</i>",
                    message_id=update.effective_message.message_id,
                    chat_id=update.effective_message.chat.id,
                    parse_mode=ParseMode.HTML,
                )

            # Done...
            return

        return

        # OLD way...
        data = json.loads(update.callback_query.data)
        if data['t'] == QueryType.GroupList.value:
            functions.squad.admin.group_list(bot, update, user, data)
        elif data['t'] == QueryType.GroupInfo.value:
            order_groups.group_info(bot, update, user, data)
        elif data['t'] == QueryType.DelAdm.value:
            delete_admin(bot, update, user, data)
        elif data['t'] == QueryType.Order.value:
            orders.order_button(bot, update, user, data, chat_data)
        elif data['t'] == QueryType.OrderOk.value:
            orders.inline_order_confirmed(bot, update, user, data, job_queue)
        elif data['t'] == QueryType.Orders.value:
            orders.inline_orders(bot, update, user, data, chat_data)
        elif data['t'] == QueryType.OrderGroup.value:
            order_groups.order_group(bot, update, user, data, chat_data)
        elif data['t'] == QueryType.OrderGroupManage.value:
            order_groups.order_group_manage(bot, update, user, data)
        elif data['t'] == QueryType.OrderGroupTriggerChat.value:
            order_groups.order_group_tirgger_chat(bot, update, user, data)
        elif data['t'] == QueryType.OrderGroupAdd.value:
            order_groups.order_group_add(bot, update, user, data, chat_data)
        elif data['t'] == QueryType.OrderGroupDelete.value:
            order_groups.order_group_delete(bot, update, user, data)
        elif data['t'] == QueryType.OrderGroupList.value:
            order_groups.order_group_list(bot, update)
        elif data['t'] == QueryType.RequestSquadAccept.value:
            functions.squad.admin.squad_request_accept(bot, update, user, data)
        elif data['t'] == QueryType.RequestSquadDecline.value:
            functions.squad.admin.squad_request_decline(bot, update, user, data)
        elif data['t'] == QueryType.InviteSquadAccept.value:
            functions.squad.admin.squad_invite_accept(bot, update, user, data)
        elif data['t'] == QueryType.InviteSquadDecline.value:
            functions.squad.admin.squad_invite_decline(bot, update, user, data)
        elif data['t'] == QueryType.TriggerOrderPin.value:
            orders.trigger_order_pin(bot, update, user, data, chat_data)
        elif data['t'] == QueryType.TriggerOrderButton.value:
            orders.trigger_order_button(bot, update, user, data, chat_data)
        elif data['t'] == QueryType.GroupDelete.value:
            functions.squad.admin.inline_squad_delete(bot, update, user, data)
        elif data['t'] == QueryType.DisableAPIAccess:
            disable_api(bot, update, user, data)
        elif data['t'] in [QueryType.EnableAutomatedReport, QueryType.DisableAutomatedReport]:
            toggle_report(bot, update, user, data)
        elif data['t'] in [QueryType.DisableDealReport, QueryType.EnableDealReport]:
            toggle_deal_report(bot, update, user, data)
        elif data['t'] in [QueryType.DisableHideGold, QueryType.EnableHideGold]:
            toggle_gold_hiding(bot, update, user, data)
        elif data['t'] in [QueryType.DisableSniping, QueryType.EnableSniping]:
            toggle_sniping(bot, update, user, data)
        elif data['t'] == QueryType.OtherReport.value:
            functions.squad.admin.other_report(bot, update, user, data)
        elif data['t'] == QueryType.BattleGlobalTop.value:
            update.callback_query.answer(text=MSG_TOP_GENERATING)
            #global_battle_top(bot, update)
        elif data['t'] == QueryType.BattleWeekTop.value:
            update.callback_query.answer(text=MSG_TOP_GENERATING)
            #week_battle_top(bot, update)

    except TelegramError as e:
        # Ignore Message is not modified errors
        if str(e) != "Message is not modified":
            raise e
