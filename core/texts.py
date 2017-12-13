""" Строки """

MSG_ORDER_STATISTIC = 'Статистика выполнения приказов за {} дней:\n'
MSG_ORDER_STATISTIC_OUT_FORMAT = '{}: {}/{}\n'
MSG_USER_UNKNOWN = 'Не знаю таких'

MSG_NEW_GROUP_ADMIN = """Приветствуйте нового админа: @{}!
Для списка команд бота используй /help"""
MSG_NEW_GROUP_ADMIN_EXISTS = '@{} и без тебя тут правит!'

MSG_DEL_GROUP_ADMIN_NOT_EXIST = 'У @{} здесь нет власти!'
MSG_DEL_GROUP_ADMIN = '@{}, тебя разжаловали.'

MSG_NEW_GLOBAL_ADMIN = 'Новый глобальный админ: @{}!'
MSG_NEW_GLOBAL_ADMIN_EXISTS = '@{} и без тебя админ!'

MSG_DEL_GLOBAL_ADMIN_NOT_EXIST = 'У @{} нет власти!'
MSG_DEL_GLOBAL_ADMIN = '@{} разжалован.'

MSG_NEW_SUPER_ADMIN = 'Новый суперадмин: @{}!'
MSG_NEW_SUPER_ADMIN_EXISTS = '@{} уже суперадмин!'

MSG_LIST_ADMINS_HEADER = 'Список здешних админов:\n'
MSG_LIST_ADMINS_FORMAT = '{} @{} {} {}\n'
MSG_LIST_ADMINS_USER_FORMAT = '@{} {} {}\n'

MSG_EMPTY = '[Пусто]\n'

MSG_START_WELCOME = 'Привет! Я - бот 🌑Замка Лунного Света. Перешли мне свой игровой профиль из @chtwrsbot (🏅 команда "/hero").'
MSG_ADMIN_WELCOME = 'Да здравствует админ!'

MSG_HELP_GLOBAL_ADMIN = """Команды приветствия:
/enable_welcome — включить приветствие.
/disable_welcome — выключить приветствие.
/set_welcome <текст> — установить текст приветствия. \
Может содержать %username% — будет заменено на @username, \
если не установлено на Имя Фамилия, %first_name% — на имя, 
%last_name% — на фамилию, %id% — на id.
/show_welcome — показать текущий текст приветствия для данного чата.

Команды триггеров:
присылаем фаил, ответом на него присылаем команду /set_trigger <сообщение> — \
установить сообщение, которое бот будет отправлять по триггеру. /установить тригер
/add_trigger <триггер>::<сообщение> — \
добавить сообщение, которое бот будет отправлять по триггеру. \
Старое сообщение не заменяется./добавить триггер

/del_trigger <триггер> — удалить триггер.
/list_triggers — показать все триггеры.

Команды суперадмина:
/add_admin <пользователь> — добавить админа для текущего чата.
/del_admin <пользователь> — забрать привилегии у админа текущего чата.
/list_admins — показать список админов в чате.
/enable_trigger — разрешить триггерить всем в группе.
/disable_trigger — запретить триггерить всем в группе.
"""

MSG_HELP_GROUP_ADMIN = """Команды приветствия:
/enable_welcome — включить приветствие.
/disable_welcome — выключить приветствие.
/set_welcome <текст> — установить текст приветствия. \
Может содержать %username% — будет заменено на @username, \
если не установлено на Имя Фамилия, %first_name% — на имя, 
%last_name% — на фамилию, %id% — на id.
/show_welcome — показать текущий текст приветствия для данного чата.

Команды триггеров:
/add_trigger <триггер>::<сообщение> — \
добавить сообщение, которое бот будет отправлять по триггеру. \
Старое сообщение не заменяется.
/list_triggers — показать список триггеров.
/enable_trigger — разрешить триггерить всем в группе.
/disable_trigger — запретить триггерить всем в группе.
"""

MSG_HELP_USER = "/list_triggers — показать список триггеров."

MSG_PING = 'Иди освежись, @{}!'

