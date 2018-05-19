""" Строки """

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

MSG_START_WELCOME = 'Greetings, warrior! I am the Castle Bot of 🥔Potato Castle! \n\n' \
                    'To get things started please send me your game profile from @chtwrsbot ("/hero" command) or select "🔑Register" to allow me direct access to your profile.'
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

MSG_MAIN_READY_TO_BATTLE_45 ='WAAARRR IN 15 MINS!!\
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

MSG_NO_PROFILE_IN_BOT = 'First give me a recent profile!'
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
MSG_SQUAD_REQUEST = 'Here are the requests you have receive:'
MSG_SQUAD_LEAVED = '{} left the squad {} 😰'
MSG_SQUAD_LEAVE_ASK = 'Are you sure you want to leave the squad?'
MSG_SQUAD_LEAVE_DECLINE = 'Have you changed your mind? Well, it is nice, let it remain a secret!'
MSG_SQUAD_REQUESTED = 'You requested to join for the squad {}. \
Be patient, the process is manual and there is a small queue. Plese join the waiting room, Captains will talk to you from there: https://t.me/joinchat/Hm7VckdKMgfB0PpLWJLJtQ '
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
MSG_SQUAD_NONE = 'It looks like you are not in a squad'

MSG_SQUAD_READY = '{} warriors of <b>{}</b> are ready to battle!\n{}⚔ {}🛡'
MSG_FULL_TEXT_LINE = '<b>{}</b>: {}👥 {}⚔ {}🛡\n'
MSG_FULL_TEXT_TOTAL = '\n<b>Total</b>: {}👥 {}⚔ {}🛡'

MSG_IN_DEV = 'Under construction=('

MSG_TOP_ABOUT = '🏆 Tops 🏆'
MSG_STATISTICS_ABOUT = '📈Statistics📈'
MSG_SQUAD_ABOUT = '⚜Squad⚜'

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

MSG_DAY_SINGLE = 'Day'
MSG_DAY_PLURAL1 = 'Day'
MSG_DAY_PLURAL2 = 'Days'
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

ATTACK_ICON  = '⚔'
DEFENSE_ICON = '🛡'
REST_ICON = '🛌'


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
MSG_API_INFO = "By registering you will allow me to automatically update your profile. After this step I can also notify about /stock changes after war.\nRegistering requires three steps. Please bear with me. \n\n @chtwrsbot will send you an authentication code. Please send it back to me to complete registration."
MSG_API_INVALID_CODE = "Sorry, your code is not valid!"
MSG_API_ACCESS_RESET = "API access was reset!"
MSG_API_REQUIRE_ACCESS_STOCK = "Seems like I don't have permission to access your stock yet. You'll get a " \
                               "request from me please forward this code to me!"
MSG_API_REQUIRE_ACCESS_PROFILE = "Seems like I don't have permission to access your profile yet. You'll get a " \
                               "request from me please forward this code to me!"
MSG_API_REVOKED_PERMISSIONS = "It seems I'm unable to access your data. Did you /revoke your permission?"
MSG_API_SETUP_STEP_1_COMPLETE = "👌 First step is complete! Now you will receive another request to allow me access to " \
                                "your profile. Please also forward this code to me."
MSG_API_SETUP_STEP_2_COMPLETE = "👌 Second step is complete! Now as a last step please allow me access to your stock. " \
                                "Please also forward this code to me."
MSG_API_SETUP_STEP_3_COMPLETE = "👌 All set up now! Thank you!"

MSG_CHANGES_SINCE_LAST_UPDATE = "<b>Changes since your last stock update:</b>"

MSG_USER_BATTLE_REPORT = "<b>Your after action report:\n</b>"
MSG_USER_BATTLE_REPORT_PRELIM = "{}{} ⚔:{} 🛡:{} "\
                                "Lvl: {}\n"\
                                "Your result on the battlefield:\n" \
                                "🔥Exp: {}\n" \
                                "💰Gold: {}\n" \
                                "📦Stock: {}\n\n" \
                                "<i>Note: Please send your /report after every battle!\n</i>"
MSG_USER_BATTLE_REPORT_STOCK = "\n{}\n{}\n <i>{}: {}</i>"

#text += "\n\n<b>Please do not forget to forward me your /report command!</b>"

