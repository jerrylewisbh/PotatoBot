""" Строки """
from core.commands import USER_COMMAND_EXCHANGE, USER_COMMAND_HIDE

MSG_ORDER_STATISTIC = 'Statistics of who confirmed the orders for {} days:\n'
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

MSG_START_NEW = 'Greetings, warrior! I am the Castle Bot of 🥔Potato Castle! \n\n' \
                'To get things started please forward me your game profile from @chtwrsbot ("/hero" command).'

MSG_START_KNOWN = 'Greetings, warrior! I am the Castle Bot of 🥔Potato Castle! \n\n' \
                  'If you want to refresh your game profile forward me your /"hero" from @chtwrsbot.\n\n' \
                  'I also suggest you *join one of our squads* ("⚜Squad") to better coordinate in battle. After ' \
                  'joining you can also get automated stock change information after war, get notified if you sell ' \
                  'something or automatically buy cheap things in the Exchange (sniping).'

MSG_START_MEMBER_SQUAD = 'Welcome back 🥔{}!\n\n' \
                         'As a squad member you can choose "🔑Register" to allow me direct access to your profile ' \
                         'and get automated stock change information after war, get notified if you sell something or ' \
                         'automatically buy cheap things in the Exchange (sniping).'

MSG_START_MEMBER_SQUAD_REGISTERED = 'Welcome back 🥔{}!\n\n' \
                                    'How can I help you today?'

MSG_ADMIN_WELCOME = 'Welcome, master!'

MSG_HELP_GLOBAL_ADMIN = """Welcome commands:
/enable_welcome — enable welcome message.
/disable_welcome — disable welcome message.
/set_welcome <text> — set welcome message. \
Can contain %username% — will be shown as @username, %ign% - will show user ingame name, \
if not set to First and Last name, or ID,
using %last_name%, %first_name%, %id%.
/show_welcome — show welcome message.

Trigger commands:
Reply to a message or file with /set_trigger <trigger text> — \
set message to reply with on a trigger (only current chat)
/del_trigger <trigger> — delete trigger.
/list_triggers — show all triggers.
Reply to a message or file with /set_global_trigger <trigger text> — \
set message to reply with on a trigger (all chats)
/del_global_trigger <trigger> — delete trigger.

Super administrator commands:
/add_admin <user> — add administrator to current chat.
/del_admin <user> — delete administrator from current chat.
/list_admins — show list of current chat administrators.
/enable_trigger — allow everyone to call trigger.
/disable_trigger — forbid everyone to call trigger.
/find <user> - Show user status by telegram user name
/findc <ign> - Show user status by ingame name
/findi <id> - Show user status by telegram uquique id
/get_log - Get latest logfile



Squad commands:
/add_squad - Create a new squad and associates it to the current group
/del_squad - Delete the squad associated with teh group
/enable_thorns - Prevent non members of the squad be in the group
/disable_thorns - Allow non members of the group to be in the squad
/enable_silence  - Deletes all messages typed 3 minutes before battle
/disable_silence - Allow user to type even 3 minutes before batte
/enable_reminders  - Turn on automatated battle reminder 30 and 45 minutes before battle and report reminder 10 minutes after battle
/disable_reminders - Disable reminders
/set_squad_name <name> - Change the name of the squad
/set_invite_link <link> - Set up the invite link that will be sent to approved members
/add <user> - Ask an user to join the squad
/forceadd <user> - add user to a squad without asking for confirmation
/ban <user> <reason> - Ban an user from the squad
/unban <user> - Unban an user from the squad


User commands: 
/items - List known items
/hide - Manually trigger hide
/resume - Resume suspended sniping
/s <itemID> <maxPrice> [<limit>] - Create snipe order
/sr <itemID> - Remove sniping order
/report - Show your last report (including stock change if API is enabled)


Free text commands:
daily stats  - Show squad daily stats
weekly stats - Show squad weekly stats
battle stats - Show last batle stats for batle
prevent everyone from triggering - Allow only admins to call triggers
allow everyone to pin - Allow all members to pin messages
prevent everyone from pinning - Allow only admins to pin messages
squad - mention every squad member

Reply any message with Pin to Pin it (admins always can do that, other members if its enabled)
Reply any message with Pin and notify to pin and send notificaion
Reply any message with Delete to delete it

"""

