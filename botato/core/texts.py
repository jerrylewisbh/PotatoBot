""" Строки """
from core.commands import USER_COMMAND_EXCHANGE, USER_COMMAND_HIDE

MSG_ORDER_STATISTIC = 'Statistics of who confirmed the orders for {} days:\n'
MSG_ORDER_STATISTIC_OUT_FORMAT = '{}: {}/{}\n'
MSG_USER_UNKNOWN = 'No such user'

MSG_NEW_GROUP_ADMIN = """Welcome our new administrator: @{}!
Check the list with /help command"""
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

MSG_START_NEW = """Greetings, warrior! I am the Castle Bot of 🥔Potato Castle!

To get things started please forward me your game profile from @chtwrsbot ("/hero" command)."""

MSG_START_KNOWN = """Welcome back, warrior! I am the Castle Bot of 🥔Potato Castle!

If you want to refresh your game profile forward me your "/hero" from @chtwrsbot.

<b>I also suggest you join one of our squads!</b> 
This way we can better coordinate our battles. After joining you can also get automated stock change information after war, get notified if you sell something or automatically buy cheap things in the Exchange (sniping). To get things started just click the ⚜Squad Button."""

MSG_START_MEMBER_SQUAD = """Hi 🥔{}!

As a squad member you can choose "🔑Register" to allow me direct access to your profile and get automated stock change information after war, get notified if you sell something or automatically buy cheap things in the Exchange (sniping)."""

MSG_START_MEMBER_SQUAD_REGISTERED = 'Welcome back 🥔{}!\n\n' \
                                    'How can I help you today?'

MSG_ADMIN_WELCOME = 'Welcome, master!'

MSG_PING = 'Go and dig some potatoes, @{}! - `{:.2f}ms`'

MSG_STOCK_COMPARE_HARVESTED = '📦<b>You got:</b>\n'
MSG_STOCK_COMPARE_LOST = '\n📦<b>You lost:</b>\n'
MSG_STOCK_OVERALL_CHANGE = '\n<b>Estimated change:</b> {0:+}💰\n'
MSG_STOCK_COMPARE_W_PRICE = '{} <i>({} x {} = {}💰)</i>\n'
MSG_STOCK_COMPARE_WO_PRICE = '{} ({})\n'
MSG_STOCK_COMPARE_WAIT = 'Waiting for data to compare...'
MSG_STOCK_PRICE = "{} <i>({} x {} = {}💰)</i>\n"
MSG_STOCK_OVERALL_PRICE = "\nEstimated overall worth: {}💰\n"

MSG_PERSONAL_SITE_LINK = 'Your personal link: {}'

MSG_GROUP_STATUS_CHOOSE_CHAT = 'Choose chat'
MSG_GROUP_STATUS = """<b>Group: {}</b>
ID: {}

Bot in Group: {}
Members in Group: {}
Admins in Group: {}
Link: {}

<i>Botato-Admins:</i>
{}

<i>Settings:</i>
Welcome: {}
Trigger allowed: {}
FWD Minireport: {}
Thorns: {}
Silence: {}
Reminders: {}
Bots allowed: {}"""

MSG_GROUP_STATUS_SQUAD = """

<b>This group is linked to a squad!</b>

<i>Squad Settings:</i>
Hiring: {}
Testing Squad: {}

<b>Be careful, deleting this group also deletes the squad!</b>"""


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
MSG_ORDER_SEND_HEADER = """<b>Where to send this order?</b>

<b>Order:</b>
{}

<i>Important: Do not use "Button" for battle orders as this slows down the order process considerably!</i>"""

MSG_ORDER_GROUP_CONFIG_HEADER = 'Group settings: {}'
MSG_ORDER_GROUP_NEW = 'Send me the name of a new group of squad'
MSG_ORDER_GROUP_LIST = 'These are the existing groups:'
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


# main.py texts
MSG_MAIN_READY_TO_BATTLE_30 = """❗️⚔ <b>War in 30 minutes</b> ⚔️❗️

📦💰 <a href="http://telegra.ph/BASICS-OF-HIDING-GOLD-08-02">Hide your gold and stock</a>!
Equip your dagger 🗡/ shield 🛡

Set default status to DEF 🛡 and wait for orders."""

