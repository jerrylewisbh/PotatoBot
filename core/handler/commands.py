import logging

from telegram.ext import CommandHandler, Dispatcher

from functions.battle import call_ready_to_battle_result
from functions.user import set_admin, del_admin, list_admins, set_global_admin, set_super_admin, del_global_admin
from functions.common import admin_panel, ban, help_msg, ping, unban, get_log, force_kick_botato, kick_from_chat
from functions.exchange import list_items, list_items_other, list_items_unknown
from functions.exchange.hide import auto_hide, hide_items, hide_list
from functions.exchange.snipe import sniping, sniping_remove, sniping_resume
from functions.guild.stock import deposit, withdraw_help
from functions.profile import (find_by_character, find_by_id,
                               find_by_username, grant_access, revoke,
                               show_char, show_report, user_panel)
from functions.squad.admin.commands import enable_thorns, enable_reminders, enable_silence, disable_thorns, \
    disable_silence, disable_reminders, add_squad, set_invite_link, set_squad_name, del_squad, force_add_to_squad, \
    add_to_squad
from functions.triggers import (add_global_trigger, add_trigger,
                                del_global_trigger, del_trigger,
                                disable_trigger_all, enable_trigger_all,
                                list_triggers, set_global_trigger,
                                set_trigger)
from functions.welcome import (disable_welcome, enable_welcome,
                               set_welcome, show_welcome)


def add_handler(disp: Dispatcher):
    # NOTE: Use the @command_handler decorator for the functions registered here! This will provide you with the User
    # object and additionally filters by chat-type (private, group, etc.)

    logging.debug("Starting adding button handlers")

    disp.add_handler(CommandHandler("start", user_panel))

    # on different commands - answer in Telegram
    disp.add_handler(CommandHandler("admin", admin_panel))
    disp.add_handler(CommandHandler("help", help_msg))
    disp.add_handler(CommandHandler("ping", ping))
    disp.add_handler(CommandHandler("set_global_trigger", set_global_trigger))
    disp.add_handler(CommandHandler("add_global_trigger", add_global_trigger))
    disp.add_handler(CommandHandler("del_global_trigger", del_global_trigger))
    disp.add_handler(CommandHandler("set_trigger", set_trigger))
    disp.add_handler(CommandHandler("add_trigger", add_trigger))
    disp.add_handler(CommandHandler("del_trigger", del_trigger))
    disp.add_handler(CommandHandler("list_triggers", list_triggers))
    disp.add_handler(CommandHandler("set_welcome", set_welcome))
    disp.add_handler(CommandHandler("enable_welcome", enable_welcome))
    disp.add_handler(CommandHandler("disable_welcome", disable_welcome))
    disp.add_handler(CommandHandler("show_welcome", show_welcome))
    disp.add_handler(CommandHandler("add_admin", set_admin))
    disp.add_handler(CommandHandler("add_global_admin", set_global_admin))
    disp.add_handler(CommandHandler("del_global_admin", del_global_admin))
    disp.add_handler(CommandHandler("add_super_admin", set_super_admin))
    disp.add_handler(CommandHandler("del_admin", del_admin))
    disp.add_handler(CommandHandler("list_admins", list_admins))

    disp.add_handler(CommandHandler("force_kick_botato", force_kick_botato))  # Force Botato to remove himself from chat.
    disp.add_handler(CommandHandler("kick", kick_from_chat))  # Force Botato to remove himself from chat.

    disp.add_handler(CommandHandler("enable_trigger", enable_trigger_all))
    disp.add_handler(CommandHandler("disable_trigger", disable_trigger_all))
    disp.add_handler(CommandHandler("grant_access", grant_access))

    # Squad / Group things
    disp.add_handler(CommandHandler("enable_thorns", enable_thorns))
    disp.add_handler(CommandHandler("enable_silence", enable_silence))
    disp.add_handler(CommandHandler("enable_reminders", enable_reminders))
    disp.add_handler(CommandHandler("disable_thorns", disable_thorns))
    disp.add_handler(CommandHandler("disable_silence", disable_silence))
    disp.add_handler(CommandHandler("disable_reminders", disable_reminders))
    disp.add_handler(CommandHandler("set_squad_name", set_squad_name))
    disp.add_handler(CommandHandler("set_invite_link", set_invite_link))
    disp.add_handler(CommandHandler("add_squad", add_squad))
    disp.add_handler(CommandHandler("del_squad", del_squad))
    disp.add_handler(CommandHandler("add", add_to_squad))
    disp.add_handler(CommandHandler("forceadd", force_add_to_squad))

    disp.add_handler(CommandHandler("find", find_by_username))
    disp.add_handler(CommandHandler("findc", find_by_character))
    disp.add_handler(CommandHandler("findi", find_by_id))
    disp.add_handler(CommandHandler("ban", ban))
    disp.add_handler(CommandHandler("unban", unban))
    disp.add_handler(CommandHandler("get_log", get_log))

    # User/Profile specific
    disp.add_handler(CommandHandler("me", show_char))
    disp.add_handler(CommandHandler("report", show_report))

    # Exchange Stuff...
    disp.add_handler(CommandHandler('ah', auto_hide, pass_args=True))
    disp.add_handler(CommandHandler('s', sniping, pass_args=True))
    disp.add_handler(CommandHandler('sr', sniping_remove, pass_args=True))
    disp.add_handler(CommandHandler('resume', sniping_resume))
    disp.add_handler(CommandHandler('items', list_items))
    disp.add_handler(CommandHandler('items_other', list_items_other))
    disp.add_handler(CommandHandler('items_unknown', list_items_unknown))
    disp.add_handler(CommandHandler('hide', hide_items))
    disp.add_handler(CommandHandler('hide_list', hide_list))
    disp.add_handler(CommandHandler('revoke', revoke))

    disp.add_handler(CommandHandler('deposit', deposit))
    disp.add_handler(CommandHandler('withdraw', withdraw_help))
    disp.add_handler(CommandHandler('battleresult', call_ready_to_battle_result))

    logging.info("Finished adding button handlers")