MSG_HELP_GROUP_ADMIN = """Welcome commands:
/enable_welcome — enable welcome message.
/disable_welcome — disable welcome message.
/set_welcome <text> — set welcome message. \
Can contain %username% — will be shown as @username, \
if not set to First and Last name, or ID,
using %last_name%, %first_name%, %id%.
/show_welcome — show welcome message.

Squad commands:
/enable_thorns - Prevent non members of the squad be in the group
/disable_thorns - Allow non members of the group to be in the squad
/enable_silence  - Deletes all messages typed 3 minutes before battle
/disable_silence - Allow user to type even 3 minutes before batte
/enable_reminders  - Turn on automatated battle reminder 30 and 45 minutes before battle and report reminder 10 minutes after battle
/disable_reminders - Disable reminders
/set_invite_link <link> - Set up the invite link that will be sent to approved members
/add <user> - Ask an user to join the squad
/ban <user> <reason>  - Ban an user from the squad
/unban <user> - Unban an user from the squad


Free text commands:
daily stats  - Show squad daily stats
weekly stats - Show squad weekly stats
battle stats - Show last batle stats for batle
allow everyone to trigger - Allow every member to call triggers
prevent everyone from triggering - Allow only admins to call triggers
allow everyone to pin - Allow all members to pin messages
prevent everyone from pinning - Allow only admins to pin messages
squad - mention every squad member

Reply any message with Pin to Pin it (admins always can do that, other members if its enabled)
Reply any message with Pin and notify to pin and send notificaion
Reply any message with Delete to delete it


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
MSG_GROUP_STATUS_DEL_ADMIN = 'Demote {} {}'

MSG_ON = 'Enabled'
MSG_OFF = 'Disabled'
MSG_SYMBOL_ON = '✅'
MSG_SYMBOL_OFF = '❌'
MSG_BACK = '🔙Back'

MSG_ORDER_TO_SQUADS = 'Choose Squad'
MSG_ORDER_ACCEPT = 'Accept!'
MSG_ORDER_FORWARD = 'Forward'
MSG_ORDER_PIN = '✅Pin'
MSG_ORDER_NO_PIN = '❌No pin'
MSG_ORDER_BUTTON = '✅Button'
MSG_ORDER_NO_BUTTON = '❌No button'

MSG_ORDER_CLEARED_BY_HEADER = 'Order accepted by:\n'

MSG_ORDER_SENT = 'Message is sent'

MSG_ORDER_CLEARED = 'Recorded, soldier!'


MSG_ORDER_CLEARED_ERROR = 'STOP! You do not belong here!!!!'
MSG_ORDER_SEND_HEADER = 'Where to send?'

MSG_ORDER_GROUP_CONFIG_HEADER = 'Group settings: {}'
MSG_ORDER_GROUP_NEW = 'Send me the name of a new group of squads'
MSG_ORDER_GROUP_LIST = 'List groups'
MSG_ORDER_GROUP_ADD = '➕Add group'
MSG_ORDER_GROUP_DEL = '🔥🚨Delete group🚨🔥'

MSG_NEWBIE = """There is a new player in castle!\n
Hurry up to recruit %username%!"""

MSG_NO_USERNAME = "You have not set up a telegram username, you need to set one up to join squad."
MSG_FLAG_CHOOSE_HEADER = 'Choose a castle or send me the order'

MSG_PROFILE_OLD = 'Your profile smells rotten, forward a new one generated within one minute.'

MSG_PROFILE_SAVED = """Your profile now smells like a really good potato, {}!
Don't forget to water it regularly 🥔 """

MSG_SKILLS_SAVED = """Thanks for submitting your skills, {}!
Don't forget to send it regularly 🥔 """


MSG_PROFILE_CASTLE_MISTAKE = """\
You saw a beautiful potato field not far away from you.
There was just a fence between you.
You decided to walk around and find a way in.
Two hours later you returned to the same place you started at..."""