MSG_MAIN_READY_TO_BATTLE_45 = """❗️⚔ <b>War in 15 minutes</b> ⚔️❗

1) 📦💰 <a href="http://telegra.ph/BASICS-OF-HIDING-GOLD-08-02">Hide your gold and stock NOW</a>!
2) Press 🛡 in the game bot
3) Press "⚔️ Attack" to the state of "Ha, bold enough? Choose an enemy!" and wait for orders!
4) Keep Battle-Silence in this group from xx:57:00 till xx:00:00 

<b>Remember:</b> Be prepared to <a href="http://telegra.ph/Orders-coming-Late-A-short-guide-to-turn-fast-02-05">turn fast</a> if orders change!

@chtwrsbot"""

MSG_MAIN_SEND_REPORTS = """⚔ Battle is over! ⚔️

📜 Please send your <a href="https://t.me/share/url?url=/report">/report</a> to @PotatoCastle_bot"""

MSG_BUILD_REPORT_EXISTS = 'This report already exists!'
MSG_BUILD_REPORT_OK = 'Thanks for the help! This is your {} report.'
MSG_BUILD_REPORT_FORWARDED = 'Do not send me any more reports from alternative accounts !!! '
MSG_BUILD_REPORT_TOO_OLD = 'This report is very old, I can not accept it.'

MSG_REPORT_OLD = 'Your report stinks like rotten potato, next time try to send it within a minute after receiving.'
MSG_REPORT_EXISTS = 'The report for this battle has already been submitted.'
MSG_REPORT_MISSING = "No report for this period! Please forward me your /report from @chtwrsbot."

MSG_PROFILE_NOT_FOUND = 'In the potato plantation records, there is still no data about this hero or you are not ' \
                        'permitted to see him.'
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
MSG_GROUP_THORNS_ENABLED = 'The straw man in around, only members can be here'
MSG_GROUP_THORNS_DISABLED = 'The straw man disappeared, \
now everyone can see what is happening'

MSG_GROUP_SILENCE_ENABLED = 'Battle silence enabled, messages will be deleted 3 minutes before battle'
MSG_GROUP_SILENCE_DISABLED = 'Battle silence disabled'

MSG_GROUP_REMINDERS_ENABLED = 'This squad will automatically be reminded of battles and reports, lazy captain'
MSG_GROUP_REMINDERS_DISABLED = 'This squad will NOT be automatically reminded of battles and reports, do not let them forget 👀'

MSG_GROUP_BOTS_ALLOWED = 'Bots can join this group now. Be aware of spais!'
MSG_GROUP_BOTS_DENIED = 'Bots can no longer join this group.'

MSG_SQUAD_ALREADY_DELETED = 'This user is already expelled from the squad, this button no longer works.'
MSG_SQUAD_LEVEL_TOO_LOW = 'This squad takes soldiers at level {} and above. Come back when you get pumped!'

MSG_TRIGGER_NEW = 'The trigger for the phrase "{}" is set.'
MSG_TRIGGER_GLOBAL = '<b>Global:</b>\n'
MSG_TRIGGER_LOCAL = '\n<b>Local:</b>\n'
MSG_TRIGGER_NEW_ERROR = 'You thoughts are not clear, try one more time'
MSG_TRIGGER_EXISTS = 'Trigger "{}" already exists, select another one.'
MSG_TRIGGER_ALL_ENABLED = 'Now everybody can call triggers.'
MSG_TRIGGER_ALL_DISABLED = 'Now only admins can call triggers.'
MSG_TRIGGER_DEL = 'The trigger for "{}" has been deleted.'
MSG_TRIGGER_DEL_ERROR = 'Where did you see such a trigger? 0_o'
MSG_TRIGGER_LIST_HEADER = 'List of current triggers: \n'

MSG_THORNS = 'This fool does not look like a potato, let the straw man kick his ass!'
MSG_THORNS_NAME = 'This fool @{} does not look like a potato, let the straw man kick his ass!'

