from core.commands import *
from core.exchange.hide import hide_gold_info
from core.exchange.snipe import sniping_info
from core.functions.common import admin_panel
from core.functions.inline_keyboard_handling import send_status
from core.functions.order_groups import group_list
from core.functions.orders import orders
from core.functions.profile import user_panel, show_char, grant_access, settings, char_update, report_received, \
    build_report_received, repair_report_received, profession_update, handle_access_token
from core.functions.squad import (battle_attendance_show, battle_reports_show,
                                  leave_squad_request, list_squad_requests,
                                  remove_from_squad, squad_about,
                                  squad_list, squad_request)
from core.functions.statistics import statistic_about, exp_statistic, skill_statistic, quest_statistic
from core.functions.statistics.foray import foray_statistic
from core.functions.top import top_about, attack_top, def_top, exp_top, week_build_top, week_battle_top
from core.handlers.message_handler import *
from core.regexp import HERO, REPORT, BUILD_REPORT, REPAIR_REPORT, PROFESSION, ACCESS_CODE


def send_status_handler(is_registered):
    return RegisteredOnlyHandler(
        message=ADMIN_COMMAND_STATUS,
        action=send_status,
        is_registered=is_registered)


def user_panel_handler(is_registered):
    return RegisteredOnlyHandler(
        message=USER_COMMAND_BACK,
        action=user_panel,
        is_registered=is_registered)


def squad_request_handler(is_registered):
    return RegisteredOnlyHandler(
        message=USER_COMMAND_SQUAD_REQUEST,
        action=squad_request,
        is_registered=is_registered)


def top_about_handler(is_registered):
    return RegisteredOnlyHandler(
        message=USER_COMMAND_TOP,
        action=top_about,
        is_registered=is_registered)


list_squad_requests_handler = SimpleHandler(
    message=ADMIN_COMMAND_RECRUIT,
    action=list_squad_requests)

orders_handler = SimpleHandler(
    message=ADMIN_COMMAND_ORDER,
    action=orders)

squad_list_handler = SimpleHandler(
    message=ADMIN_COMMAND_SQUAD_LIST,
    action=squad_list)

group_list_handler = SimpleHandler(
    message=ADMIN_COMMAND_GROUPS,
    action=group_list)

battle_reports_show_handler = SimpleHandler(
    message=ADMIN_COMMAND_REPORTS,
    action=battle_reports_show)

battle_attendance_show_handler = SimpleHandler(
    message=ADMIN_COMMAND_ATTENDANCE,
    action=battle_attendance_show)

remove_from_squad_handler = SimpleHandler(
    message=ADMIN_COMMAND_FIRE_UP,
    action=remove_from_squad)

show_char_handler = SimpleHandler(
    message=USER_COMMAND_ME,
    action=show_char)

grant_access_handler = SimpleHandler(
    message=USER_COMMAND_REGISTER,
    action=grant_access)

settings_handler = SimpleHandler(
    message=USER_COMMAND_SETTINGS,
    action=settings)

attack_top_handler = SimpleHandler(
    message=TOP_COMMAND_ATTACK,
    action=attack_top)

def_top_handler = SimpleHandler(
    message=TOP_COMMAND_DEFENCE,
    action=def_top)

exp_top_handler = SimpleHandler(
    message=TOP_COMMAND_EXP,
    action=exp_top)

week_build_top_handler = SimpleHandler(
    message=TOP_COMMAND_BUILD,
    action=week_build_top)

week_battle_top_handler = SimpleHandler(
    message=TOP_COMMAND_BATTLES,
    action=week_battle_top)

statistic_about_handler = SimpleHandler(
    message=USER_COMMAND_STATISTICS,
    action=statistic_about)

exp_statistic_handler = SimpleHandler(
    message=STATISTICS_COMMAND_EXP,
    action=exp_statistic)

skill_statistic_handler = SimpleHandler(
    message=STATISTICS_COMMAND_SKILLS,
    action=skill_statistic)

quest_statistic_handler = SimpleHandler(
    message=STATISTICS_COMMAND_QUESTS,
    action=quest_statistic)

foray_statistic_handler = SimpleHandler(
    message=STATISTICS_COMMAND_FORAY,
    action=foray_statistic)

squad_about_handler = SimpleHandler(
    message=USER_COMMAND_SQUAD,
    action=squad_about)

leave_squad_request_handler = SimpleHandler(
    message=USER_COMMAND_SQUAD_LEAVE,
    action=leave_squad_request)

admin_panel_handler = SimpleHandler(
    message=ADMIN_COMMAND_ADMINPANEL,
    action=admin_panel)

hide_gold_info_handler = SimpleHandler(
    message=USER_COMMAND_HIDE,
    action=hide_gold_info)

sniping_info_handler = SimpleHandler(
    message=USER_COMMAND_EXCHANGE,
    action=sniping_info)

char_update_handler = RegexHandler(
    regex=HERO,
    action=char_update
)

report_received_handler = RegexHandler(
    regex=REPORT,
    action=report_received
)

build_report_received_handler = RegexHandler(
    regex=BUILD_REPORT,
    action=build_report_received
)

repair_report_received_handler = RegexHandler(
    regex=REPAIR_REPORT,
    action=repair_report_received
)

profession_update_handler = RegexHandler(
    regex=PROFESSION,
    action=profession_update
)

handle_access_token_handler = RegexHandler(
    regex=ACCESS_CODE,
    action=handle_access_token
)

forward_handlers = [
    char_update_handler,
    report_received_handler,
    build_report_received_handler,
    repair_report_received_handler,
    profession_update_handler,
    handle_access_token_handler
]