MSG_PROFILE_SHOW_FORMAT = """\
👤 %first_name% %last_name% (%username%)
%castle% %name% of %prof% Castle
🏛 %profession%
🏅 Level %level%
⚜️ %squad%
⚔️ %attack% | 🛡 %defence% | 🔥 %exp%/%needExp%
💰 %gold% | 👝 %pouches%
%pet%
🕑 Last update %date%"""

MSG_PROFILE_ADMIN_INFO_ADDON = "\n\n<b>Admin-Info:</b>\n" \
                               "Banned: {}\n" \
                               "Token: {}\n" \
                               "API ID: {}\n" \
                               "Profile allowed: {}\n" \
                               "Stock allowed: {}\n" \
                               "Trade allowed: {}\n" \
                               "Report enabled: {}\n" \
                               "Exchange enabled: {}\n" \
                               "Hide enabled: {}\n" \
                               "Sniping enabled: {} {}"


# | 🔋 %maxStamina% - Removed until api provides it or sth else happens...

# main.py texts
MSG_MAIN_INLINE_BATTLE = 'ROGER THAT!'
MSG_MAIN_READY_TO_BATTLE = 'The battle is in 10 minutes, 🛡🥔 HOLD DEFENSE HIDE GOLD AND WAIT FOR COMMANDS'
MSG_MAIN_READY_TO_BATTLE_30 = '❗️⚔️WAR IN 30 MINUTES ⚔️❗️\
\n\n\
CLOSE TRADES ⚖️ HIDE GOLD💰AND STOCK 📦 \
\n\n\
Equip dagger 🗡/ shield 🛡\
\n\n\
Set default status to DEF 🛡 and wait for orders.'

MSG_MAIN_READY_TO_BATTLE_45 = 'WAAARRR IN 15 MINS!!\
\n\n\
1) 💰➡️🚫HIDE GOLD&STOCK NOW\
\n\n\
2) Press 🛡  in the game bot \
\n\n\
3) Press "⚔️ Attack" to the state of "Ha, bold enough? Choose an enemy!". Don’t choose a target, wait for orders.\
\n\n\
4) Keep Battle-Silence from xx:57:00 till Wind \
\n\n\
@chtwrsbot'

MSG_MAIN_SEND_REPORTS = '⚔️BATTLE IS OVER ⚔️\
\n\n\
📜send me your reports📜\
\n\n\
➡️@PotatoCastle_bot⬅️'

# -----------------------
MSG_BUILD_REPORT_EXISTS = 'This report already exists!'
MSG_BUILD_REPORT_OK = 'Thanks for the help! This is your {} report.'
MSG_BUILD_REPORT_FORWARDED = 'Do not send me any more reports from alternative accounts !!! '
MSG_BUILD_REPORT_TOO_OLD = 'This report is very old, I can not accept it.'

MSG_REPORT_OLD = 'Your report stinks like rotten potato, next time try to send it within a minute after receiving."'
MSG_REPORT_EXISTS = 'The report for this battle has already been submitted.'
MSG_REPORT_OK = 'Thank you. Do not forget to forward reports on every battle.'

MSG_PROFILE_NOT_FOUND = 'In the potato plantation records, there is still no data about this hero'
MSG_SQUAD_REQUEST_EMPTY = 'At the moment no one wants to join you.'

MSG_NO_PROFILE_IN_BOT = 'Please forward me a recent /hero command or grant me access to your profile!'
MSG_SQUAD_RECRUITING_ENABLED = 'Squad recruiting is enabled!'
MSG_SQUAD_RECRUITING_DISABLED = 'Squad recruiting is disabled!'
MSG_SQUAD_NO_PROFILE = 'First I need him/her to give me a recent profile!'
MSG_SQUAD_GREEN_INLINE_BUTTON = '✅Yes'
MSG_SQUAD_RED_INLINE_BUTTON = '❌No'
MSG_SQUAD_NEW = """Now this is the squad {}!
Do not forget to set a link to invite new members."""
MSG_SQUAD_LINK_SAVED = """Invitation link saved!
New members will not pass by now!"""
MSG_SQUAD_RENAMED = 'Now this squad will be called {}!'
MSG_SQUAD_DELETE = 'The squad is dissolved'
MSG_SQUAD_THORNS_ENABLED = 'The straw man in around, only members can be here'
MSG_SQUAD_THORNS_DISABLED = 'The straw man disappeared, \
now everyone can see what is happening'

