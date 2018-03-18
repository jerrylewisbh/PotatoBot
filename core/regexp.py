# -*- coding: utf-8 -*-
# FIX: переделать строки в """
PROFILE = '(🌑|🐺|🥔|🦅|🦌|🐉|🦈)(.+), (.+) .+ замка\n' \
          '🏅Уровень: ([0-9]+)\n' \
          '(?:.*)Атака: ([0-9]+) 🛡Защита: ([0-9]+)\n' \
          '🔥Опыт: ([0-9]+)/([0-9]+)\n' \
          '🔋Выносливость: ([0-9]+)/([0-9]+)\n' \
          '(?:💧Мана: [0-9]+/[0-9]+\n)?' \
          '💰(-?[0-9]+) 💠([0-9]+)\n\n' \
          '🎽Экипировка (.+)\n' \
          '🎒Рюкзак: ([0-9]+)/([0-9]+) /inv' \
          '(?:\n\nПомощник:\n(.+?) (?:.+?) (.+)? \(([0-9]+) ур\.\) (.+) /pet)?'

HERO = '(🌑|🐺|🥔|🦅|🦌|🐉|🦈)(.+) of (.+) .+\n' \
       '🏅Level: ([0-9]+)\n' \
       '.+Atk: ([0-9]+) 🛡Def: ([0-9]+)\n' \
       '🔥Exp: ([0-9]+)/([0-9]+)\n' \
       '🔋Stamina: ([0-9]+)/([0-9]+)\n' \
       '(?:💧Mana: [0-9]+/[0-9]+\n)?'\
       '💰Gold: (-?[0-9]+)(?: \(\+([0-9]+)\))?\n' \
       '(?:🤺PVP: ([0-9]+)\n)?' \
       '(?:📚Expertise: (.+)\n)?' \
       '(?:🏛Class info: (.+)\n)?' \
       '.+\n\n\n' \
       '🎽Equipment(?:(.+)(?:\n)?((?:.|\n)+)?)\n\n' \
       '🎒Bag: ([0-9]+)/([0-9]+) /inv\n' \
       '📦Warehouse: (?:[0-9]+) /stock(?:\n\n' \
       'Помощник:\n' \
       '(.+?) (?:.+?) (.+)? \(([0-9]+) ур\.\) (.+) /pet)?'

REPORT = '(🌑|🐺|🥔|🦅|🦌|🐉|🦈)(.+) ⚔:([0-9]+) 🛡:([0-9]+) \(Lvl: ([0-9]+)\)\n' \
       'Your result on the battlefield:(?:\n' \
       '🔥Exp: ([0-9]+))?(?:\n' \
       '💰Gold: (-?[0-9]+))?(?:\n' \
       '📦Stock: (-?[0-9]+))?'

BUILD_REPORT = 'Ты вернулся со стройки: (.+), прогресс работ: ([0-9]+)%'

REPAIR_REPORT = 'Здание отремонтировано: (.+)'

STOCK = '📦storage'

TRADE_BOT = '📦твой склад с материалами:'
