""" Строки """

MSG_ORDER_STATISTIC = 'Statistics of following the orders for {} days:\n'
MSG_ORDER_STATISTIC_OUT_FORMAT = '{}: {}/{}\n'
MSG_USER_UNKNOWN = 'No such user'

MSG_NEW_GROUP_ADMIN = """Welcome our new administrator: @{}!
Check the commands list with /help command"""
MSG_NEW_GROUP_ADMIN_EXISTS = '@{} already has administrator rights'

MSG_DEL_GROUP_ADMIN_NOT_EXIST = '@{} never had any power here!'
MSG_DEL_GROUP_ADMIN = '@{}, now you have no power here!'

MSG_NEW_GLOBAL_ADMIN = 'New global administrator: @{}!'
MSG_NEW_GLOBAL_ADMIN_EXISTS = '@{} already has global administrator rights'

MSG_DEL_GLOBAL_ADMIN_NOT_EXIST = '{} never had any global rights!'
MSG_DEL_GLOBAL_ADMIN = '@{} now you have no global rights'

MSG_NEW_SUPER_ADMIN = 'New super administrator: @{}!'
MSG_NEW_SUPER_ADMIN_EXISTS = '@{} is already a super administrator!'

MSG_LIST_ADMINS_HEADER = 'Administrators list:\n'
MSG_LIST_ADMINS_FORMAT = '{} @{} {} {}\n'
MSG_LIST_ADMINS_USER_FORMAT = '@{} {} {}\n'

MSG_EMPTY = '[Empty]\n'

MSG_START_WELCOME = 'Greetings, warrior! I am the Castle Bot of 🥔Potato castle! ' \
                    'Please send me your game profile from @chtwrsbot ("/hero" command).'
MSG_ADMIN_WELCOME = 'Welcome, master!'

MSG_HELP_GLOBAL_ADMIN = """Welcome commands:
/enable_welcome — enable welcome message.
/disable_welcome — disable welcome message.
/set_welcome <text> — set welcome message. \
Can contain %username% — will be shown as @username, \
if not set to First and Last name, or ID, 
using %last_name%, %first_name%, %id%.
/show_welcome — show welcome message.

Trigger commands:
Reply to a message or file with /set_trigger <trigger text> — \
set message to reply with on a trigger.
/add_trigger <trigger text>::<reply text> — \
add message to reply with on a trigger. \
Old messages can't be replaced.

/del_trigger <trigger> — delete trigger.
/list_triggers — show all triggers.

Super administrator commands:
/add_admin <user> — add administrator to current chat.
/del_admin <user> — delete administrator from current chat.
/list_admins — show list of current chat administrators.
/enable_trigger — allow everyone to call trigger.
/disable_trigger — forbid everyone to call trigger.
"""

MSG_HELP_GROUP_ADMIN = """Welcome commands:
/enable_welcome — enable welcome message.
/disable_welcome — disable welcome message.
/set_welcome <text> — set welcome message. \
Can contain %username% — will be shown as @username, \
if not set to First and Last name, or ID, 
using %last_name%, %first_name%, %id%.
/show_welcome — show welcome message.

Trigger Commands:
/add_trigger <trigger text>::<reply text> — \
add message to reply with on a trigger. \
Old messages can't be replaced.
/list_triggers — show all triggers.
/enable_trigger — allow everyone to call trigger.
/disable_trigger — forbid everyone to call trigger.
"""

MSG_HELP_USER = "/list_triggers — show all triggers."

MSG_PING = 'Go and dig some potatoes, @{}!'

MSG_STOCK_COMPARE_HARVESTED = '📦<b>You got:</b>\n'
MSG_STOCK_COMPARE_LOST = '\n📦<b>You lost:</b>\n'
MSG_STOCK_COMPARE_FORMAT = '{} ({})\n'
MSG_STOCK_COMPARE_WAIT = 'Waiting for data to compare...'

MSG_PERSONAL_SITE_LINK = 'Your personal link: {}'

MSG_GROUP_STATUS_CHOOSE_CHAT = 'Choose chat'
MSG_GROUP_STATUS = """Group: {}

Admins:
{}
Welcome: {}
Trigger allowed: {}
Thorns: {}"""