MSG_WELCOME_DEFAULT = 'Hi, %username%!'
MSG_WELCOME_SET = 'The welcome text is set.'
MSG_WELCOME_ENABLED = 'Welcome enabled'
MSG_WELCOME_DISABLED = 'Welcome disabled'
MSG_MINI_REPORT_FWD_DISABLED = 'Mini Report forward disabled'
MSG_MINI_REPORT_FWD_ENABLED = 'Mini Report forward enabled'

MSG_NO_PERMISSION_TO_ADD_BOT = "Sorry but you do not have permission to add me to a group. Please ask a council member or someone admin. You can also contact [@BotatoFeedbackBot](tg://user?id=582014258)."

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
MSG_SQUAD_REQUEST_EXISTS = 'You are already have requested to enter a squad. \
Exit the current squad or cancel the request to create a new one. '
MSG_SQUAD_REQUEST = 'Here are the requests you have received:'
MSG_SQUAD_LEFT = '{} left the squad {} 😰'
MSG_SQUAD_LEAVE_ASK = 'Are you sure you want to leave the squad?'
MSG_SQUAD_LEAVE_DECLINE = 'Have you changed your mind? Well, it is nice, let it remain a secret!'

MSG_SQUAD_REQUESTED = """<b>You requested to join the squad "{}"!</b> 

Please be patient as this is a manual process."""

MSG_ACADEMY_REQUESTED = """<b>You requested to join the squad "{}"!</b> 

Please be patient as this is a manual process and there is a small queue. Join our waiting room. Our captains will take care of you and guide you through the process.

<a href="{}">Potato Castle Waiting Room</a>"""

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
MSG_SQUAD_ADD_DECLINED = '{} declined! 😰'

MSG_SQUAD_READY = '{} warriors of <b>{}</b> are ready to battle!\n{}⚔ {}🛡'
MSG_FULL_TEXT_LINE = '<b>{}</b>: {}👥 {}⚔ {}🛡\n'
MSG_FULL_TEXT_TOTAL = '\n<b>Total</b>: {}👥 {}⚔ {}🛡'

MSG_TOP_ABOUT = '🏆 Select the statistics you want to see'
MSG_STATISTICS_ABOUT = '📈Statistics📈'
MSG_SQUAD_ABOUT = 'You are a member of the Squad "{}"'
MSG_SQUAD_NONE = 'You are currently not a member of any squad. Select "⚜Join Squad" to join one!'

MSG_TOP_FORMAT = '{}. {} (Level {}) - {}{}\n'
MSG_TOP_FORMAT_REDUCED = '{}. {} (Level {})\n'
MSG_SQUAD_TOP_FORMAT = '{}. {} ({}👥) - {}{} ({}{}/👤)\n'

MSG_TOP_DEFENCE = '🛡Top Defenders:\n\n'
MSG_TOP_ATTACK = '⚔Тop Attackers:\n\n'
MSG_TOP_EXPERIENCE = '🔥Top XP:\n\n'

MSG_TOP_DEFENCE_CLASS = '🛡Top Defenders for class {}:\n\n'
MSG_TOP_ATTACK_CLASS = '⚔Тop Attackers for class {}:\n\n'
MSG_TOP_EXPERIENCE_CLASS = '🔥Top XP for class {}:\n\n'

MSG_TOP_DEFENCE_SQUAD = '🛡Top Defenders for squad {}:\n\n'
MSG_TOP_ATTACK_SQUAD = '⚔Тop Attackers for squad {}:\n\n'
MSG_TOP_EXPERIENCE_SQUAD = '🔥Top XP for squad {}:\n\n'

MSG_TOP_WEEK_WARRIORS = '⛳️Top attendance:\n\n'
MSG_TOP_WEEK_WARRIORS_SQUAD = '⛳Top attendance in Squad "{}":\n\n'
MSG_TOP_WEEK_WARRIORS_CLASS = '⛳Top {} battle attendance {}:\n\n'
MSG_TOP_SQUAD = '<b>Squad TOP:</b>\n'

