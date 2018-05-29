# -*- coding: utf-8 -*-
from enum import Enum


CASTLE_LIST = ['🌑', '🐺', '🥔','🦅','🦌','🐉','🦈']

CASTLE_MAP = {
    '🌑': 'Moonlight',
    '🐺': 'Wolfpack',
    '🥔': 'Potato',
    '🦅': 'Highnest',
    '🦌': 'Deerhorn',
    '🐉': 'Dragonscale',
    '🦈': 'Sharkteeth',
}

CLASS_MAP = {
    '⚔️': 'Knight',
    '🏹': 'Ranger',
    '⚗️': 'Alchemist',
    '🛡': 'Sentinel',
    '⚒️': 'Blacksmith',
    '📦': 'Collector',
    '🐣': 'Esquire / Master'
}

# Only these items are going to reported in stock loss/gain
STOCK_WHITELIST = [
    'bone',
    'bone powder',
    'charcoal',
    'cloth',
    'coal',
    'cocoa powder',
    'coke',
    'egg',
    'flour',
    'hardener',
    'iron ore',
    'leather',
    'magic stone',
    'metal plate',
    'milk',
    'pelt',
    'powder',
    'purified powder',
    'rope',
    'ruby',
    'sapphire',
    'silver alloy',
    'silver mold',
    'silver ore',
    'solvent',
    'steel',
    'steel mold',
    'stick',
    'string',
    'sugar',
    'thread',
    'wooden shaft',
    'crafted leather',
    'metallic fiber',
]

# these /stock items take up TWO slots in inventory
HEAVY_ITEMS = [
    'hardener',
    'iron ore',
    'metal plate',
    'ruby',
    'silver alloy',
    'silver ore',
    'solvent',
    'steel mold',
    'steel',
    'sapphire',
    'crafted leather',
    'metallic fiber',
]

TACTICTS_COMMAND_PREFIX = "/tactics_"

class Castle(Enum):
    UNDEFINED = 0
    BLACK = '🌑'
    RED = '🐺'
    BLUE = '🥔'
    YELLOW = '🦅'
    WHITE = '🦌'
    MINT = '🐉'
    DUSK = '🦈'
    LES = '\U0001f332Лесной форт'
    GORY = '\u26f0Горный форт'
    SEA = '\u2693\uFE0FМорской форт'


class Icons(Enum):
    BLACK = '🌑'
    RED = '🐺'
    BLUE = '🥔'
    YELLOW = '🦅'
    WHITE = '🦌'
    MINT = '🐉'
    DUSK = '🦈'
    LES = '\U0001f332'
    GORY = '\u26f0'
    SEA = '\u2693\uFE0F'