MSG_GROUP_STATUS_ADMIN_FORMAT = '{} @{} {} {}\n'
MSG_GROUP_STATUS_DEL_ADMIN = 'Bust {} {}'

MSG_ON = 'Enabled'
MSG_OFF = 'Disabled'
MSG_SYMBOL_ON = '✅'
MSG_SYMBOL_OFF = '❌'
MSG_BACK = '🔙Back'

MSG_ORDER_TO_SQUADS = 'To groups'
MSG_ORDER_ACCEPT = 'Accepted!'
MSG_ORDER_PIN = '✅Pin'
MSG_ORDER_NO_PIN = '❌No pin'
MSG_ORDER_BUTTON = '✅Button'
MSG_ORDER_NO_BUTTON = '❌No button'

MSG_ORDER_CLEARED_BY_HEADER = 'Order accepted by:\n'

MSG_ORDER_SENT = 'Message is sent'

MSG_ORDER_CLEARED = 'Recorded, soldier!'
MSG_ORDER_CLEARED_ERROR = 'Please stop it!!!!'

MSG_ORDER_SEND_HEADER = 'Where to send?'

MSG_ORDER_GROUP_CONFIG_HEADER = 'Group settings: {}'
MSG_ORDER_GROUP_NEW = 'Send me the name of a new group of squads'
MSG_ORDER_GROUP_LIST = 'List groups'
MSG_ORDER_GROUP_ADD = '➕Add group'
MSG_ORDER_GROUP_DEL = '🔥🚨Delete group🚨🔥'

MSG_NEWBIE = """There is a new player in castle!\n
Hurry up to recruit %username%!"""

MSG_FLAG_CHOOSE_HEADER = 'Choose a flag or send me the order'

MSG_PROFILE_OLD = 'Your profile smells rotten...'
MSG_PROFILE_SAVED = """Your profile now smells like a really good potato, {}!
Don't forget to water it regularly 🥔 """
MSG_PROFILE_CASTLE_MISTAKE = """\
You saw a beautiful potato field not far away from you.
There was just fence between you.
You decided to walk around and find a way in.
Two hours later you returned to the same place you started at..."""
MSG_PROFILE_SHOW_FORMAT = """\
👤 %first_name% %last_name% (%username%)
%castle% %name%
🏅 %prof% %level% level of
⚜️ Squad %squad%
⚔️ %attack% | 🛡 %defence% | 🔥 %exp%/%needExp%
💰 %gold% | 🔋 %maxStamina%
%pet%
🕑 Last update %date%"""

# main.py texts
MSG_MAIN_INLINE_BATTLE = 'ROB AND KILL!'
MSG_MAIN_READY_TO_BATTLE = 'The battle is in 10 minutes, 🛡🥔 HOLD DEFENSE HIDE GOLD AND WAIT FOR COMMANDS'
# -----------------------
MSG_BUILD_REPORT_EXISTS = 'This report already exists!'
MSG_BUILD_REPORT_OK = 'Thanks for the help! This is your {} report.'
MSG_BUILD_REPORT_FORWARDED = 'Do not send me any more reports from alternative accounts !!! '
MSG_BUILD_REPORT_TOO_OLD = 'This report is very old, I can not accept it.'

MSG_REPORT_OLD = 'Your report stinks like rotten potato, next time try to send it within a minute after receiving."'
MSG_REPORT_EXISTS = 'The report for this battle has already been submitted.'
MSG_REPORT_OK = 'Thank you. Do not forget to forward reports on every battle.'

MSG_PROFILE_NOT_FOUND = 'In the potato plantation records there is still no data about this hero'
MSG_SQUAD_REQUEST_EMPTY = 'At the moment no one wants to join you.'