MSG_STOCK_COMPARE_HARVESTED = '📦<b>Награблено:</b>\n'
MSG_STOCK_COMPARE_LOST = '\n📦<b>Потеряно:</b>\n'
MSG_STOCK_COMPARE_FORMAT = '{} ({})\n'
MSG_STOCK_COMPARE_WAIT = 'Жду с чем сравнивать...'

MSG_PERSONAL_SITE_LINK = 'Твоя персональная ссылка на сайт: {}'

MSG_GROUP_STATUS_CHOOSE_CHAT = 'Выбери чат'
MSG_GROUP_STATUS = """Группа: {}

Админы:
{}
Приветствие: {}
Триггерят все: {}
Тернии: {}"""

MSG_GROUP_STATUS_ADMIN_FORMAT = '{} @{} {} {}\n'
MSG_GROUP_STATUS_DEL_ADMIN = 'Разжаловать {} {}'

MSG_ON = 'Включено'
MSG_OFF = 'Выключено'
MSG_SYMBOL_ON = '✅'
MSG_SYMBOL_OFF = '❌'
MSG_BACK = '🔙Назад'

MSG_ORDER_TO_SQUADS = 'По орденам'
MSG_ORDER_ACCEPT = 'Принято!'
MSG_ORDER_PIN = '✅Пинить'
MSG_ORDER_NO_PIN = '❌Не Пинить'
MSG_ORDER_BUTTON = '✅С кнопкой'
MSG_ORDER_NO_BUTTON = '❌Без кнопки'

MSG_ORDER_CLEARED_BY_HEADER = 'Приказ выполнили:\n'

MSG_ORDER_SENT = 'Ваше сообщение отправлено'

MSG_ORDER_CLEARED = 'Я тебя записал'
MSG_ORDER_CLEARED_ERROR = 'Хорош тыкать, уже всё'

MSG_ORDER_SEND_HEADER = 'Куда слать?'

MSG_ORDER_GROUP_CONFIG_HEADER = 'Настройки группы {}'
MSG_ORDER_GROUP_NEW = 'Напиши мне название новой группы орденов'
MSG_ORDER_GROUP_LIST = 'Список групп'
MSG_ORDER_GROUP_ADD = '➕Добавить группу'
MSG_ORDER_GROUP_DEL = '🔥🚨Удалить группу🚨🔥'

MSG_NEWBIE = """Новый игрок в замке!\n
Все на вербовку %username%!"""

MSG_FLAG_CHOOSE_HEADER = 'Выбери флаг из списка или отправь мне любой другой приказ'

MSG_PROFILE_OLD = 'Твой профиль перестал сиять, освети его лунный луной...'
MSG_PROFILE_SAVED = """Твой профиль вновь сияет лунным светом, {}!
Не забывай освещать свой профиль хотя бы раз в день. 🌑"""
MSG_PROFILE_CASTLE_MISTAKE = """\
Перед тобой во всей красе предстала луна.
Ты бесстрашно вошёл в её свет в надежде добраться до таинственных новых земель.
Однако долгие часы скитаний не привели тебя ни к чему.
Повезло хоть, что выбраться смог! Без проводника здесь делать нечего..."""
MSG_PROFILE_SHOW_FORMAT = """\
👤 %first_name% %last_name% (%username%)
%castle% %name%
🏅 %prof% %level% уровня
⚜️ Орден %squad%
⚔️ %attack% | 🛡 %defence% | 🔥 %exp%/%needExp%
💰 %gold% | 🔋 %maxStamina%
%pet%
🕑 Последнее обновление %date%"""

# main.py texts
MSG_MAIN_INLINE_BATTLE = 'ГРАБЬНАСИЛУЙУБИВАЙ!'
MSG_MAIN_READY_TO_BATTLE = 'К битве готовсь!'
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
MSG_SQUAD_GREEN_INLINE_BUTTON = '✅Зелёное Да'
MSG_SQUAD_RED_INLINE_BUTTON = '❌Красное Да'
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
