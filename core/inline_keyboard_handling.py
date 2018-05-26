from core.inline_markup import *
from core.order import inline_handler as order
from core.profile import inline_handler as profile
from core.quest import inline_handler as quest
from core.squad import inline_handler as squad
from telegram import Update, InlineQueryResultArticle, \
    InputTextMessageContent, TelegramError
from telegram.ext import JobQueue
from telegram.ext.dispatcher import run_async

from core.enums import CASTLE_LIST, TACTICTS_COMMAND_PREFIX
from core.texts import *
from core.types import *
from core.utils import update_group, add_user
from group import inline_handler as group
from misc.top import global_build_top, week_build_top, week_battle_top, global_battle_top, \
    week_squad_build_top, global_squad_build_top


@run_async
@user_allowed
def callback_query(bot: Bot, update: Update, session, chat_data: dict, job_queue: JobQueue):
    try:
        update_group(update.callback_query.message.chat, session)
        user = add_user(update.effective_user, session)
        data = json.loads(update.callback_query.data)

        # Profile stuff...
        if data['t'] == QueryType.ShowEquip:
            profile.equip_show(bot, data, session, update)
        elif data['t'] == QueryType.ShowSkills:
            profile.skills_show(bot, data, session, update)
        elif data['t'] == QueryType.ShowStock:
            profile.stock_show(bot, data, session, update)
        elif data['t'] == QueryType.ShowHero.value:
            profile.hero_show(bot, data, session, update)
        elif data['t'] == QueryType.DisableAPIAccess:
            profile.setting_api_disable(bot, data, session, update)
        elif data['t'] in [QueryType.EnableAutomatedReport, QueryType.DisableAutomatedReport]:
            profile.setting_report_toggle(bot, data, session, update)
        elif data['t'] in [QueryType.DisableDealReport, QueryType.EnableDealReport]:
            profile.setting_deal_toggle(bot, data, session, update)

        # Squad stuff
        elif data['t'] == QueryType.MemberList:
            squad.list_members(bot, data, session, update)
        elif data['t'] == QueryType.LeaveSquad.value:
            squad.leave(bot, data, session, update, user)
        elif data['t'] == QueryType.RequestSquad.value:
            squad.request_join(bot, data, session, update, user)
        elif data['t'] == QueryType.RequestSquadAccept.value:
            squad.member_accept(bot, data, session, update)
        elif data['t'] == QueryType.RequestSquadDecline.value:
            squad.member_decline(bot, data, session, update)
        elif data['t'] == QueryType.InviteSquadAccept.value:
            squad.invite_accept(bot, data, session, update)
        elif data['t'] == QueryType.InviteSquadDecline.value:
            squad.invite_decline(bot, data, session, update)
        elif data['t'] == QueryType.Yes:
            squad.leave_squad(bot, user, user.member, update.effective_message, session)
        elif data['t'] == QueryType.No:
            squad.leave_squad_no(bot, update)
        elif data['t'] == QueryType.SquadList:
            squad.list_members(bot, session, update)
        elif data['t'] == QueryType.OtherReport:
            squad.report(bot, data, session, update)

        # Groups
        elif data['t'] == QueryType.GroupInfo:
            group.group_info(bot, data, session, update)
        elif data['t'] == QueryType.DelAdm:
            group.admin_delete(bot, data, session, update)
        elif data['t'] == QueryType.GroupList:
            list(bot, session, update)
        elif data['t'] == QueryType.GroupDelete:
            # First... Ask to delete squad...
            # Fixme: The code was referring to squads and message sending before refactoring... O_o
            #squad.delete(bot, data, session)
            #list(bot, session, update)
            print("HAS THIS EVER WORKED!?")
        # Orders
        elif data['t'] == QueryType.Order:
            order(bot, chat_data, data, session, update)
        elif data['t'] == QueryType.OrderOk:
            order.order_okay(data, job_queue, session, update)
        elif data['t'] == QueryType.Orders:
            order.order_wait(bot, chat_data, data, session, update)
        elif data['t'] == QueryType.OrderGroup:
            order.order_group(bot, chat_data, data, session, update)
        elif data['t'] == QueryType.OrderGroupManage:
            order.order_group_manage(bot, data, session, update)
        elif data['t'] == QueryType.OrderGroupTriggerChat:
            order.group_trigger_chat(bot, data, session, update)
        elif data['t'] == QueryType.OrderGroupAdd:
            group.order_group_add(bot, chat_data, update)
        elif data['t'] == QueryType.OrderGroupDelete:
            order.order_group_delete(bot, data, session, update)
        elif data['t'] == QueryType.OrderGroupList:
            order.order_group_list(bot, session, update)
        elif data['t'] == QueryType.TriggerOrderPin:
            order.order_trigger_pin(bot, chat_data, data, session, update)
        elif data['t'] == QueryType.TriggerOrderButton.value:
            order.order_trigger_button(bot, chat_data, data, session, update)

        # Statistics and other stuff...
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

        # Quests
        elif data['t'] == QueryType.QuestFeedbackRequired:
            quest.quest_feedback_required(bot, data, session, update)
    except TelegramError as e:
        # Ignore Message is not modified errors
        if str(e) != "Message is not modified":
            raise e


def inlinequery(_bot, update):
    """Handle the inline query."""
    query = update.inline_query.query
    if query not in CASTLE_LIST and not query.startswith(TACTICTS_COMMAND_PREFIX):
        return

    results = [
        InlineQueryResultArticle(
            id=0,
            title=("DEFEND " if Castle.BLUE.value == query or query.startswith(
                TACTICTS_COMMAND_PREFIX) else "ATTACK ") + query,
            input_message_content=InputTextMessageContent(query))]

    update.inline_query.answer(results)
