from datetime import datetime, timedelta
from enum import IntFlag, auto

""" Helper for getting current game state(s)... """

"""
Notes:

Times are based on UTC!

+------------+----------------+----------------+----------------+
|   State    |    Cycle 1     |    Cycle 2     |    Cycle 3     |
+------------+----------------+----------------+----------------+
| Morning:   | 23:00 to 01:00 | 07:00 to 09:00 | 15:00 to 17:00 |
| Day:       | 01:00 to 03:00 | 09:00 to 11:00 | 17:00 to 19:00 |
| Dawn:      | 03:00 to 05:00 | 11:00 to 13:00 | 19:00 to 21:00 |
| Night:     | 05:00 to 07:00 | 13:00 to 15:00 | 21:00 TO 23:00 |
| Howling:   | 07:00 to 07:03 | 15:00 to 15:03 | 23:00 TO 23:03 |
| Silence:   | 06:57 to 07:00 | 14:57 to 15:00 | 22:57 TO 23:00 |
| NoReports: | 06:57 to 07:03 | 14:57 to 15:03 | 22:57 TO 23:03 |
+------------+----------------+----------------+----------------+

"""


class GameState(IntFlag):
    NO_STATE = auto()

    MORNING = auto()
    DAY = auto()
    EVENING = auto()
    NIGHT = auto()

    HOWLING_WIND = auto()
    BATTLE_SILENCE = auto()
    NO_REPORTS = auto()


def get_game_state(custom_time=None):
    """ Return calculated GameState for the given time_value. """

    if not custom_time:
        now = datetime.now().time()
    else:
        now = custom_time

    mod = (now.hour + 1) % 8
    states = []
    if mod in [0, 1]:
        states.append(GameState.MORNING)
    elif mod in [2, 3]:
        states.append(GameState.DAY)
    elif mod in [4, 5]:
        states.append(GameState.EVENING)
    elif mod in [6, 7]:
        states.append(GameState.NIGHT)

    # Additional states for action phases...

    # Howling
    if mod == 0 and now.minute <= 3:
        states.append(GameState.HOWLING_WIND)

    # Silence
    if (mod == 7 and now.minute >= 57) or (mod == 0 and now.minute == 0 and now.second == 0):
        states.append(GameState.BATTLE_SILENCE)

    # No Report phase...
    if (mod == 7 and now.minute >= 57) or (mod == 0 and now.minute < 3):
        states.append(GameState.NO_REPORTS)

    state = 0
    for state_item in states:
        state |= state_item

    return state


def get_last_battle(date=None) -> datetime:
    # Get last battletime
    now = date
    if not date:
        now = datetime.now()
    if (now.hour < 7):
        now = now - timedelta(days=1)

    return now.replace(
        hour=(int((now.hour + 1) / 8) * 8 - 1 + 24) % 24,
        minute=0,
        second=0,
        microsecond=0
    )
