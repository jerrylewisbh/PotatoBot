import logging

from core.commands import *
from functions import order
from functions.admin import admin_panel
from functions.common import help_intro, tools, tindertato
from functions.exchange.auction import auction_info
from functions.exchange.hide import hide_gold_info
from functions.exchange.snipe import sniping_info, list_snipes
from functions.group import list
from functions.guild import guild_info
from functions.order import groups
from functions.profile import user_panel, show_char, grant_access, settings
from functions.squad import (leave_squad_request, squad_about, join_squad_request)
from functions.squad.admin import list_requests, battle_attendance_show, \
    battle_reports, list_squads
from functions.statistics import statistic_about, exp_statistic, skill_statistic, quest_statistic, item_statistic
from functions.statistics.foray import foray_statistic, foray_interval
from functions.top import classes as top_class
from functions.top import overall as top_overall, top_about
from telegram.ext import Dispatcher, RegexHandler

from functions.top import squad as top_squad


def to_re(string):
    return "^{}$".format(string)


def add_handler(disp: Dispatcher):
    # NOTE: Use the @command_handler decorator for the functions registered here! This will provide you with the User
    # object and additionally filters by chat-type (private, group, etc.)

    logging.debug("Starting adding command handlers")
    # on different commands - answer in Telegram
    disp.add_handler(RegexHandler(to_re(USER_COMMAND_BACK), user_panel))

    disp.add_handler(RegexHandler(to_re(ADMIN_COMMAND_ORDER), order.select_orders, pass_chat_data=True))
    disp.add_handler(RegexHandler(to_re(ADMIN_COMMAND_STATUS), list))
    disp.add_handler(RegexHandler(to_re(ADMIN_COMMAND_GROUPS), groups.list))
    disp.add_handler(RegexHandler(to_re(ADMIN_COMMAND_RECRUIT), list_requests))
    #disp.add_handler(RegexHandler(to_re(ADMIN_COMMAND_FIRE_UP), remove_from_squad))
    disp.add_handler(RegexHandler(to_re(ADMIN_COMMAND_SQUAD_LIST), list_squads))
    disp.add_handler(RegexHandler(to_re(ADMIN_COMMAND_SNIPE_LIST), list_snipes))
    disp.add_handler(RegexHandler(to_re(ADMIN_COMMAND_ADMINPANEL), admin_panel))
    disp.add_handler(RegexHandler(to_re(ADMIN_COMMAND_REPORTS), battle_reports))
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
    disp.add_handler(RegexHandler(to_re(USER_COMMAND_AUCTION), auction_info))
    disp.add_handler(RegexHandler(to_re(USER_COMMAND_HIDE), hide_gold_info))
    disp.add_handler(RegexHandler(to_re((USER_COMMAND_HELP)), help_intro))
    disp.add_handler(RegexHandler(to_re((USER_COMMAND_TOOLS)), tools))
    disp.add_handler(RegexHandler(to_re((USER_COMMAND_GUILD)), guild_info))
    disp.add_handler(RegexHandler(to_re((USER_COMMAND_TEMP)), tindertato))

    # Top
    disp.add_handler(RegexHandler(to_re(USER_COMMAND_TOP), top_about))
    disp.add_handler(RegexHandler(to_re(TOP_COMMAND_GLOBAL), top_overall.top))
    disp.add_handler(RegexHandler(to_re(TOP_COMMAND_CLASS), top_class.top))
    disp.add_handler(RegexHandler(to_re(TOP_COMMAND_SQUAD), top_squad.top))

    disp.add_handler(RegexHandler(to_re(STATISTICS_COMMAND_EXP), exp_statistic))
    disp.add_handler(RegexHandler(to_re(STATISTICS_COMMAND_QUESTS), quest_statistic))
    disp.add_handler(RegexHandler(to_re(STATISTICS_COMMAND_QUESTS_ALL), quest_statistic))
    disp.add_handler(RegexHandler(to_re(STATISTICS_COMMAND_ITEMS_ALL), item_statistic))
    disp.add_handler(RegexHandler(to_re(STATISTICS_COMMAND_FORAY_GLOBAL), foray_statistic))
    disp.add_handler(RegexHandler(to_re(STATISTICS_COMMAND_FORAY), foray_interval))
    disp.add_handler(RegexHandler(to_re(STATISTICS_COMMAND_SKILLS), skill_statistic))

    logging.info("Finished adding button handlers")