MSG_SQUAD_SILENCE_ENABLED = 'Battle silence enabled, messages will be deleted 3 minutes before battle'
MSG_SQUAD_SILENCE_DISABLED = 'Battle silence disabled'

MSG_SQUAD_REMINDERS_ENABLED = 'This squad will automatically be reminded of battles and reports, lazy captain'
MSG_SQUAD_REMINDERS_DISABLED = 'This squad will NOT be automatically reminded of battles and reports, do not let them forget 👀'

MSG_SQUAD_ALREADY_DELETED = 'This user is already expelled from the squad, this button no longer works=('
MSG_SQUAD_LEVEL_TOO_LOW = 'This squad takes soldiers at level {} and above. Come back when you get pumped!'

MSG_TRIGGER_NEW = 'The trigger for the phrase "{}" is set.'
MSG_TRIGGER_GLOBAL = '<b>Global:</b>\n'
MSG_TRIGGER_LOCAL = '\n<b>Local:</b>\n'
MSG_TRIGGER_NEW_ERROR = 'You thoughts are not clear, try one more time'
MSG_TRIGGER_EXISTS = 'Trigger "{}" already exists, select another one.'
MSG_TRIGGER_ALL_ENABLED = 'now everything can call triggers.'
MSG_TRIGGER_ALL_DISABLED = 'Now only admins can call triggers.'
MSG_TRIGGER_DEL = 'The trigger for "{}" has been deleted.'
MSG_TRIGGER_DEL_ERROR = 'Where did you see such a trigger? 0_o'
MSG_TRIGGER_LIST_HEADER = 'List of current triggers: \n'

MSG_THORNS = 'This fool {} does not look like a potato, let the straw man kick his ass'

MSG_WELCOME_DEFAULT = 'Hi, %username%!'
MSG_WELCOME_SET = 'The welcome text is set.'
MSG_WELCOME_ENABLED = 'Welcome enabled'
MSG_WELCOME_DISABLED = 'Welcome disabled'

MSG_PIN_ALL_ENABLED = 'Anyone can pin'
MSG_PIN_ALL_DISABLED = 'Now only admins can pin😡'

MSG_ORDER_CLEARED_BY_DUMMY = 'The requested is being processed \
because of high server load due to continuous updates'

MSG_NO_SQUAD = 'Squadless'
MSG_NO_PET = ''
MSG_NO_PROFESSION = 'Classless'
MSG_WANTS_TO_JOIN = '\n\nWants to join {}'

MSG_CLEARED = 'Done'

MSG_SQUAD_LIST = 'List of your squads:'
MSG_SQUAD_REQUEST_EXISTS = 'You are already have requested to enter this squad. \
Exit the current squad or cancel the request to create a new one. '
MSG_SQUAD_REQUEST = 'Here are the requests you have received:'
MSG_SQUAD_LEAVED = '{} left the squad {} 😰'
MSG_SQUAD_LEAVE_ASK = 'Are you sure you want to leave the squad?'
MSG_SQUAD_LEAVE_DECLINE = 'Have you changed your mind? Well, it is nice, let it remain a secret!'
MSG_SQUAD_REQUESTED = 'You requested to join for the squad {}. ' \
                      'Be patient, the process is manual and there is a small queue. Please join our waiting room, captains will talk to you from there: {}'
MSG_SQUAD_REQUEST_ACCEPTED = 'The request from {} is accepted.'
MSG_SQUAD_REQUEST_DECLINED = '{} is useless, no one cares.'
MSG_SQUAD_REQUEST_NEW = 'There are new applications for your squad'
MSG_SQUAD_REQUEST_ACCEPTED_ANSWER = 'You were accepted into the squad'
MSG_SQUAD_REQUEST_ACCEPTED_ANSWER_LINK = 'You were accepted into the squad join using {}'
MSG_SQUAD_REQUEST_DECLINED_ANSWER = 'You application was rejected'
MSG_SQUAD_CLEAN = """Harvesting in the squad {}.
Who do you want to kick? """
MSG_SQUAD_ADD = '{}, Do you want to join the squad?'
MSG_SQUAD_ADD_IN_SQUAD = '{} is already in a squad (perhaps not yours)'
MSG_SQUAD_ADD_ACCEPTED = '{} Accepted the offer'
MSG_SQUAD_ADD_FORCED = '{} was added to the squad'
MSG_SQUAD_ADD_DECLINED = '{} declined, 😰'

