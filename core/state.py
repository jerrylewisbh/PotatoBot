from datetime import time, datetime

from enum import IntEnum, Flag


class GameState(Flag):
    NO_WIND = 0

    MORNING = 1
    DAY = 2
    EVENING = 4
    NIGHT = 8

    HOWLING_WIND = 16

def get_game_state():
    """ Track the current state of the game so that we can simple query for state """
    now = datetime.now().time()

    # Cycle 1 (Note: first hour of cycle is 23:00-00:00 handled later on...)
    daytime = None
    if now >= time(0, 0) and now <= time(1, 0):
        daytime = GameState.MORNING
    elif now >= time(1, 0) and now <= time(3, 0):
        daytime = GameState.DAY
    elif now >= time(3, 0) and now <= time(5, 0):
        daytime = GameState.EVENING
    elif now >= time(5,0) and now <= time(7, 0):
        daytime = GameState.NIGHT
    elif now >= time(7, 0) and now <= time(9, 0):
        daytime = GameState.MORNING
    elif now >= time(9, 0) and now <= time(11, 0):
        daytime = GameState.DAY
    elif now >= time(11, 0) and now <= time(13, 0):
        daytime = GameState.EVENING
    elif now >= time(13, 0) and now <= time(15, 0):
        daytime = GameState.NIGHT
    elif now >= time(15, 0) and now <= time(17, 0):
        daytime = GameState.MORNING
    elif now >= time(17, 0) and now <= time(19, 0):
        daytime = GameState.DAY
    elif now >= time(19, 0) and now <= time(21, 0):
        daytime = GameState.EVENING
    elif now >= time(21, 0) and now <= time(23, 0):
        daytime = GameState.NIGHT
    elif now >= time(23, 0) and now <= time(0, 0):
        daytime = GameState.MORNING

    if now >= time(6, 57) and now <= time(7, 3) or now >= time(14, 57) and now <= time(15, 3) or now >= time(22, 57) and now <= time(23, 3):
        daytime = GameState.HOWLING_WIND

    return daytime
