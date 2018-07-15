# -*- coding: utf-8 -*-
from enum import IntEnum

CASTLE_LIST = ['🌑', '🐺', '🦅', '🦌', '🐉', '🦈', '🥔']

CASTLE_MAP = {
    '🌑': 'Moonlight',
    '🐺': 'Wolfpack',
    '🥔': 'Potato',
    '🦅': 'Highnest',
    '🦌': 'Deerhorn',
    '🐉': 'Dragonscale',
    '🦈': 'Sharkteeth',
    '⚱': 'Urn',
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

TACTICTS_COMMAND_PREFIX = "/tactics_"


class AdminType(IntEnum):
    SUPER = 0
    FULL = 1
    GROUP = 2

    WARLORD = 10
    SQUAD_CONTROLLER = 11

    NOT_ADMIN = 100


class MessageType(IntEnum):
    TEXT = 0
    VOICE = 1
    DOCUMENT = 2
    STICKER = 3
    CONTACT = 4
    VIDEO = 5
    VIDEO_NOTE = 6
    LOCATION = 7
    AUDIO = 8
    PHOTO = 9