MSG_UPDATE_PROFILE = 'Send me a new profile (🏅 command "/hero"), or you might be kicked off.'
MSG_SQUAD_DELETE_OUTDATED = 'You were kicked from the squad for not updating your profile for a long time.'
MSG_SQUAD_DELETE_OUTDATED_EXT = '{} (@{}) was kicked from {} for not updating profile for a long time.'

MSG_ALREADY_BANNED = 'This user is already banned.'
MSG_USER_BANNED = '{} violated the rules and was kicked off!\nReason: {}'
MSG_USER_BANNED_NO_REASON = '{} violated the rules and was kicked off!'
MSG_USER_BANNED_UNAUTHORIZED = "🚨🚨🚨 {} violated the rules but can't be removed from these groups!\nReason: {}\nGroups: {}"

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
MSG_REPORT_SUMMARY_HEADER = 'Reports of the squad {} for the battle {}\n' \
                            'Report: {} from {}\n' \
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



MSG_REPORT_SUMMARY_ROW = '{} <b>{}</b> (@{})\n       ⚔{} 🛡{} 🔥{} 💰{} 📦{}\n'
MSG_REPORT_SUMMARY_ROW_EMPTY = '<b>{}</b> (@{}) ❗\n'


BTN_HERO = '🏅Hero'
BTN_STOCK = '📦Stock'
BTN_EQUIPMENT = '🎽Equipment'
BTN_SKILL = '🏛Skills'
BTN_KICK = '🗑️Kick'

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

BTN_PLEDGE_YES = "I got a pledge!"
BTN_PLEDGE_NO = "No"

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

MSG_USER_BATTLE_REPORT = "{}{} ⚔:{} 🛡:{} "\
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
                    "- Sniping: {}\n" \
                    "- Hide Gold: {}\n\n" \
                    "<i>Last profile update: {}</i>\n" \
                    "<i>Last stock update: {}</i>"
MSG_NEEDS_API_ACCESS = "Requires API Access. Please 🔑Register"
MSG_NEEDS_TRADE_ACCESS = 'This requires trade permissions. I will request them once you select "{}" or "{}".'.format(
    USER_COMMAND_EXCHANGE,
    USER_COMMAND_HIDE)

MSG_NO_REPORT_PHASE_BEFORE_BATTLE = "War is coming! Your Stock and Profile is getting updated automatically. No need to forward your data just yet!"
MSG_NO_REPORT_PHASE_AFTER_BATTLE = "War is over but I don't accept reports just yet! I will remind you when it is time."

MSG_DEAL_SOLD = "⚖️You sold <b>{}</b> for {}💰 ({} x {}💰)\nBuyer: {}{}\n\n<i>Note: You can disable this notification in your \"⚙️Settings\".</i>"

MSG_QUEST = "<b>Please tell me where did you quest?</b>\n\n<i>{}</i>"
MSG_QUEST_DUPLICATE = "You already told me about this particular quest!"
MSG_QUEST_OK = "Your adventure took place in {}. Thank you for your quest details!"
MSG_QUEST_ACCEPTED = "Thank you for sending in this quest."
MSG_FORAY_ACCEPTED = "Thank you for sending in your successful 🗡Foray."
MSG_FORAY_FAILED = "Thank you for sending me this 🗡Foray information."
MSG_FORAY_ACCEPTED_KNIGHT = "Thank you for sending in your successful 🗡Foray. Where you offered to /pledge your allegiance to a village?"
MSG_FORAY_ACCEPTED_SAVED_PLEDGE = "Congratulations! You were offered a new pledge. Thank you for this information!"
MSG_FORAY_ACCEPTED_SAVED = "You unfortunately did not get a new /pledge. Thank you for this information!"

MSG_ARENA_ACCEPTED = "Thank you for sending in your successful 📯Arena fight!"
MSG_ARENA_FAILED = "Thank you for sending in your failed 📯Arena fight! Cheer up!"

MSG_FORAY_PLEDGE = "Please send in your Foray result and choose there if your pledge was successful."
MSG_QUEST_7_DAYS = "*In the last seven days you told me about the following adventures:*\n\n"
MSG_QUEST_STAT_LOCATION = "*{} ({})*: \n" \
                          "Avg: {:.2f}🔥, {:.2f}💰, {:.2f}📦\n" \
                          "Ttl: {:.2f}🔥, {:.2f}💰, {:.2f}📦\n"
