from functions.activity import day_activity, week_activity, battle_activity
from functions.admins import list_admins, admins_for_users
from functions.common import help_msg, ping, delete_msg, delete_user
from functions.squad import open_hiring, close_hiring
from functions.triggers import set_trigger, del_trigger, list_triggers, enable_trigger_all, disable_trigger_all
from functions.welcome import set_welcome, show_welcome, enable_welcome, disable_welcome

from core.chat_commands import *
from core.handlers.message_handler import MessageHandler, SimpleHandler
from functions.common.pin import pin_all, not_pin_all, pin, silent_pin


def squad_handler(is_registered):
    return SimpleHandler(
        message=CC_SQUAD,
        action=help_msg)


welcome_handler = MessageHandler(
    condition=lambda msg: msg.startswith(CC_SET_WELCOME),
    action=set_welcome)

help_handler = SimpleHandler(
    message=CC_HELP,
    action=help_msg)

show_welcome_handler = SimpleHandler(
    message=CC_SHOW_WELCOME,
    action=show_welcome)

enable_welcome_handler = SimpleHandler(
    message=CC_TURN_ON_WELCOME,
    action=enable_welcome)

disable_welcome_handler = SimpleHandler(
    message=CC_TURN_OFF_WELCOME,
    action=disable_welcome)

set_trigger_handler = SimpleHandler(
    message=CC_SET_TRIGGER,
    action=set_trigger)

del_trigger_handler = SimpleHandler(
    message=CC_UNSET_TRIGGER,
    action=del_trigger)

list_triggers_handler = SimpleHandler(
    message=CC_TRIGGER_LIST,
    action=list_triggers)

list_admins_handler = SimpleHandler(
    message=CC_ADMIN_LIST,
    action=list_admins)

ping_handler = SimpleHandler(
    message=CC_PING,
    action=ping)

day_activity_handler = SimpleHandler(
    message=CC_DAY_STATISTICS,
    action=day_activity)

week_activity_handler = SimpleHandler(
    message=CC_WEEK_STATISTICS,
    action=week_activity)

battle_activity_handler = SimpleHandler(
    message=CC_BATTLE_STATISTICS,
    action=battle_activity)

enable_trigger_all_handler = SimpleHandler(
    message=CC_ALLOW_TRIGGER_ALL,
    action=enable_trigger_all)

disable_trigger_all_handler = SimpleHandler(
    message=CC_DISALLOW_TRIGGER_ALL,
    action=disable_trigger_all)

admins_for_users_handler = SimpleHandler(
    message=CC_ADMINS,
    action=admins_for_users)

pin_all_handler = SimpleHandler(
    message=CC_ALLOW_PIN_ALL,
    action=pin_all)

not_pin_all_handler = SimpleHandler(
    message=CC_DISALLOW_PIN_ALL,
    action=not_pin_all)

open_hiring_handler = SimpleHandler(
    message=CC_OPEN_HIRING,
    action=open_hiring)

close_hiring_handler = SimpleHandler(
    message=CC_CLOSE_HIRING,
    action=close_hiring)

pin_handler = SimpleHandler(
    message=CC_PIN,
    action=pin)

silent_pin_handler = SimpleHandler(
    message=CC_SILENT_PIN,
    action=silent_pin)

delete_msg_handler = SimpleHandler(
    message=CC_DELETE,
    action=delete_msg)

delete_user_handler = SimpleHandler(
    message=CC_KICK,
    action=delete_user)

group_reply_handlers = [
    pin_handler,
    silent_pin_handler,
    delete_msg_handler,
    delete_user_handler
]
