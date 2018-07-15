from enum import IntFlag, auto

class QuestType(IntFlag):
    NORMAL = auto()
    NORMAL_FAILED = auto()

    FORAY = auto()
    FORAY_FAILED = auto()
    FORAY_PLEDGE = auto()

    STOP = auto()
    STOP_FAIL = auto()

    ARENA = auto()
    ARENA_FAIL = auto()

    UNKNOWN = auto()