MSG_QUEST_STAT_NO_LOOT = "*{} ({})*: \n" \
    "Avg: {:.2f}🔥, {:.2f}💰\n" \
    "Ttl: {:.2f}🔥, {:.2f}💰\n"
MSG_FORAY_INTRO = "Statistics for all forays I know. Forward them to me to get " \
                  "more detailed stats! This graph also contains /pledge rate for knights.\n\n" \
                  "_Tip: Your personal statistics can be found in 🗺Quests_"

MSG_ITEM_STAT = "*Item droprates:*"

MSG_GAME_TIMES = """Time in UTC and In-Game daytime:
+------------+----------------+----------------+----------------+
|   State    |    Cycle 1     |    Cycle 2     |    Cycle 3     |
+------------+----------------+----------------+----------------+
| Morning:   | 23:00 to 01:00 | 07:00 to 09:00 | 15:00 to 17:00 |
| Day:       | 01:00 to 03:00 | 09:00 to 11:00 | 17:00 to 19:00 |
| Dawn:      | 03:00 to 05:00 | 11:00 to 13:00 | 19:00 to 21:00 |
| Night:     | 05:00 to 07:00 | 13:00 to 15:00 | 21:00 TO 23:00 |
+------------+----------------+----------------+----------------+"""

MSG_QUEST_STAT_FORAY = "Success rate: {: .2f}% / Pledge rate: {: .2f}%\n"
MSG_QUEST_BASIC_STAT = "Success rate: {: .2f}%\n"

MSG_QUEST_OVERALL = "\n\n*Overall:*\n\n"

MSG_QUEST_STAT = "\n\nJust continue sending me your quest reports.\n\n_Hint: Overall statistics, item details, etc. coming soonish..._"

# Exchange stuff
HIDE_WELCOME = "*Use at your own risk! Please report any issues to:* [@BotatoFeedbackBot](tg://user?id=582014258)\n\n" \
               "*With this feature enabled I will try to spend all your gold once you issue /hide.*\n\n" \
               "You can set your buy-preferences via `/ah <itemId> <prio> <maxPrice>`.\n" \
               "Leave `<maxPrice>` out to always buy at market price. You can get a list of items with `/items`. \n\n" \
               "Examples: \n" \
               "- `/ah 01 1 30` to buy Thread for a maximum price of 30 💰 until you can't afford another one\n" \
               "- `/ah 20 2` to buy Leather for the lowest price currently on the market until you can't buy any more of it.\n\n" \
               "_Note: If you already have set an order for one priority this gets overriden._\n\n" \
               "To remove an item from your settings do `/ah <itemId>`.\n\n" \
               "*Your current settings are:*\n" \
               "{}"
HIDE_DISABLED = "You have to enable hiding in your settings first!"
HIDE_STARTED = "Started hiding. This can take a few minutes. I'll notify you when I'm done. _Note: If you are currently busy questing this will not work and you have to start over!_"
HIDE_WRONG_ARGS = "Sorry, the /ah command you issued is not valid. Try again."
HIDE_WRONG_LIMIT = "Sorry, the limit you specified is not valid. Try again."
HIDE_WRONG_ITEM = "Sorry, the item `{}` you specified is not valid. Try again."
HIDE_WRONG_PRIORITY = "Sorry, the priority you specified is not valid. Try again."
HIDE_BUY_UNLIMITED = "- P{}: Buy {} (`{}`)\n"
HIDE_BUY_LIMITED = "- P{}: Buy {} (`{}`) for a maximum price of {} 💰\n"
HIDE_ITEM_NOT_TRADABLE = "Sorry, this item is currently not tradable!"
HIDE_REMOVED = "{} was removed from your hiding list!"
HIDE_RESULT_INTRO = "<b>Hiding finished! Your results:\n</b>"
HIDE_BOUGHT = "You bought <b>{}</b> for {}💰\n"
HIDE_LIST = "*Choose items to hide and forward to Chatwars:*"

