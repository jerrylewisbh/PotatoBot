import datetime
import os
import sys
import unittest

from core.state import GameState, get_game_state

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))



class TestTime(unittest.TestCase):
    def test_game_state_morning(self):
        """ Test if GameState returns Morning state... """

        sample_1 = get_game_state(datetime.time(hour=23, minute=3))     # Morning C1
        self.assertIn(GameState.MORNING, sample_1, "State should contain MORNING state")

        sample_2 = get_game_state(datetime.time(hour=7, minute=3))     # Morning C2
        self.assertIn(GameState.MORNING, sample_2, "State should contain MORNING state")

        sample_3 = get_game_state(datetime.time(hour=15, minute=3))    # Morning C3
        self.assertIn(GameState.MORNING, sample_3, "State should contain MORNING state")

    def test_game_state_day(self):
        """ Test if GameState returns Day state... """

        sample_1 = get_game_state(datetime.time(hour=1, minute=3))     # Day C1
        self.assertIn(GameState.DAY, sample_1, "State should contain DAY state")

        sample_2 = get_game_state(datetime.time(hour=9, minute=3))     # Day C2
        self.assertIn(GameState.DAY, sample_2, "State should contain DAY state")

        sample_3 = get_game_state(datetime.time(hour=17, minute=3))    # Day C3
        self.assertIn(GameState.DAY, sample_3, "State should contain DAY state")

    def test_game_state_evening(self):
        """ Test if GameState returns Evening state... """

        sample_1 = get_game_state(datetime.time(hour=3, minute=3))     # Evening C1
        self.assertIn(GameState.EVENING, sample_1, "State should contain EVENING state")

        sample_2 = get_game_state(datetime.time(hour=11, minute=3))     # Evening C2
        self.assertIn(GameState.EVENING, sample_2, "State should contain EVENING state")

        sample_3 = get_game_state(datetime.time(hour=19, minute=3))    # Evening C3
        self.assertIn(GameState.EVENING, sample_3, "State should contain EVENING state")

    def test_game_state_night(self):
        """ Test if GameState returns Night state... """

        sample_1 = get_game_state(datetime.time(hour=5, minute=3))     # Night C1
        self.assertIn(GameState.NIGHT, sample_1, "State should contain NIGHT state")

        sample_2 = get_game_state(datetime.time(hour=13, minute=3))     # Night C2
        self.assertIn(GameState.NIGHT, sample_2, "State should contain NIGHT state")

        sample_3 = get_game_state(datetime.time(hour=21, minute=3))    # Night C3
        self.assertIn(GameState.NIGHT, sample_3, "State should contain NIGHT state")

    def test_no_reports(self):
        """ Test if GameState returns Morning state... """

        sample_1 = get_game_state(datetime.time(hour=23, minute=2, microsecond=999))
        self.assertIn(GameState.NO_REPORTS, sample_1, "State should contain NO_REPORT state")

        sample_2 = get_game_state(datetime.time(hour=7, minute=2, microsecond=999))
        self.assertIn(GameState.NO_REPORTS, sample_2, "State should contain NO_REPORT state")

        sample_3 = get_game_state(datetime.time(hour=15, minute=2, microsecond=999))
        self.assertIn(GameState.NO_REPORTS, sample_3, "State should contain NO_REPORT state")

        sample_4 = get_game_state(datetime.time(hour=23, minute=5))
        self.assertNotIn(GameState.NO_REPORTS, sample_4, "State NOT should contain NO_REPORT state")

        sample_5 = get_game_state(datetime.time(hour=8, minute=5))
        self.assertNotIn(GameState.NO_REPORTS, sample_5, "State NOT should contain NO_REPORT state")

        sample_6 = get_game_state(datetime.time(hour=16, minute=5))
        self.assertNotIn(GameState.NO_REPORTS, sample_6, "State NOT should contain NO_REPORT state")

    def test_silence(self):
        """ Test if GameState returns Morning state... """

        sample_1 = get_game_state(datetime.time(hour=6, minute=57))
        self.assertIn(GameState.NO_REPORTS, sample_1, "State should contain SILENCE state")

        sample_2 = get_game_state(datetime.time(hour=14, minute=57))
        self.assertIn(GameState.NO_REPORTS, sample_2, "State should contain SILENCE state")

        sample_3 = get_game_state(datetime.time(hour=22, minute=57))
        self.assertIn(GameState.NO_REPORTS, sample_3, "State should contain SILENCE state")

        sample_4 = get_game_state(datetime.time(hour=7, minute=0))
        self.assertIn(GameState.NO_REPORTS, sample_3, "State should contain SILENCE state")

        sample_5 = get_game_state(datetime.time(hour=16, minute=0))
        self.assertIn(GameState.NO_REPORTS, sample_3, "State should contain SILENCE state")

        sample_6 = get_game_state(datetime.time(hour=23, minute=0))
        self.assertIn(GameState.NO_REPORTS, sample_3, "State should contain SILENCE state")

    def test_howling(self):
        """ Test if GameState returns Morning state... """

        sample_1 = get_game_state(datetime.time(hour=7, minute=0))
        self.assertIn(GameState.HOWLING_WIND, sample_1, "State should contain HOWLING_WIND state")

        sample_2 = get_game_state(datetime.time(hour=15, minute=0))
        self.assertIn(GameState.HOWLING_WIND, sample_2, "State should contain HOWLING_WIND state")

        sample_3 = get_game_state(datetime.time(hour=23, minute=0))
        self.assertIn(GameState.HOWLING_WIND, sample_3, "State should contain HOWLING_WIND state")

        sample_4 = get_game_state(datetime.time(hour=8, minute=3))
        self.assertIn(GameState.HOWLING_WIND, sample_1, "State should contain HOWLING_WIND state")

        sample_5 = get_game_state(datetime.time(hour=16, minute=3))
        self.assertIn(GameState.HOWLING_WIND, sample_2, "State should contain HOWLING_WIND state")

        sample_6 = get_game_state(datetime.time(hour=0, minute=3))
        self.assertIn(GameState.HOWLING_WIND, sample_3, "State should contain HOWLING_WIND state")

    def test_silence_whole_day(self):
        expected_silence = [
            # Cycle 1
            datetime.time(hour=6, minute=57, second=0, microsecond=0),
            datetime.time(hour=6, minute=58, second=0, microsecond=0),
            datetime.time(hour=6, minute=59, second=0, microsecond=0),
            datetime.time(hour=7, minute=00, second=0, microsecond=0),

            # Cycle 2
            datetime.time(hour=14, minute=57, second=0, microsecond=0),
            datetime.time(hour=14, minute=58, second=0, microsecond=0),
            datetime.time(hour=14, minute=59, second=0, microsecond=0),
            datetime.time(hour=15, minute=00, second=0, microsecond=0),

            # Cycle 3
            datetime.time(hour=22, minute=57, second=0, microsecond=0),
            datetime.time(hour=22, minute=58, second=0, microsecond=0),
            datetime.time(hour=22, minute=59, second=0, microsecond=0),
            datetime.time(hour=23, minute=00, second=0, microsecond=0),
        ]
        t = datetime.datetime(year=2018, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        for minute in range(0, 3601):
            t += datetime.timedelta(minutes=1)
            t_state = get_game_state(t.time())
            # print(t)
            #print(t.time() in expected_silence)
            if t.time() in expected_silence:
                self.assertIn(GameState.BATTLE_SILENCE, t_state, "Expected silence at {}!".format(t))
            else:
                self.assertNotIn(GameState.BATTLE_SILENCE, t_state, "NO silence expected at {}?!".format(t))


if __name__ == '__main__':
    # Force TZ!
    import os
    os.environ['TZ'] = 'UTC'

    unittest.main()