MSG_SQUAD_READY = '{} warriors of <b>{}</b> are ready to battle!\n{}⚔ {}🛡'
MSG_FULL_TEXT_LINE = '<b>{}</b>: {}👥 {}⚔ {}🛡\n'
MSG_FULL_TEXT_TOTAL = '\n<b>Total</b>: {}👥 {}⚔ {}🛡'

MSG_IN_DEV = 'Under construction=('

MSG_TOP_ABOUT = '🏆 Tops 🏆'
MSG_STATISTICS_ABOUT = '📈Statistics📈'
MSG_SQUAD_ABOUT = 'You are a member of the Squad "{}"'
MSG_SQUAD_NONE = 'You are currently not a member of any squad. Select "⚜Join Squad" to join one!'

MSG_TOP_FORMAT = '{}. {} (Level {}) - {}{}\n'
MSG_SQUAD_TOP_FORMAT = '{}. {} ({}👥) - {}{} ({}{}/👤)\n'
MSG_TOP_DEFENCE = '🛡Top Defenders:\n'
MSG_TOP_ATTACK = '⚔Тop attackers:\n'
MSG_TOP_EXPERIENCE = '🔥Top XP:\n'
MSG_TOP_GLOBAL_BUILDERS = '⚒Top Builders:\n'
MSG_TOP_WEEK_BUILDERS = '👷Top builders of the week:\n'
MSG_TOP_WEEK_WARRIORS = '⛳️Top battle attendance:\n\n'
MSG_TOP_WEEK_WARRIORS_SQUAD = '⛳️Reports sent on the past 7 days for {}:\n\n'

MSG_UPDATE_PROFILE = 'Send me a new profile (🏅 command "/hero"), or you might be kicked off.'
MSG_SQUAD_DELETE_OUTDATED = 'You were kicked from the squad for not updating your profile for a long time.'
MSG_SQUAD_DELETE_OUTDATED_EXT = '{} (@{}) was kicked from {} for not updating profile for a long time.'

MSG_ALREADY_BANNED = 'This user is already banned. The reason is: {2}.'
MSG_USER_BANNED = '{} violated the rules and was kicked off!'
MSG_USER_BANNED_TRAITOR = 'Et tu, Brute? {} pledged allegiance to another castle, we will remember you!'
MSG_YOU_BANNED = 'You were banned because: {}'
MSG_BAN_COMPLETE = 'Warrior successfully banned'
MSG_USER_NOT_BANNED = 'This warrior is not banned'
MSG_USER_UNBANNED = '{} is no longer banned.'
MSG_YOU_UNBANNED = 'We can talk again 🌚'

PLOT_X_LABEL = 'Date'
PLOT_Y_LABEL = 'XP'

MSG_DAY_SINGLE = 'day'
MSG_DAY_PLURAL1 = 'day'
MSG_DAY_PLURAL2 = 'days'
MSG_DATE_FORMAT = '{} {}'
MSG_PLOT_DESCRIPTION = 'On average {} experience per day. For the next level, you need {} experience and approximately {}'


MSG_PLOT_DESCRIPTION_SKILL = 'Here you can compare the level of your skills with the average for the whole castle. Note it is still beta, please report if you find something wrong'

MSG_SQUAD_CALL_HEADER = 'Everybody come here!\n'
MSG_REPORT_SUMMARY_HEADER = 'Reports of the squad {} for the battle {}' \
                            'Reports: {} from {}\n' \
                            '<b>General</b>\n' \
                            'Attack: ⚔{}\n' \
                            'Defense: 🛡{}\n' \
                            'Profit: 🔥{} 💰{} 📦{}\n\n' \
                            '<b>Personal</b>\n'

