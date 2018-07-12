from telegram.ext import Dispatcher, RegexHandler

from core.regexp import *
from functions.activity import *
from functions.common import *
from functions.common.pin import *
from functions.guild.stock import withdraw
from functions.profile import *
from functions.report import *
from functions.squad.admin import call_squad
from functions.squad.admin.commands import open_hiring, close_hiring
from functions.triggers import *
from functions.user import list_admins, admins_for_users
from functions.welcome import *


def to_re(string, case_insensitive=True):
    if case_insensitive:
        return re.compile("^{}".format(string), re.IGNORECASE)
    else:
        return re.compile("^{}".format(string))


def add_handler(disp: Dispatcher):
    # NOTE: Use the @command_handler decorator for the functions registered here! This will provide you with the User
    # object and additionally filters by chat-type (private, group, etc.)

    logging.debug("Starting adding chat handlers")

    disp.add_handler(RegexHandler(HERO, char_update))
    disp.add_handler(RegexHandler(REPORT, report_received))
    disp.add_handler(RegexHandler(BUILD_REPORT, build_report_received))
    disp.add_handler(RegexHandler(REPAIR_REPORT, repair_report_received))
    disp.add_handler(RegexHandler(PROFESSION, profession_update))
    disp.add_handler(RegexHandler(ACCESS_CODE, handle_access_token))
    disp.add_handler(RegexHandler(to_re(STOCK, False), stock_compare_forwarded, pass_chat_data=True))
    disp.add_handler(RegexHandler(to_re(GUILD_WAREHOUSE, False), withdraw))

    logging.info("Finished adding chat handlers")
