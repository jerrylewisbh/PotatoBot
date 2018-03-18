# -*- coding: utf-8 -*-
from enum import Enum


CASTLE_LIST = ['🌑', '🐺', '🥔','🦅','🦌','🐉','🦈']

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
