from telegram.ext import Dispatcher, CommandHandler

from core.functions.admins import set_admin, set_global_admin, del_global_admin, set_super_admin, del_admin, list_admins
from core.functions.ban import unban, ban
from core.functions.common import (
    help_msg, ping, kick,
    admin_panel, user_panel)
from core.functions.profile import char_show, grant_access, find_by_username, find_by_character, find_by_id, revoke
from core.functions.squad import add_squad, del_squad, enable_thorns, enable_silence, enable_reminders, disable_thorns, \
    disable_silence, disable_reminders, set_squad_name, set_invite_link, add_to_squad, force_add_to_squad
from core.functions.triggers import set_global_trigger, add_global_trigger, del_global_trigger, set_trigger, \
    add_trigger, del_trigger, list_triggers, enable_trigger_all, disable_trigger_all
from core.functions.welcome import set_welcome, enable_welcome, disable_welcome, show_welcome


def add_triggers(disp: Dispatcher):
    # on different commands - answer in Telegram
    disp.add_handler(CommandHandler("start", user_panel))
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
    disp.add_handler(CommandHandler("kick", kick))
    disp.add_handler(CommandHandler("enable_trigger", enable_trigger_all))
    disp.add_handler(CommandHandler("disable_trigger", disable_trigger_all))
    disp.add_handler(CommandHandler("me", char_show))
    disp.add_handler(CommandHandler("grant_access", grant_access))
    disp.add_handler(CommandHandler("add_squad", add_squad))
    disp.add_handler(CommandHandler("del_squad", del_squad))
    disp.add_handler(CommandHandler("enable_thorns", enable_thorns))
    disp.add_handler(CommandHandler("enable_silence", enable_silence))
    disp.add_handler(CommandHandler("enable_reminders", enable_reminders))
    disp.add_handler(CommandHandler("disable_thorns", disable_thorns))
    disp.add_handler(CommandHandler("disable_silence", disable_silence))
    disp.add_handler(CommandHandler("disable_reminders", disable_reminders))
    disp.add_handler(CommandHandler("set_squad_name", set_squad_name))
    disp.add_handler(CommandHandler("set_invite_link", set_invite_link))
    disp.add_handler(CommandHandler("find", find_by_username))
    disp.add_handler(CommandHandler("findc", find_by_character))
    disp.add_handler(CommandHandler("findi", find_by_id))
    disp.add_handler(CommandHandler("add", add_to_squad))
    disp.add_handler(CommandHandler("forceadd", force_add_to_squad))
    disp.add_handler(CommandHandler("ban", ban))
    disp.add_handler(CommandHandler("unban", unban))
    disp.add_handler(CommandHandler("revoke", revoke))
