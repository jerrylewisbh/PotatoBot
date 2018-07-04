import logging

from telegram.ext import Dispatcher, RegexHandler

from core.commands import *
from functions import orders
from functions.common import admin_panel
from functions.exchange.hide import hide_gold_info
from functions.exchange.snipe import sniping_info
from functions.order_groups import group_list
from functions.orders import orders
from functions.profile import user_panel, show_char, grant_access, settings
from functions.squad import (leave_squad_request, squad_about, join_squad_request)
from functions.squad.admin import list_squad_requests, battle_attendance_show, \
    battle_reports_show, send_status, remove_from_squad, list_squads
from functions.statistics import statistic_about, exp_statistic, skill_statistic, quest_statistic, item_statistic
from functions.statistics.foray import foray_statistic

from functions.top import overall as top_overall, top_about
from functions.top import squad as top_squad
from functions.top import classes as top_class


def to_re(string):
    return "^{}$".format(string)


def add_handler(disp: Dispatcher):
    # NOTE: Use the @command_handler decorator for the functions registered here! This will provide you with the User
    # object and additionally filters by chat-type (private, group, etc.)

    logging.debug("Starting adding command handlers")
    # on different commands - answer in Telegram
    disp.add_handler(RegexHandler(to_re(USER_COMMAND_BACK), user_panel))

    disp.add_handler(RegexHandler(to_re(ADMIN_COMMAND_ORDER), orders, pass_chat_data=True))
    disp.add_handler(RegexHandler(to_re(ADMIN_COMMAND_STATUS), send_status))
    disp.add_handler(RegexHandler(to_re(ADMIN_COMMAND_GROUPS), group_list))
    disp.add_handler(RegexHandler(to_re(ADMIN_COMMAND_RECRUIT), list_squad_requests))
    disp.add_handler(RegexHandler(to_re(ADMIN_COMMAND_FIRE_UP), remove_from_squad))
    disp.add_handler(RegexHandler(to_re(ADMIN_COMMAND_SQUAD_LIST), list_squads))
    disp.add_handler(RegexHandler(to_re(ADMIN_COMMAND_ADMINPANEL), admin_panel))
    disp.add_handler(RegexHandler(to_re(ADMIN_COMMAND_REPORTS), battle_reports_show))
    disp.add_handler(RegexHandler(to_re(ADMIN_COMMAND_ATTENDANCE), battle_attendance_show))
    disp.add_handler(RegexHandler(to_re(USER_COMMAND_ME), show_char))
    disp.add_handler(RegexHandler(to_re(USER_COMMAND_SQUAD), squad_about))
    disp.add_handler(RegexHandler(to_re(USER_COMMAND_STATISTICS), statistic_about))
    disp.add_handler(RegexHandler(to_re(USER_COMMAND_SQUAD_REQUEST), join_squad_request))
    disp.add_handler(RegexHandler(to_re(USER_COMMAND_SQUAD_LEAVE), leave_squad_request))
    disp.add_handler(RegexHandler(to_re(USER_COMMAND_REGISTER), grant_access))
    # disp.add_handler(RegexHandler(to_re(USER_COMMAND_REGISTER_CONTINUE),
    disp.add_handler(RegexHandler(to_re(USER_COMMAND_SETTINGS), settings))
    disp.add_handler(RegexHandler(to_re(USER_COMMAND_EXCHANGE), sniping_info))
    disp.add_handler(RegexHandler(to_re(USER_COMMAND_HIDE), hide_gold_info))

    # Top
    disp.add_handler(RegexHandler(to_re(USER_COMMAND_TOP), top_about))
    disp.add_handler(RegexHandler(to_re(TOP_COMMAND_GLOBAL), top_overall.top))
    disp.add_handler(RegexHandler(to_re(TOP_COMMAND_CLASS), top_class.top))
    disp.add_handler(RegexHandler(to_re(TOP_COMMAND_SQUAD), top_squad.top))

    disp.add_handler(RegexHandler(to_re(STATISTICS_COMMAND_EXP), exp_statistic))
    disp.add_handler(RegexHandler(to_re(STATISTICS_COMMAND_QUESTS), quest_statistic))
    disp.add_handler(RegexHandler(to_re(STATISTICS_COMMAND_QUESTS_ALL), quest_statistic))
    disp.add_handler(RegexHandler(to_re(STATISTICS_COMMAND_ITEMS_ALL), item_statistic))
    disp.add_handler(RegexHandler(to_re(STATISTICS_COMMAND_FORAY), foray_statistic))
    disp.add_handler(RegexHandler(to_re(STATISTICS_COMMAND_SKILLS), skill_statistic))

    logging.info("Finished adding button handlers")