MSG_REPORT_SUMMARY_RATING = "Reports for the battle {}"

ATTACK_ICON = '⚔'
DEFENSE_ICON = '🛡'
REST_ICON = '🛌'
PRELIMINARY_ICON = '⚠️'


MSG_NO_CLASS = ' Please forward me your /class first'

MSG_REPORT_SUMMARY = '\n\n{} ({}/{})\n' \
    'Attack: ⚔{}\n' \
    'Defense: 🛡{}\n' \
    'Profit: 🔥{} 💰{} 📦{}' \


MSG_REPORT_TOTAL = '\n\n({} attacked / {} defended)\n' \
    'Attack: ⚔{}\n' \
    'Defense: 🛡{}\n' \



MSG_REPORT_SUMMARY_ROW = '{} <b>{}</b> (@{})\n ⚔{} 🛡{} 🔥{} 💰{} 📦{}\n'
MSG_REPORT_SUMMARY_ROW_EMPTY = '<b>{}</b> (@{}) ❗\n'


BTN_HERO = '🏅Hero'
BTN_STOCK = '📦Stock'
BTN_EQUIPMENT = '🎽Equipment'
BTN_PROFESSIONS = '🏛Skills'

BTN_YES = '✅YES'
BTN_NO = '❌NO'

BTN_LEAVE = 'Leave'

BTN_ACCEPT = '✅Accept'
BTN_DECLINE = '❌Decline'

BTN_SETTING_API_DISABLE = '❌Disable API'
BTN_SETTING_DISABLE_REPORT = '✅Disable automated report'
BTN_SETTING_ENABLE_REPORT = '❌Enable automated report'
BTN_SETTING_DISABLE_DEAL_REPORT = '✅Disable exchange report'
BTN_SETTING_ENABLE_DEAL_REPORT = '❌Enable exchange report'
BTN_SETTING_DISABLE_SNIPING = '✅Disable sniping'
BTN_SETTING_ENABLE_SNIPING = '❌Enable sniping'
BTN_SETTING_DISABLE_HIDE_GOLD = '✅Disable gold hiding'
BTN_SETTING_ENABLE_HIDE_GOLD = '❌Enable gold hiding'

BTN_WEEK = "Week"
BTN_ALL_TIME = "All Time"
BTN_SQUAD_WEEK = "Squads per Week"
BTN_SQUAD_ALL_TIME = "Squads of all time"

MSG_LAST_UPDATE = '🕑 Last Update'
MSG_GO_AWAY = 'Go Away!'
MSG_TOP_GENERATING = 'Generating Top'

MSG_NO_REASON = 'Reason not specified'
MSG_REASON_TRAITOR = 'User changed castles'


# API Access related stuff...
MSG_API_TRY_AGAIN = "Please try again in a few seconds."
MSG_API_INFO = "By registering you will allow me to automatically update your profile. After this step I can also notify about /stock changes after war.\nRegistering requires three steps. Please bear with me. \n\n @chtwrsbot will send you an authentication code. Please send it back to me to complete registration."
MSG_API_INVALID_CODE = "Sorry, your code is not valid!"
MSG_API_ACCESS_RESET = "API access was reset!"
MSG_API_REQUIRE_ACCESS_STOCK = "Seems like I don't have permission to access your stock yet. You'll get a " \
                               "request from me please forward this code to me!"
MSG_API_REQUIRE_ACCESS_TRADE = "Seems like I don't have permission to access your trade options yet. You'll get a " \
                               "request from me please forward this code to me!"
MSG_API_REQUIRE_ACCESS_PROFILE = "Seems like I don't have permission to access your profile yet. You'll get a " \
    "request from me please forward this code to me!"
MSG_API_REVOKED_PERMISSIONS = "It seems I'm unable to access your data. Did you /revoke your permission? Disabling API functions until you register again."
MSG_API_SETUP_STEP_1_COMPLETE = "👌 Profile access is now granted! If I need additional permissions I will let you " \
                                "know!"
MSG_API_INCOMPLETE_SETUP = "It seems that you did not completely register. Please complete registration."