SNIPE_LIST = "*Current snipe orders:*\n"
SNIPE_LIST_ITEM = '`{}` {} - Orders: {} / Items: {} / Min: {} / Max: {}\n'
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

AUCTION_WELCOME = """*Notify on new auctions (BETA!):*
Put items on your watchlist with `/watch <itemId> [<maxPrice>]`. You can skip <maxPrice> if you want to be notified of all auctions for that item. 

Example: `/watch k09 31` notifies you if Order Gauntlets part is on auction for 31👝 or less

To remove an item from your watchlist simply issue `/watch <itemId>` again.
    
*Your items on the watchlist are:*
{}"""

# TODO: *Search for items:*
# - Search for all items currently up for auctions: `/lots <itemId>`. For example: `/lots k09` for all Order Gauntlet parts.

AUCTION_NOTIFY_UNLIMITED = "- {}\n"
AUCTION_NOTIFY_LIMITED = "- {} with max price {} 👝\n"
AUCTION_ITEM_NOT_TRADABLE = "Sorry, this item is currently not auctionable!"
AUCTION_REMOVED = "{} was removed from your watchlist!"
AUCTION_NOTIFICATION = """{} up for auction! 

Seller: {}{}
Current price: {}
Buyer: {}
End At: {}

/bet_{}"""

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
SNIPE_SUSPENDED_NOTICE = 'Warning: Sniping items is currently suspended since you did not have enough funds. You can re-enable it with /resume'

SNIPE_CONTINUED = "Automated buying will now be continued."
SNIPE_NOT_SUSPENDED = "Automated buying is not suspended."
ITEM_LIST = "*Items I know:*\n"


GUILD_DEPOSIT = "*Deposit:*"
GUILD_WITHDRAW = "*Withdraw:*"
GUILD_WITHDRAW_HELP = "Please forward me your Guild Warehouse"