MSG_NO_PROFILE_IN_BOT = 'First give me a profile!'
MSG_SQUAD_RECRUITING_ENABLED = 'Squad recruiting is enabled!'
MSG_SQUAD_RECRUITING_DISABLED = 'Squad recruiting is disabled!'
MSG_SQUAD_NO_PROFILE = 'First let him give the profile!'
MSG_SQUAD_GREEN_INLINE_BUTTON = '✅Yes'
MSG_SQUAD_RED_INLINE_BUTTON = '❌No'
MSG_SQUAD_NEW = """Now the orders will be here {}!
Do not forget to set a link to invite new members."""
MSG_SQUAD_LINK_SAVED = """Invitation link saved!
New members will not pass by now!"""
MSG_SQUAD_RENAMED = 'Now this squad will be called{}!'
MSG_SQUAD_DELETE = 'The squad is dissolved'
MSG_SQUAD_THORNS_ENABLED = 'The straw man in around'
MSG_SQUAD_THORNS_DISABLED = 'The straw man disappeared, \
now everyone can see what is happening'
MSG_SQUAD_ALREADY_DELETED = 'This user is already expelled from the squad, this button no longer works=('
MSG_SQUAD_LEVEL_TOO_LOW = 'This squad takes soldiers at level {} and above. Come back when you get pumped!'

MSG_TRIGGER_NEW = 'The trigger for the phrase "{}" is set.'
MSG_TRIGGER_GLOBAL = '<b>Global:</b>\n'
MSG_TRIGGER_LOCAL = '\n<b>Local:</b>\n'
MSG_TRIGGER_NEW_ERROR = 'You thoughts are not clear, try one more time'
MSG_TRIGGER_EXISTS = 'Trigger "{}" already exists, select another one.'
MSG_TRIGGER_ALL_ENABLED = 'now everything can be triggered.'
MSG_TRIGGER_ALL_DISABLED = 'Now only admins can trigger.'
MSG_TRIGGER_DEL = 'The trigger for "{}" has been deleted.'
MSG_TRIGGER_DEL_ERROR = 'Where did you see such a trigger? 0_o'
MSG_TRIGGER_LIST_HEADER = 'List of current triggers: \n'

MSG_THORNS = 'This fool {} does not look like a potato, let the straw man kick his ass'

MSG_WELCOME_DEFAULT = 'Hi, %username%!'
MSG_WELCOME_SET = 'The welcome text is set.'
MSG_WELCOME_ENABLED = 'Welcome enabled'
MSG_WELCOME_DISABLED = 'Welcome disabled'

MSG_PIN_ALL_ENABLED = 'Anyone can pin'
MSG_PIN_ALL_DISABLED = 'Do not suffer, now only admins can pin😡'

MSG_ORDER_CLEARED_BY_DUMMY = 'The requested is order is being processed \
because of high server load due to continuous updates'

MSG_NO_SQUAD = 'squadless parasite'
MSG_NO_PET = 'No pets'
MSG_WANTS_TO_JOIN = '\n\nWants to join{}'

MSG_CLEARED = 'Done'

MSG_SQUAD_LIST = 'List of your squads:'
MSG_SQUAD_REQUEST_EXISTS = 'You are already have requested to enter this squad. \
Exit the current squad or cancel the request to create a new one. '
MSG_SQUAD_REQUEST = 'Here are the requests you have receive:'
MSG_SQUAD_LEAVED = '{} left the squad {}, now it is useless, \
and no one will help him any more.'
MSG_SQUAD_LEAVE_ASK = 'Are you sure you want to leave the squad?'
MSG_SQUAD_LEAVE_DECLINE = 'Have you changed your mind? Well, it is nice, let it remain a secret!'
MSG_SQUAD_REQUESTED = 'You requested to join for the squad {}. \
To speed up the decision-making process, you can write to the heads of the squad: {}.'
MSG_SQUAD_REQUEST_ACCEPTED = 'The request from {} is accepted.'
MSG_SQUAD_REQUEST_DECLINED = '{} is useless and no one cares.'
MSG_SQUAD_REQUEST_NEW = 'There are new applications for your squad'
MSG_SQUAD_REQUEST_ACCEPTED_ANSWER = 'You were accepted into the squad'
MSG_SQUAD_REQUEST_DECLINED_ANSWER = 'You application was rejected'
MSG_SQUAD_CLEAN = """Cleaning the squad  {}.
Guess Who is going to have a rest today? """
MSG_SQUAD_ADD = '{}, вас хотят в орден. А вы хотите?'
MSG_SQUAD_ADD_IN_SQUAD = '{} is already in a squad (perhaps not yours)'
MSG_SQUAD_ADD_ACCEPTED = '{} Accepted the offer'
MSG_SQUAD_ADD_DECLINED = '{} is useless and no one cares'
MSG_SQUAD_NONE = 'It looks like you are not in a squad'

