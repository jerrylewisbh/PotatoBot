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

CC_SET_WELCOME = 'welcome:'
CC_HELP = 'help'
CC_SQUAD = 'squad'
CC_SHOW_WELCOME = 'show welcome message'
CC_TURN_ON_WELCOME = 'turn on welcome message'
CC_TURN_OFF_WELCOME = 'turn off welcome message'
CC_TURN_ON_REPORT_FWD = 'turn on minireport'
CC_TURN_OFF_REPORT_FWD = 'turn off minireport'
CC_SET_TRIGGER = 'trigger:'
CC_UNSET_TRIGGER = 'untrigger:'
CC_TRIGGER_LIST = 'trigger list'
CC_ADMIN_LIST = 'admin list'
CC_PING = 'ping'
CC_DAY_STATISTICS = 'daily stats'
CC_WEEK_STATISTICS = 'weekly stats'
CC_BATTLE_STATISTICS = 'battle stats'
CC_ALLOW_TRIGGER_ALL = 'allow everyone to trigger'
CC_DISALLOW_TRIGGER_ALL = 'prevent everyone from triggering'
CC_ADMINS = 'admins'
CC_COMMANDER = 'commander'
CC_ALLOW_PIN_ALL = 'allow everyone to pin'
CC_DISALLOW_PIN_ALL = 'prevent everyone from pinning'
CC_OPEN_HIRING = 'open admissions'
CC_CLOSE_HIRING = 'close admissions'
CC_PIN = 'pin and notify'
CC_SILENT_PIN = 'pin'
CC_DELETE = 'delete'
CC_KICK = 'kick'


def to_re(string, case_insensitive=True):
    if case_insensitive:
        return re.compile("^{}".format(string), re.IGNORECASE)
    else:
        return re.compile("^{}".format(string))


def add_handler(disp: Dispatcher):
    # NOTE: Use the @command_handler decorator for the functions registered here! This will provide you with the User
    # object and additionally filters by chat-type (private, group, etc.)

    logging.debug("Starting adding chat handlers")
    # on different commands - answer in Telegram

    # TODO: Move to commands?
    disp.add_handler(RegexHandler(to_re(CC_SET_WELCOME), set_welcome))
    disp.add_handler(RegexHandler(to_re(CC_HELP), help_msg))
    disp.add_handler(RegexHandler(to_re(CC_SQUAD), call_squad))
    disp.add_handler(RegexHandler(to_re(CC_SHOW_WELCOME), show_welcome))
    disp.add_handler(RegexHandler(to_re(CC_TURN_OFF_WELCOME), disable_welcome))
    disp.add_handler(RegexHandler(to_re(CC_TURN_ON_WELCOME), enable_welcome))
    disp.add_handler(RegexHandler(to_re(CC_TURN_ON_REPORT_FWD), enable_report_fwd))
    disp.add_handler(RegexHandler(to_re(CC_TURN_OFF_REPORT_FWD), disable_report_fwd))
    disp.add_handler(RegexHandler(to_re(CC_SET_TRIGGER), set_trigger))
    disp.add_handler(RegexHandler(to_re(CC_UNSET_TRIGGER), del_trigger))
    disp.add_handler(RegexHandler(to_re(CC_TRIGGER_LIST), list_triggers))
    disp.add_handler(RegexHandler(to_re(CC_ADMIN_LIST), list_admins))
    disp.add_handler(RegexHandler(to_re(CC_PING), ping))
    disp.add_handler(RegexHandler(to_re(CC_DAY_STATISTICS), day_activity))
    disp.add_handler(RegexHandler(to_re(CC_WEEK_STATISTICS), week_activity))
    disp.add_handler(RegexHandler(to_re(CC_BATTLE_STATISTICS), battle_activity))
    disp.add_handler(RegexHandler(to_re(CC_ALLOW_TRIGGER_ALL), enable_trigger_all))
    disp.add_handler(RegexHandler(to_re(CC_DISALLOW_TRIGGER_ALL), disable_trigger_all))
    disp.add_handler(RegexHandler(to_re(CC_ADMINS), admins_for_users))
    disp.add_handler(RegexHandler(to_re(CC_COMMANDER), admins_for_users))
    disp.add_handler(RegexHandler(to_re(CC_ALLOW_PIN_ALL), pin_all))
    disp.add_handler(RegexHandler(to_re(CC_DISALLOW_PIN_ALL), not_pin_all))
    disp.add_handler(RegexHandler(to_re(CC_OPEN_HIRING), open_hiring))
    disp.add_handler(RegexHandler(to_re(CC_CLOSE_HIRING), close_hiring))
    disp.add_handler(RegexHandler(to_re(CC_PIN), pin))
    disp.add_handler(RegexHandler(to_re(CC_SILENT_PIN), silent_pin))
    disp.add_handler(RegexHandler(to_re(CC_DELETE), delete_msg))
    disp.add_handler(RegexHandler(to_re(CC_KICK), delete_user))

    disp.add_handler(RegexHandler(HERO, char_update))
    disp.add_handler(RegexHandler(REPORT, report_received))
    disp.add_handler(RegexHandler(BUILD_REPORT, build_report_received))
    disp.add_handler(RegexHandler(REPAIR_REPORT, repair_report_received))
    disp.add_handler(RegexHandler(PROFESSION, profession_update))
    disp.add_handler(RegexHandler(ACCESS_CODE, handle_access_token))
    disp.add_handler(RegexHandler(to_re(STOCK, False), stock_compare_forwarded, pass_chat_data=True))
    disp.add_handler(RegexHandler(to_re(GUILD_WAREHOUSE, False), withdraw))

    logging.info("Finished adding chat handlers")
