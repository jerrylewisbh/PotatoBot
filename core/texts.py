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

MSG_EMPTY = '[Пусто]\n'

MSG_START_WELCOME = 'Greetings, warrior! I am the Castle Bot of 🥔Potato castle! Please send me your game profile from @chtwrsbot ("/hero" command).'
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

Команды триггеров:
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
Trigger allowrd: {}
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
MSG_ORDER_CLEARED_ERROR = 'Please stahp!!!!'

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
It was just fence between you.
You decided to walk around and find a way in.
Two hours later you returned to the same place you started at..."""
MSG_PROFILE_SHOW_FORMAT = """\
👤 %first_name% %last_name% (%username%)
%castle% %name%
🏅 %prof% %level% уровня
⚜️ Squad %squad%
⚔️ %attack% | 🛡 %defence% | 🔥 %exp%/%needExp%
💰 %gold% | 🔋 %maxStamina%
%pet%
🕑 Last update %date%"""

# main.py texts
MSG_MAIN_INLINE_BATTLE = 'ГРАБЬНАСИЛУЙУБИВАЙ!'
MSG_MAIN_READY_TO_BATTLE = 'Битва через 10 минут, 🛡🌑 обязательно встаньте в деф, слейте всё золото и ждите приказ'
# -----------------------
MSG_BUILD_REPORT_EXISTS = 'Ты уже кидал этот репорт!'
MSG_BUILD_REPORT_OK = 'Спасибо за помощь на стройке! Это твой {} репорт.'
MSG_BUILD_REPORT_FORWARDED = 'Больше не присылай мне репорты с твинков!!!'
MSG_BUILD_REPORT_TOO_OLD = 'Этот репорт очень стар, я не могу его принять.'

MSG_REPORT_OLD = 'Твой репорт уже попахивает, в следующий раз постарайся прислать его в течении минуты после получения.'
MSG_REPORT_EXISTS = 'Репорт за эту битву уже внесён.'
MSG_REPORT_OK = 'Спасибо. Не забывай кидать репорты каждую битву.'

MSG_PROFILE_NOT_FOUND = 'В лунных записях ещё нет данных об этом герое'
MSG_SQUAD_REQUEST_EMPTY = 'На данный момент к вам никто не хочет.'

MSG_NO_PROFILE_IN_BOT = 'Сначала дай мне профиль!'
MSG_SQUAD_RECRUITING_ENABLED = 'Набор открыт!'
MSG_SQUAD_RECRUITING_DISABLED = 'Набор закрыт!'
MSG_SQUAD_NO_PROFILE = 'Сначала пусть даст профиль!'
MSG_SQUAD_GREEN_INLINE_BUTTON = '✅Да'
MSG_SQUAD_RED_INLINE_BUTTON = '❌Нет'
MSG_SQUAD_NEW = """Теперь здесь будет обитать орден {}!
Не забудьте задать ссылку для приглашения новых участников."""
MSG_SQUAD_LINK_SAVED = """Ссылка приглашений сохранена!
Новые участники теперь не пройдут мимо!"""
MSG_SQUAD_RENAMED = 'Теперь этот орден будет называться {}!'
MSG_SQUAD_DELETE = 'Орден распущен'
MSG_SQUAD_THORNS_ENABLED = 'Непроходимое лунная тень вокруг'
MSG_SQUAD_THORNS_DISABLED = 'Тень луны исчезла, \
теперь каждый может видеть происходящее'
MSG_SQUAD_ALREADY_DELETED = 'Этот пользователь уже изгнан из ордена, кнопка больше не работает =('
MSG_SQUAD_LEVEL_TOO_LOW = 'В отряды принимают воинов {} уровня и выше. Приходи, когда подкачаешься!'

MSG_TRIGGER_NEW = 'Триггер на фразу "{}" установлен.'
MSG_TRIGGER_GLOBAL = '<b>Глобальные:</b>\n'
MSG_TRIGGER_LOCAL = '\n<b>Локальные:</b>\n'
MSG_TRIGGER_NEW_ERROR = 'Какие-то у тебя несвежие мысли, попробуй ещё раз.'
MSG_TRIGGER_EXISTS = 'Триггер "{}" уже существует, выбери другой.'
MSG_TRIGGER_ALL_ENABLED = 'Теперь триггерить могут все.'
MSG_TRIGGER_ALL_DISABLED = 'Теперь триггерить могут только админы.'
MSG_TRIGGER_DEL = 'Триггер на фразу "{}" удалён.'
MSG_TRIGGER_DEL_ERROR = 'Где ты такой триггер видел? 0_о'
MSG_TRIGGER_LIST_HEADER = 'Список текущих триггеров:\n'

MSG_THORNS = 'Этот дурень {} забыл надеть скафандр, пусть луна ему будет пылью'

MSG_WELCOME_DEFAULT = 'Привет, %username%!'
MSG_WELCOME_SET = 'Текст приветствия установлен.'
MSG_WELCOME_ENABLED = 'Приветствие включено.'
MSG_WELCOME_DISABLED = 'Приветствие выключено.'

MSG_PIN_ALL_ENABLED = 'Пусть пинят...'
MSG_PIN_ALL_DISABLED = 'Совсем уже распустились, вот мучайтесь теперь 😡'

MSG_ORDER_CLEARED_BY_DUMMY = 'Функция перерабатывается в связи с высокой \
нагрузкой от постоянного обновления'

MSG_NO_SQUAD = 'Безотрядный тунеядец'
MSG_NO_PET = 'Животины нет'
MSG_WANTS_TO_JOIN = '\n\nХочет вступить в орден {}'

MSG_CLEARED = 'Выполнено'

MSG_SQUAD_LIST = 'Список ваших орденов:'
MSG_SQUAD_REQUEST_EXISTS = 'Вы уже состоите в ордене или подали запрос. \
Выйдите из текущего ордена или отмените запрос, чтобы создать новый.'
MSG_SQUAD_REQUEST = 'Вот ордены, в которые тебя могут принять:'
MSG_SQUAD_LEAVED = '{} покинул орден {}, теперь он бесполезен, \
и никто ему больше не поможет.'
MSG_SQUAD_LEAVE_ASK = 'Ты уверен, что хочешь покинуть отряд?'
MSG_SQUAD_LEAVE_DECLINE = 'Передумал? Ну и славно, пусть это останется в секрете!'
MSG_SQUAD_REQUESTED = 'Ты попросился в орден {}. \
Чтобы ускорить процесс принятия решения, можешь написать главам ордена: {}.'
MSG_SQUAD_REQUEST_ACCEPTED = 'Заявка от {} принята.'
MSG_SQUAD_REQUEST_DECLINED = '{} бесполезен и никто ему не поможет.'
MSG_SQUAD_REQUEST_NEW = 'К вам в орден есть новые заявки.'
MSG_SQUAD_REQUEST_ACCEPTED_ANSWER = 'Вас приняли в орден.'
MSG_SQUAD_REQUEST_DECLINED_ANSWER = 'Ваша заявка в орден отклонена.'
MSG_SQUAD_CLEAN = """Чистка ордена {}.
Кого сегодня отправим на покой?"""
MSG_SQUAD_ADD = '{}, вас хотят в орден. А вы хотите?'
MSG_SQUAD_ADD_IN_SQUAD = '{} уже в ордене (возможно не в вашем).'
MSG_SQUAD_ADD_ACCEPTED = '{} принял предложение.'
MSG_SQUAD_ADD_DECLINED = '{} бесполезен и никто ему не поможет.'
MSG_SQUAD_NONE = 'Похоже ты не в ордене'

MSG_SQUAD_READY = '{} бойцов ордена <b>{}</b> к битве готовы!\n{}⚔ {}🛡'
MSG_FULL_TEXT_LINE = '<b>{}</b>: {}👥 {}⚔ {}🛡\n'
MSG_FULL_TEXT_TOTAL = '\n<b>Всего</b>: {}👥 {}⚔ {}🛡'

MSG_IN_DEV = 'Функция находится в разработке =('

MSG_TOP_ABOUT = '🏆 Топы 🏆'
MSG_STATISTICS_ABOUT = '📈Статистика📈'
MSG_SQUAD_ABOUT = '⚜орден⚜'

MSG_TOP_FORMAT = '{}. {} ({}🌟) - {}{}\n'
MSG_SQUAD_TOP_FORMAT = '{}. {} ({}👥) - {}{} ({}{}/👤)\n'
MSG_TOP_DEFENCE = '🛡Топ дэферы:\n'
MSG_TOP_ATTACK = '⚔Топ атакеры:\n'
MSG_TOP_EXPERIENCE = '🔥Топ качки:\n'
MSG_TOP_GLOBAL_BUILDERS = '⚒Топ строители:\n'
MSG_TOP_WEEK_BUILDERS = '👷Топ строители недели:\n'
MSG_TOP_WEEK_WARRIORS = '⛳️Топ по участию в битвах:\n'

MSG_UPDATE_PROFILE = 'Пришли свежий игровой профиль (🏅 команда "/hero"), пока я не выгнал тебя из ордена.'
MSG_SQUAD_DELETE_OUTDATED = 'Ты был изгнан из ордена за то, что давно не обновлял свой профиль.'
MSG_SQUAD_DELETE_OUTDATED_EXT = '{} (@{}) был изгнан из ордена {} за то, что давно не обновлял свой профиль.'

MSG_ALREADY_BANNED = 'Пользователь уже забанен. Причина: {2}.'
MSG_USER_BANNED = 'Член нашего ордена {} был замечен в нарушении правил и был с позором изгнан из замка!'
MSG_YOU_BANNED = 'Вас изгнали по причине: {}'
MSG_BAN_COMPLETE = 'Изгнание завершено.'
MSG_USER_NOT_BANNED = 'Мы не изгоняли этого господина.'
MSG_USER_UNBANNED = '{} больше не изгнан.'
MSG_YOU_UNBANNED = 'Мы снова можем пообщаться 🌚'

PLOT_X_LABEL = 'Дата'
PLOT_Y_LABEL = 'Опыт'

MSG_DAY_SINGLE = 'день'
MSG_DAY_PLURAL1 = 'дня'
MSG_DAY_PLURAL2 = 'дней'
MSG_DATE_FORMAT = '{} {}'
MSG_PLOT_DESCRIPTION = 'В среднем {} опыта в день. До следующего уровня осталось {} опыта и {}'

MSG_SQUAD_CALL_HEADER = 'Все сюда!\n'
MSG_REPORT_SUMMARY_HEADER = 'Репорты отряда {} за битву {}\n' \
                            'Репорты: {} из {}\n' \
                            '<b>Общие</b>\n' \
                            'Атака: ⚔{}\n' \
                            'Защита: 🛡{}\n' \
                            'Профит: 🔥{} 💰{} 📦{}\n\n' \
                            '<b>Личные</b>\n'
MSG_REPORT_SUMMARY_ROW = '<b>{}</b> (@{})\n⚔{} 🛡{} 🔥{} 💰{} 📦{}\n'
MSG_REPORT_SUMMARY_ROW_EMPTY = '<b>{}</b> (@{}) ❗\n'

BTN_HERO = '🏅Герой'
BTN_STOCK = '📦Склад'
BTN_EQUIPMENT = '🎽Экипировка'

BTN_YES = '✅Да'
BTN_NO = '❌Нет'

BTN_LEAVE = 'Выйти'

BTN_ACCEPT = '✅Принять'
BTN_DECLINE = '❌Отклонить'

BTN_WEEK = "Неделя"
BTN_ALL_TIME = "Всё время"
BTN_SQUAD_WEEK = "Отряды за неделю"
BTN_SQUAD_ALL_TIME = "Отряды за всё время"

MSG_LAST_UPDATE = '🕑 Последнее обновление'
MSG_GO_AWAY = 'Пшёл вон!'
MSG_TOP_GENERATING = 'Генерируем топ'

MSG_NO_REASON = 'Причина не указана'