MSG_DISABLED_TRADING = "\nDisabling trading until then."

MSG_API_SETUP_STEP_2_COMPLETE = "👌 Thanks for granting additional permissions!"
MSG_CHANGES_SINCE_LAST_UPDATE = "<b>Changes since your last stock updates:</b>\n"

MSG_USER_BATTLE_REPORT_HEADER = "<b>Your after action report:</b>\n\n"
MSG_USER_BATTLE_REPORT_FULL = "<b>Your complete report:</b>\n\n"

MSG_USER_BATTLE_REPORT= "{}{} ⚔:{} 🛡:{} "\
                        "Lvl: {}\n"\
                        "Your result on the battlefield:\n" \
                        "🔥Exp: {}\n" \
                        "💰Gold: {}\n" \
                        "📦Stock: {}\n\n" \
                        "<i>Note: Thanks for sending in your /report. Please do this after every battle!\n</i>"

MSG_USER_BATTLE_REPORT_PRELIM = "{}{} Lvl: {}\n\n"\
                                "<b>Please forward me your /report as soon as possible!</b>\n"

TRIBUTE_NOTE = "\n\n<i>Note: Stock change also may contain tributes.</i>"

MSG_USER_BATTLE_REPORT_STOCK = "\n{}\n{}\n\n <i>🕑 Last Updates: {} / {}</i>"

MSG_SETTINGS_INFO = "<b>Your settings:</b>\n" \
                    "- Automatic stock report after war: {}\n" \
                    "- Send notification when I sell something: {}\n" \
                    "- Hide Gold: {}\n" \
                    "- Sniping: {}\n\n" \
                    "<i>Last profile update: {}</i>\n" \
                    "<i>Last stock update: {}</i>"
MSG_NEEDS_API_ACCESS = "Requires API Access. Please 🔑Register"
MSG_NEEDS_TRADE_ACCESS = 'This requires trade permissions. I will request them once you select "{}" or "{}".'.format(USER_COMMAND_EXCHANGE, USER_COMMAND_HIDE)

MSG_NO_REPORT_PHASE_BEFORE_BATTLE = "War is coming! Your Stock and Profile is getting updated automatically. No need to forward your data just yet!"
MSG_NO_REPORT_PHASE_AFTER_BATTLE = "War is over but I don't accept reports just yet! I will remind you when it is time."

MSG_DEAL_SOLD = "⚖️You sold <b>{}</b> for {}💰 ({} x {}💰)\nBuyer: {}{}\n\n<i>Note: You can disable this notification in your \"⚙️Settings\".</i>"

#text += "\n\n<b>Please do not forget to forward me your /report command!</b>"

MSG_QUEST = "<b>Please tell me where did you quest?</b>\n\n<i>{}</i>"
MSG_QUEST_DUPLICATE = "You already told me about this particular quest!"
MSG_QUEST_OK = "Your adventure took place in {}. Thank you for your quest details!"

MSG_QUEST_7_DAYS = "*In the last seven days you told me about the following adventures:*\n\n"
MSG_QUEST_STAT_LOCATION = "*{} ({})*: \n" \
                          "Avg: {:.2f}🔥, {:.2f}💰, {:.2f}📦\n" \
                          "Ttl: {:.2f}🔥, {:.2f}💰, {:.2f}📦\n"

MSG_QUEST_OVERALL = "\n\n*Overall:*\n\n"

MSG_QUEST_STAT = "\n\nJust continue sending me your quest reports.\n\n_Hint: Overall statistics, item details, etc. coming soonish..._"

# Exchange stuff
HIDE_WELCOME = "*Use at your own risk! Please report any issues to:* [@BotatoFeedbackBot](tg://user?id=582014258)\n\n" \
               "*With this feature enabled I will try to spend all your gold 15 Minutes before battle. I will remind " \
               "you 15 Minutes before battle so that you can abort it if needed*. \n\n" \
               "You can set your buy-preferences via `/ah <itemId> <prio> <maxPrice>`.\n" \
               "Leave `<maxPrice>` out to always buy at market price. You can get a list of items with `/items`. \n\n" \
               "Examples: \n" \
               "- `/ah 01 1 30` to buy Thread for a maximum price of 30 💰 until you can't afford another one\n" \
               "- `/ah 20 2` to by Leather for the lowest price currently on the market until you can't buy any more of it.\n\n" \
               "_Note: If you already have set an order for one priority this gets overriden._\n\n" \
               "To remove a item from your settings do `/ah <itemId>`.\n\n" \
               "*Your current settings are:*\n" \
               "{}"

