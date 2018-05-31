# Creates entries for 'daytime' in UserQuests since this was not there in the beginning...
# NEW COLUMNN:
#   daytime = Column(BigInteger, nullable=False, default=0)

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.types import *
from core.state import get_game_state, GameState

session = Session()

a = session.query(UserQuest).filter(UserQuest.daytime==0).all()

for item in a:
    daytime = get_game_state(item.from_date)

    # Remove additional state...
    daytime &= ~GameState.HOWLING_WIND
    daytime &= ~GameState.NO_REPORTS
    daytime &= ~GameState.BATTLE_SILENCE

    print("... Migrating")

    item.daytime = int(daytime)

    session.add(item)
    session.commit()