MSG_HELP_GLOBAL_ADMIN = """<b>Available Commands:</b>

<i>General stuff:</i>
/start - Start interacting with Botato
/help - Show this help

<i>Admin:</i>
/admin - Show admin-panel
/ping - Ping botato
/list_admins — show list of current chat administrators
/add_admin &lt;user&gt; — add administrator to current chat
/add_global_admin &lt;user&gt; — add global administrator
/del_admin &lt;user&gt; — delete administrator from current chat
/del_global_admin &lt;user&gt; — delete global administrator 
/get_log - Get logfile - ONLY FOR A FEW PPL
/force_kick_botato - Force Botato to leave group
/kick - Reply to any message to kick the user from a chat
/ban &lt;user&gt; &lt;reason&gt;  - Ban user 
/unban &lt;user&gt; - Unban user 
/ban_list - List banned
/find &lt;user&gt; - Show user status by telegram user name
/findc &lt;ign&gt; - Show user status by ingame name
/findi &lt;id&gt; - Show user status by telegram uquique id
/battleresult - Send last battle-result to government chat 


<i>Groups and Squads:</i>
/enable_welcome - Enable welcome message 
/disable_welcome — Disable welcome message
/set_welcome &lt;text&gt; — set welcome message (Can contain %username% — will be shown as @username, %ign% - will show user ingame name, if not set to First and Last name, or ID, using %last_name%, %first_name%, %id%)
/show_welcome — Show welcome message
/enable_trigger — Allow everyone to call trigger
/disable_trigger — Forbid everyone to call trigger
/enable_report_forward - Enable report forwarding
/disable_report_forward - Disable report forwarding
/enable_thorns - Prevent non members of the squad be in the group
/disable_thorns - Allow non members of the group to be in the squad
/enable_silence  - Deletes all messages typed 3 minutes before battle
/disable_silence - Allow user to type even 3 minutes before batte
/enable_reminders  - Turn on automatated battle reminder 30+45 minutes before battle and reminder afterwards
/disable_reminders - Disable reminders
/allow_bots - Allow bots to be joined into this channel
/deny_bots - Do not allow bots to be joined into this channel
/delete - Reply to message with /delete will delete that message
/pin - Reply to message will pin this message 
/pin_notify - Reply to message will pin this message and notify
/disable_pin_all - Disable pinning for everyone 
/enable_pin_all - Allow pinning for everyone
/commander - Show admins of Squad/Group
/admins - Show admins of Squad/Group

<i>Triggers:</i>
/list_triggers — show all triggers
/set_trigger - Reply to a message or file /set_trigger &lt;trigger name&gt; to set a new trigger
/del_trigger &lt;trigger&gt; — delete trigger
/add_trigger - Same as /set_trigger but does not override existing ones
/set_global_trigger - Reply to a message with /set_global_trigger &lt;trigger name&gt; to set a new trigger (all chats)
/add_global_trigger - Same as /set_global_trigger but does not override existing ones
/del_global_trigger &lt;trigger&gt; — delete trigger

<i>Squads:</i>
/add_squad - Create a new squad and associates it to the current group
/del_squad - Delete the squad associated with the group
/set_squad_name &lt;name&gt; - Change the name of the squad
/set_invite_link &lt;link&gt; - Set up the invite link 
/add &lt;user&gt; - Ask an user to join the squad
/forceadd &lt;user&gt; - add user to a squad without asking
/hiring_open - Open hiring
/hiring_close - Close hiring
/squad - Call every squadmember 
/daily_stats - Show daily squad stats
/weekly_stats - Show weekly squad stats
/battle_stats - Show battlestats

<i>User commands:</i>
/me - Show your profile 
/report - Show your last report
/admins - Show Admins/Commanders
/commander - Show Admins/Commanders
/items - List known exchange-tradable items
/items_other - List known untradable items
/items_unknown - Show new items
/hide - Manually trigger hide
/hide_list - Show commands to put your items for 1000g in exchange - Sorted by price
/ah - Auto-Hide settings
/resume - Resume suspended sniping
/s &lt;itemID&gt; &lt;maxPrice&gt; [&lt;limit&gt;] - Create snipe order
/sr &lt;itemID&gt; - Remove sniping order
/report - Show your last report (including stock change if API is enabled)
/deposit - Generate deposit-list for guild
/withdraw - Generate withdraw-list
/roll - Roll a dice (1-6). You can specify your own number of dice and how many sides the dice has with /roll <num>d<sides>"""