HIDE_WRONG_ARGS = "Sorry, the /ah command you issued is not valid. Try again."
HIDE_WRONG_LIMIT = "Sorry, the limit you specified is not valid. Try again."
HIDE_WRONG_ITEM = "Sorry, the item `{}` you specified is not valid. Try again."
HIDE_WRONG_PRIORITY = "Sorry, the priority you specified is not valid. Try again."
HIDE_BUY_UNLIMITED = "- P{}: Buy {} (`{}`)\n"
HIDE_BUY_LIMITED = "- P{}: Buy {} (`{}`) for a maximum price of {} 💰\n"
HIDE_ITEM_NOT_TRADABLE = "Sorry, this item is currently not tradable!"
HIDE_REMOVED = "{} was removed from your hiding list!"

SNIPE_WELCOME = "*Use at your own risk! Please report any issues to:* [@BotatoFeedbackBot](tg://user?id=582014258)\n\n" \
               "*Automated buying of items at a given price*\n" \
               "You can set your order via `/s <itemId> <price> [<numberOfItems>]`.\n\n" \
               "Examples: \n" \
               "- `/s 01 10  ` - Buy one Thread for 10💰 or less\n" \
               "- `/s 20 2 10` - Buy Leather for 2💰 or less until 10 are bought\n\n" \
               "_How does it work?_: If your given item is sold for or below the price you specified I will try to buy it. " \
               "It can take some time until this item is available for that price. It is also possible that other " \
               "players are searching for the same item. In this case you need a little bit of luck, although we try " \
               "\"first came, first served\". You can issue `/items` to get a list of items. \n\n" \
               "To remove a buy order `/sr <itemId>`.\n\n" \
               "*Your current orders are:*\n" \
               "{}"

SNIPE_LIMIT_EXCEEDED = "Sorry but you may only have {} orders active at any given time. Please remove another order first."
SNIPE_INITIAL_ORDER_EXCEEDED = "Sorry but you may only order {} pieces at a time. Please reduce your amount."
SNIPE_ITEM_NOT_TRADABLE = "Sorry, this item is currently not tradable!"
SNIPE_WRONG_ARGS = "Sorry, the /s command you issued is not valid. Try again."
SNIPE_WRONG_ARGS_SR = "Sorry, the /sr command you issued is not valid. Try again."
SNIPE_WRONG_LIMIT = "Sorry, the limit you specified is not valid. Try again."
SNIPE_WRONG_ITEM = "Sorry, the item `{}` you specified is not valid. Try again."
SNIPE_BUY_ONE = "- Buy one {} (`{}`) for a price of {}💰\n"
SNIPE_BUY_MULTIPLE = "- Buy {} {} (`{}`) for a price of {}💰 (Remaining: {})\n"
SNIPE_REMOVED = "{} was removed from your order list!"
SNIPED_ITEM = "⚖️Got it! You bought <b>{}</b> for {}💰 ({} x {}💰)\nSeller: {}{}\n\n<i>Note: You can disable this notification in your \"⚙️Settings\".</i>"
SNIPE_DISABLED = "You have to enable sniping in your settings first!"
SNIPE_SUSPENDED = "I have tried to buy an item for you but you don't have the necessary funds. I suspended automated buying until. If you have enough gold again or after you adjusted your buying settings just send me /resume."
SNIPE_SUSPENDED_NOTICE = '*Warning:* Sniping items is currently suspended since you did not have enough funds. You can re-enable it with /resume'

SNIPE_CONTINUED = "Automated buying will now be continued."
SNIPE_NOT_SUSPENDED = "Automated buying is not suspended."
ITEM_LIST = "*Items I know:*\n"
