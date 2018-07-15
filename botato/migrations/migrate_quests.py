# Creates entries for 'daytime' in UserQuests since this was not there in the beginning...
# NEW COLUMNN:
#   daytime = Column(BigInteger, nullable=False, default=0)

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.db import Session
from core.model import UserQuest
from core.state import GameState, get_game_state

session = Session()

a = session.query(UserQuest).filter().all()

for item in a:
    daytime = get_game_state(item.forward_date)

    # Remove additional state...
    daytime &= ~GameState.HOWLING_WIND
    daytime &= ~GameState.NO_REPORTS
    daytime &= ~GameState.BATTLE_SILENCE

    item.daytime = int(daytime)

    print("Migrating {} -> {}".format(item.id, daytime.name))

    session.add(item)
    session.commit()