MSG_SQUAD_READY = '{} warriors of <b>{}</b> are ready to battle!\n{}⚔ {}🛡'
MSG_FULL_TEXT_LINE = '<b>{}</b>: {}👥 {}⚔ {}🛡\n'
MSG_FULL_TEXT_TOTAL = '\n<b>Total</b>: {}👥 {}⚔ {}🛡'

MSG_IN_DEV = 'Under construction=('

MSG_TOP_ABOUT = '🏆 Tops 🏆'
MSG_STATISTICS_ABOUT = '📈Statistics📈'
MSG_SQUAD_ABOUT = '⚜Squad⚜'

MSG_TOP_FORMAT = '{}. {} ({}🌟) - {}{}\n'
MSG_SQUAD_TOP_FORMAT = '{}. {} ({}👥) - {}{} ({}{}/👤)\n'
MSG_TOP_DEFENCE = '🛡Top Defenders:\n'
MSG_TOP_ATTACK = '⚔Тop attackers:\n'
MSG_TOP_EXPERIENCE = '🔥Top XP:\n'
MSG_TOP_GLOBAL_BUILDERS = '⚒Top Builders:\n'
MSG_TOP_WEEK_BUILDERS = '👷Top builders of the week:\n'
MSG_TOP_WEEK_WARRIORS = '⛳️Top in the battle:\n'

MSG_UPDATE_PROFILE = 'Send me a new profile (🏅 command "/hero"), or you might be kicked of .'
MSG_SQUAD_DELETE_OUTDATED = 'You were kicked from the squad for not updating your profile for a long time.'
MSG_SQUAD_DELETE_OUTDATED_EXT = '{} (@{}) was kicked from {} for not updating profile for a long time.'

MSG_ALREADY_BANNED = 'This user is already banned. The reason is: {2}.'
MSG_USER_BANNED = 'A member of {} violated the rules and was kicked!'
MSG_YOU_BANNED = 'You were banned because: {}'
MSG_BAN_COMPLETE = 'Warrior successfully banned'
MSG_USER_NOT_BANNED = 'This warrior is not banned'
MSG_USER_UNBANNED = '{} is no longer banned.'
MSG_YOU_UNBANNED = 'We can talk again 🌚'

PLOT_X_LABEL = 'Date'
PLOT_Y_LABEL = 'XP'

MSG_DAY_SINGLE = 'Day'
MSG_DAY_PLURAL1 = 'Day'
MSG_DAY_PLURAL2 = 'Days'
MSG_DATE_FORMAT = '{} {}'
MSG_PLOT_DESCRIPTION = 'On average {} of experience per day. For next level, you need {} experience and {}'

MSG_SQUAD_CALL_HEADER = 'Everybody come here!\n'
MSG_REPORT_SUMMARY_HEADER = 'Reports of the squad {} for the batle {}\n' \
                            'Reports: {} from {}\n' \
                            '<b>General</b>\n' \
                            'Attack: ⚔{}\n' \
                            'Defense: 🛡{}\n' \
                            'Profit: 🔥{} 💰{} 📦{}\n\n' \
                            '<b>Personal</b>\n'
MSG_REPORT_SUMMARY_ROW = '<b>{}</b> (@{})\n⚔{} 🛡{} 🔥{} 💰{} 📦{}\n'
MSG_REPORT_SUMMARY_ROW_EMPTY = '<b>{}</b> (@{}) ❗\n'

BTN_HERO = '🏅Hero'
BTN_STOCK = '📦Stock'
BTN_EQUIPMENT = '🎽Equipment'

BTN_YES = '✅YES'
BTN_NO = '❌NO'

BTN_LEAVE = 'Leave'

BTN_ACCEPT = '✅Accept'
BTN_DECLINE = '❌Decline'

BTN_WEEK = "Week"
BTN_ALL_TIME = "All Time"
BTN_SQUAD_WEEK = "Squads per Week"
BTN_SQUAD_ALL_TIME = "Squads of all time"

MSG_LAST_UPDATE = '🕑 Last Update'
MSG_GO_AWAY = 'Go Away!'
MSG_TOP_GENERATING = 'Generating Top'

MSG_NO_REASON = 'Reason not specified'
