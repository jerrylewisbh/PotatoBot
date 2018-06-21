from core.chat_commands import *
from core.functions.activity import day_activity, week_activity, battle_activity
from core.functions.admins import list_admins, admins_for_users
from core.functions.common import help_msg, ping
from core.functions.common.pin import pin_all, not_pin_all
from core.functions.squad import open_hiring, close_hiring
from core.functions.triggers import set_trigger, del_trigger, list_triggers, enable_trigger_all, disable_trigger_all
from core.functions.welcome import set_welcome, show_welcome, enable_welcome, disable_welcome
from core.handlers.message_handler import MessageHandler, SimpleHandler, RegisteredOnlyHandler


def squad_handler(is_registered):
    return RegisteredOnlyHandler(
        message=CC_SQUAD,
        action=help_msg,
        is_registered=is_registered)


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
