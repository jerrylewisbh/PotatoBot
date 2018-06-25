import json

from telegram import Bot, Update, TelegramError
from telegram.ext import run_async, JobQueue

from core.decorators import command_handler
from core.texts import MSG_TOP_GENERATING
from core.types import User
from core.utils import update_group, create_or_update_user
from functions.admins import delete_admin
from functions.inline_markup import QueryType
from functions.order_groups import group_info, order_group, order_group_manage, order_group_tirgger_chat, \
    order_group_add, order_group_delete, order_group_list
from functions.orders import order_button, inline_order_confirmed, inline_orders, trigger_order_pin, \
    trigger_order_button
from functions.profile import show_equip, show_skills, show_stock, show_hero
from functions.quest import set_user_quest_location, set_user_foray_pledge
from functions.squad import group_list, inline_list_squad_members, squad_leave, inline_squad_request, \
    squad_request_accept, squad_request_decline, squad_invite_accept, squad_invite_decline, inline_squad_list, \
    inline_squad_delete, other_report, leave_squad, squad_leave_no
from functions.top import global_build_top, week_build_top, global_squad_build_top, week_squad_build_top, \
    global_battle_top, week_battle_top
from functions.user import disable_api, toggle_report, toggle_deal_report, toggle_gold_hiding, toggle_sniping


@run_async
@command_handler()
def callback_query(bot: Bot, update: Update, user:User, chat_data: dict, job_queue: JobQueue):
    try:
        update_group(update.callback_query.message.chat)

        user = create_or_update_user(update.effective_user)

        data = json.loads(update.callback_query.data)
        if data['t'] == QueryType.GroupList.value:
            group_list(bot, update, user, data)
        elif data['t'] == QueryType.GroupInfo.value:
            group_info(bot, update, user, data)
        elif data['t'] == QueryType.DelAdm.value:
            delete_admin(bot, update, user, data)
        elif data['t'] == QueryType.Order.value:
            order_button(bot, update, user, data, chat_data)
        elif data['t'] == QueryType.OrderOk.value:
            inline_order_confirmed(bot, update, user, data, job_queue)
        elif data['t'] == QueryType.Orders.value:
            inline_orders(bot, update, user, data, chat_data)
        elif data['t'] == QueryType.OrderGroup.value:
            order_group(bot, update, user, data, chat_data)
        elif data['t'] == QueryType.OrderGroupManage.value:
            order_group_manage(bot, update, user, data)
        elif data['t'] == QueryType.OrderGroupTriggerChat.value:
            order_group_tirgger_chat(bot, update, user, data)
        elif data['t'] == QueryType.OrderGroupAdd.value:
            order_group_add(bot, update, user, data, chat_data)
        elif data['t'] == QueryType.OrderGroupDelete.value:
            order_group_delete(bot, update, user, data)
        elif data['t'] == QueryType.OrderGroupList.value:
            order_group_list(bot, update)
        elif data['t'] == QueryType.ShowEquip.value:
            show_equip(bot, update, user, data)
        elif data['t'] == QueryType.ShowSkills.value:
            show_skills(bot, update, user, data)
        elif data['t'] == QueryType.ShowStock.value:
            show_stock(bot, update, user, data)
        elif data['t'] == QueryType.ShowHero.value:
            show_hero(bot, update, user, data)
        elif data['t'] == QueryType.MemberList.value:
            inline_list_squad_members(bot, update, user, data)
        elif data['t'] == QueryType.LeaveSquad.value:
            squad_leave(bot, data, update, user)
        elif data['t'] == QueryType.RequestSquad.value:
            inline_squad_request(bot, data, update, user)
        elif data['t'] == QueryType.RequestSquadAccept.value:
            squad_request_accept(bot, update, user, data)
        elif data['t'] == QueryType.RequestSquadDecline.value:
            squad_request_decline(bot, update, user, data)
        elif data['t'] == QueryType.InviteSquadAccept.value:
            squad_invite_accept(bot, update, user, data)
        elif data['t'] == QueryType.InviteSquadDecline.value:
            squad_invite_decline(bot, update, user, data)
        elif data['t'] == QueryType.TriggerOrderPin.value:
            trigger_order_pin(bot, update, user, data, chat_data)
        elif data['t'] == QueryType.TriggerOrderButton.value:
            trigger_order_button(bot, update, user, data, chat_data)
        elif data['t'] == QueryType.SquadList.value:
            inline_squad_list(bot, update)
        elif data['t'] == QueryType.GroupDelete.value:
            inline_squad_delete(bot, update, user, data)
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
            other_report(bot, update, user, data)
        elif data['t'] == QueryType.GlobalBuildTop.value:
            update.callback_query.answer(text=MSG_TOP_GENERATING)
            global_build_top(bot, update)
        elif data['t'] == QueryType.WeekBuildTop.value:
            update.callback_query.answer(text=MSG_TOP_GENERATING)
            week_build_top(bot, update)
        elif data['t'] == QueryType.SquadGlobalBuildTop.value:
            update.callback_query.answer(text=MSG_TOP_GENERATING)
            global_squad_build_top(bot, update)
        elif data['t'] == QueryType.SquadWeekBuildTop.value:
            update.callback_query.answer(text=MSG_TOP_GENERATING)
            week_squad_build_top(bot, update)
        elif data['t'] == QueryType.BattleGlobalTop.value:
            update.callback_query.answer(text=MSG_TOP_GENERATING)
            global_battle_top(bot, update)
        elif data['t'] == QueryType.BattleWeekTop.value:
            update.callback_query.answer(text=MSG_TOP_GENERATING)
            week_battle_top(bot, update)
        elif data['t'] == QueryType.Yes.value:
            leave_squad(bot, user, user.member, update.effective_message)
        elif data['t'] == QueryType.No.value:
            squad_leave_no(bot, update)
        elif data['t'] == QueryType.QuestFeedbackRequired:
            set_user_quest_location(bot, update, user, data)
        elif data['t'] == QueryType.ForayFeedbackRequired:
            set_user_foray_pledge(bot, update, user, data)

    except TelegramError as e:
        # Ignore Message is not modified errors
        if str(e) != "Message is not modified":
            raise e
