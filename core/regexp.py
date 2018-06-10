# -*- coding: utf-8 -*-

# flags=re.UNICODE needed...
EMOJI = u"(\ud83d[\ude00-\ude4f])|(\ud83c[\udf00-\uffff])|(\ud83d[\u0000-\uddff])|(\ud83d[\ude80-\udeff])|(\ud83c[\udde0-\uddff])+"

# Fixme: Expertise is not extracted...
HERO = '(?P<castle>🌑|🐺|🥔|🦅|🦌|🐉|🦈)(?P<guild>(\[.+\])?)(?P<ribbon>(🎗?))(?P<name>.+) of (?:.+) .+\n' \
       '🏅Level: (?P<level>[0-9]+)\n' \
       '.+Atk: (?P<attack>[0-9]+) 🛡Def: (?P<defence>[0-9]+)\n' \
       '🔥Exp: (?P<exp>[0-9]+)/(?P<exp_needed>[0-9]+)\n' \
       '🔋Stamina: (?P<stamina>[0-9]+)/(?P<max_stamina>[0-9]+)\n' \
       '(?:💧Mana: (?P<mana>[0-9]+/[0-9]+\n))?'\
       '💰(?P<gold>-?[0-9]+)(?: 👝(?P<pouches>[0-9]+))?(?: 💎(?P<diamonds>[0-9]+))?\n' \
       '(?:🤺PVP: (?P<pvp>[0-9]+)\n)?' \
       '(?:📚Expertise: (?P<expertise>.+)\n)?' \
       '(?:🏛Class info: (?P<class>.+)\n)?' \
       '.+\n+' \
       '(?:.+\n)*'\
       '.+\n+' \
       '🎽Equipment(?:(?P<equipment>.+)(?:\n)?((?:.|\n)+)?)\n\n' \
       '🎒Bag: (?P<bag>[0-9]+)/(?P<max_bag>[0-9]+) /inv\n' \
       '📦Warehouse: (?P<stock>[0-9]+) /stock'
#(📚Expertise: (.*))?
REPORT = '(?P<castle>🌑|🐺|🥔|🦅|🦌|🐉|🦈)' \
         '(?P<guild>(\[.+\])?)' \
         '(?P<ribbon>(🎗?))' \
         '(?P<name>.+) ' \
         '⚔:(?P<attack>[0-9]+)(?:\(((\-|\+)[0-9]+)\))? ' \
         '🛡:(?P<defence>[0-9]+)(?:\(((\-|\+)[0-9]+)\))? ' \
         'Lvl: (?P<level>[0-9]+)\n' \
         'Your result on the battlefield:(?:\n' \
         '🔥Exp: (?P<exp>[0-9]+))?(?:\n' \
         '💰Gold: (?P<gold>-?[0-9]+))?(?:\n' \
         '📦Stock: (?P<stock>-?[0-9]+))?'


BUILD_REPORT = 'Ты вернулся со стройки: (.+), прогресс работ: ([0-9]+)%'

REPAIR_REPORT = 'Здание отремонтировано: (.+)'

STOCK = '📦storage'

PROFESSION = '(.*) skills levels:'

ACCESS_CODE = "(Code )([0-9a-zA-Z]+)( to authorize).*"

TRADE_BOT = '📦твой склад с материалами:'