MSG_HELP_GROUP_ADMIN= """<b>Available Commands:</b>

<i>General stuff:</i>
/start - Start interacting with Botato
/help - Show this help

<i>Admin:</i>
/admin - Show admin-panel
/ping - Ping botato
/list_admins — show list of current chat administrators
/add_admin &lt;user&gt; — add administrator to current chat
/del_admin &lt;user&gt; — delete administrator from current chat
/force_kick_botato - Force Botato to leave the chat where this command was issued
/kick - Reply to any message to kick the user from a chat
/ban &lt;user&gt; &lt;reason&gt;  - Ban user
/ban_list - List banned 
/unban &lt;user&gt; - Unban user 
/user_info - Get info for user regarding bans/restrictions 
/find &lt;user&gt; - Show user status by telegram user name
/findc &lt;ign&gt; - Show user status by ingame name
/findi &lt;id&gt; - Show user status by telegram uquique id
/battleresult - Send last battle-result to government chat 


<i>Groups and Squads:</i>
/enable_welcome - Enable welcome message 
/disable_welcome — Disable welcome message
/set_welcome &lt;text&gt; — set welcome message (Can contain %username% — will be shown as @username, %ign% - will show user ingame name, if not set to First and Last name, or ID, using %last_name%, %first_name%, %id%)
/show_welcome — Show welcome message
/enable_trigger — Allow everyone to call trigger
/disable_trigger — Forbid everyone to call trigger
/enable_report_forward - Enable report forwarding
/disable_report_forward - Disable report forwarding
/enable_thorns - Prevent non members of the squad be in the group
/disable_thorns - Allow non members of the group to be in the squad
/enable_silence  - Deletes all messages typed 3 minutes before battle
/disable_silence - Allow user to type even 3 minutes before batte
/enable_reminders  - Turn on automatated battle reminder 30 and 45 minutes before battle and report reminder 10 minutes after battle
/disable_reminders - Disable reminders
/allow_bots - Allow bots to be joined into this channel
/deny_bots - Do not allow bots to be joined into this channel
/delete - Reply to message with /delete will delete that message
/pin - Reply to message will pin this message 
/pin_notify - Reply to message will pin this message and notify people
/disable_pin_all - Disable pinning for everyone 
/enable_pin_all - Allow pinning for everyone
/commander - Show admins of Squad/Group
/admins - Show admins of Squad/Group

<i>Triggers:</i>
/list_triggers — show all triggers
/set_trigger - Reply to a message or file /set_trigger &lt;trigger name&gt; to set a new trigger
/del_trigger &lt;trigger&gt; — delete trigger
/add_trigger - Same as /set_trigger but does not override existing ones
/set_global_trigger - Reply to a message or file with /set_global_trigger &lt;trigger name&gt; to set a new trigger (all chats)
/add_global_trigger - Same as /set_global_trigger but does not override existing ones
/del_global_trigger &lt;trigger&gt; — delete trigger

<i>Squads:</i>
/add_squad - Create a new squad and associates it to the current group
/del_squad - Delete the squad associated with teh group
/set_squad_name &lt;name&gt; - Change the name of the squad
/set_invite_link &lt;link&gt; - Set up the invite link that will be sent to approved members
/add &lt;user&gt; - Ask an user to join the squad
/forceadd &lt;user&gt; - add user to a squad without asking for confirmation
/hiring_open - Open hiring
/hiring_close - Close hiring
/squad - Call every squadmember to get their attention
/daily_stats - Show daily squad stats
/weekly_stats - Show weekly squad stats
/battle_stats - Show battlestats

<i>User commands:</i>
/me - Show your profile 
/report - Show your last report
/admins - Show Admins/Commanders
/commander - Show Admins/Commanders
/items - List known exchange-tradable items
/items_other - List known untradable items
/items_unknown - Show new items
/hide - Manually trigger hide
/hide_list - Show commands to put your items for 1000g in exchange - Sorted by price
/ah - Auto-Hide settings
/resume - Resume suspended sniping
/s &lt;itemID&gt; &lt;maxPrice&gt; [&lt;limit&gt;] - Create snipe order
/sr &lt;itemID&gt; - Remove sniping order
/report - Show your last report (including stock change if API is enabled)
/deposit - Generate deposit-list for guild
/withdraw - Generate withdraw-list
/roll - Roll a dice (1-6). You can specify your own number of dice and how many sides the dice has with /roll <num>d<sides>"""

MSG_HELP_USER = """<b>Available Commands:</b>

<i>General stuff:</i>
/start - Start interacting with Botato
/help - Show this help

<i>Triggers:</i>
/list_triggers — show all triggers

<i>User commands:</i>
/me - Show your profile 
/report - Show your last report
/admins - Show Admins/Commanders
/commander - Show Admins/Commanders
/items - List known exchange-tradable items
/items_other - List known untradable items
/items_unknown - Show new items
/hide - Manually trigger hide
/hide_list - Show commands to put your items for 1000g in exchange - Sorted by price
/ah - Auto-Hide settings
/resume - Resume suspended sniping
/s &lt;itemID&gt; &lt;maxPrice&gt; [&lt;limit&gt;] - Create snipe order
/sr &lt;itemID&gt; - Remove sniping order
/report - Show your last report (including stock change if API is enabled)
/deposit - Generate deposit-list for guild
/withdraw - Generate withdraw-list
/roll - Roll a dice (1-6). You can specify your own number of dice and how many sides the dice has with /roll <num>d<sides>"""


MSG_HELP_INTRO = """Welcome, this bot is intended to make your life as a Potato easier and to better coordinate our castle."""

MSG_HELP_TOOLS = """Here are some other useful commands:

/deposit - Sends you a list of items you can deposit to your guild storage.
/withdraw - Forward your guild-stock to me and I will send you a list of withdraw-commands
/items - List all items that are tradable at the exchange
/items_other - List all items that are NOT tradable on the exchange
"""
