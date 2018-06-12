import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.functions.profile.util import parse_hero_text, parse_report_text



class TestRegex(unittest.TestCase):
    def test_report_parsing(self):
        """ Test if Report can be parsed """

        test = """🥔[GO]Kroket van Potet ⚔:12 🛡:34 Lvl: 56
Your result on the battlefield:
🔥Exp: 123
💰Gold: 456"""

        parsed_data = parse_report_text(test)
        self.assertNotEquals(parsed_data, None)

        self.assertEqual(parsed_data['castle'], "🥔")
        self.assertEqual(parsed_data['name'], "[GO]Kroket van Potet")
        self.assertEqual(parsed_data['attack'], 12)
        self.assertEqual(parsed_data['defence'], 34)
        self.assertEqual(parsed_data['guild'], "[GO]")
        self.assertEqual(parsed_data['ribbon'], None)
        self.assertEqual(parsed_data['level'], 56)
        self.assertEqual(parsed_data['exp'], 123)
        self.assertEqual(parsed_data['gold'], 456)
        self.assertEqual(parsed_data['stock'], 0)

    def test_report_parsing_ribbon(self):
        """ Test if Report can be parsed """
        test = """🥔[GO]🎗Kroket van Potet ⚔:12 🛡:34 Lvl: 56
Your result on the battlefield:
🔥Exp: 123
💰Gold: 456"""

        parsed_data = parse_report_text(test)
        self.assertNotEquals(parsed_data, None)

        self.assertEqual(parsed_data['castle'], "🥔")
        self.assertEqual(parsed_data['name'], "[GO]Kroket van Potet")
        self.assertEqual(parsed_data['attack'], 12)
        self.assertEqual(parsed_data['guild'], "[GO]")
        self.assertEqual(parsed_data['ribbon'], "🎗")
        self.assertEqual(parsed_data['defence'], 34)
        self.assertEqual(parsed_data['level'], 56)
        self.assertEqual(parsed_data['exp'], 123)
        self.assertEqual(parsed_data['gold'], 456)
        self.assertEqual(parsed_data['stock'], 0)

    def test_report_parsing_ribbon_guildless(self):
        """ Test if Report can be parsed """
        test = """🥔🎗Kroket van Potet ⚔:12 🛡:34 Lvl: 56
Your result on the battlefield:
🔥Exp: 123
💰Gold: 456"""

        parsed_data = parse_report_text(test)
        self.assertNotEquals(parsed_data, None)

        self.assertEqual(parsed_data['castle'], "🥔")
        self.assertEqual(parsed_data['name'], "Kroket van Potet")
        self.assertEqual(parsed_data['attack'], 12)
        self.assertEqual(parsed_data['guild'], "")
        self.assertEqual(parsed_data['ribbon'], "🎗")
        self.assertEqual(parsed_data['defence'], 34)
        self.assertEqual(parsed_data['level'], 56)
        self.assertEqual(parsed_data['exp'], 123)
        self.assertEqual(parsed_data['gold'], 456)
        self.assertEqual(parsed_data['stock'], 0)

    def test_report_parsing_guildless(self):
        """ Test if Report can be parsed """
        test = """🥔Kroket van Potet ⚔:12 🛡:34 Lvl: 56
Your result on the battlefield:
🔥Exp: 123
💰Gold: 456"""

        parsed_data = parse_report_text(test)
        self.assertNotEquals(parsed_data, None)

        self.assertEqual(parsed_data['castle'], "🥔")
        self.assertEqual(parsed_data['name'], "Kroket van Potet")
        self.assertEqual(parsed_data['attack'], 12)
        self.assertEqual(parsed_data['guild'], "")
        self.assertEqual(parsed_data['ribbon'], None)
        self.assertEqual(parsed_data['defence'], 34)
        self.assertEqual(parsed_data['level'], 56)
        self.assertEqual(parsed_data['exp'], 123)
        self.assertEqual(parsed_data['gold'], 456)
        self.assertEqual(parsed_data['stock'], 0)

    def test_hero_parsing_ribbon(self):
        test = """🥔🎗Fozzie of Potato Castle
🏅Level: 23
⚔Atk: 73 🛡Def: 64
🔥Exp: 11451/13123
🔋Stamina: 1/6
💰27 👝2 💎12
📚Expertise: 📕
🏛Class info: /class



🎽Equipment +38⚔+46🛡:
Rapier +27⚔
Mithril dagger +7⚔
Mithril helmet +12🛡
Mithril gauntlets +8🛡
Mithril armor +3⚔ +17🛡
Mithril boots +8🛡
Royal Guard Cape +1⚔ +1🛡

🎒Bag: 13/15 /inv
📦Warehouse: 635 /stock"""

        parsed_data = parse_hero_text(test)
        self.assertNotEquals(parsed_data, None)

        self.assertEqual(parsed_data['castle'], "🥔")
        self.assertEqual(parsed_data['castle_name'], "Potato")
        self.assertEqual(parsed_data['name'], "Fozzie")
        self.assertEqual(parsed_data['attack'], 73)
        self.assertEqual(parsed_data['guild'], "")
        self.assertEqual(parsed_data['ribbon'], "🎗")
        self.assertEqual(parsed_data['defence'], 64)
        self.assertEqual(parsed_data['level'], 23)
        self.assertEqual(parsed_data['exp'], 11451)
        self.assertEqual(parsed_data['gold'], 27)
        self.assertEqual(parsed_data['stamina'], 1)
        self.assertEqual(parsed_data['max_stamina'], 6)
        self.assertEqual(parsed_data['pouches'], 2)
        self.assertEqual(parsed_data['exp_needed'], 13123)
        #self.assertEqual(parsed_data['expertise'], "📕")
        self.assertEqual(parsed_data['diamonds'], 12)
        self.assertIsNotNone(parsed_data['equipment'])

    def test_hero_parsing_missings(self):
        test = """🥔Fozzie of Potato Castle
🏅Level: 23
⚔Atk: 73 🛡Def: 64
🔥Exp: 11451/13123
🔋Stamina: 1/6
💰27
📚Expertise: 📕
🏛Class info: /class



🎽Equipment +38⚔+46🛡:
Rapier +27⚔
Mithril dagger +7⚔
Mithril helmet +12🛡
Mithril gauntlets +8🛡
Mithril armor +3⚔ +17🛡
Mithril boots +8🛡
Royal Guard Cape +1⚔ +1🛡

🎒Bag: 13/15 /inv
📦Warehouse: 635 /stock"""

        parsed_data = parse_hero_text(test)
        self.assertNotEquals(parsed_data, None)

        self.assertEqual(parsed_data['castle'], "🥔")
        self.assertEqual(parsed_data['castle_name'], "Potato")
        self.assertEqual(parsed_data['name'], "Fozzie")
        self.assertEqual(parsed_data['attack'], 73)
        self.assertEqual(parsed_data['guild'], "")
        self.assertEqual(parsed_data['ribbon'], None)
        self.assertEqual(parsed_data['defence'], 64)
        self.assertEqual(parsed_data['level'], 23)
        self.assertEqual(parsed_data['exp'], 11451)
        self.assertEqual(parsed_data['gold'], 27)
        self.assertEqual(parsed_data['stamina'], 1)
        self.assertEqual(parsed_data['max_stamina'], 6)
        self.assertEqual(parsed_data['pouches'], 0)
        self.assertEqual(parsed_data['exp_needed'], 13123)
        #self.assertEqual(parsed_data['expertise'], "📕")
        self.assertEqual(parsed_data['diamonds'], 0)
        self.assertIsNotNone(parsed_data['equipment'])

    def test_hero_parsing_full(self):
        test = """🥔Fozzie of Potato Castle
🏅Level: 23
⚔Atk: 73 🛡Def: 64
🔥Exp: 11451/13123
🔋Stamina: 1/6
💰27 👝2 💎12
📚Expertise: 📕
🏛Class info: /class



🎽Equipment +38⚔+46🛡:
Rapier +27⚔
Mithril dagger +7⚔
Mithril helmet +12🛡
Mithril gauntlets +8🛡
Mithril armor +3⚔ +17🛡
Mithril boots +8🛡
Royal Guard Cape +1⚔ +1🛡

🎒Bag: 13/15 /inv
📦Warehouse: 635 /stock"""

        parsed_data = parse_hero_text(test)
        self.assertNotEquals(parsed_data, None)

        self.assertEqual(parsed_data['castle'], "🥔")
        self.assertEqual(parsed_data['castle_name'], "Potato")
        self.assertEqual(parsed_data['name'], "Fozzie")
        self.assertEqual(parsed_data['attack'], 73)
        self.assertEqual(parsed_data['guild'], "")
        self.assertEqual(parsed_data['ribbon'], None)
        self.assertEqual(parsed_data['defence'], 64)
        self.assertEqual(parsed_data['level'], 23)
        self.assertEqual(parsed_data['exp'], 11451)
        self.assertEqual(parsed_data['gold'], 27)
        self.assertEqual(parsed_data['stamina'], 1)
        self.assertEqual(parsed_data['max_stamina'], 6)
        self.assertEqual(parsed_data['pouches'], 2)
        self.assertEqual(parsed_data['exp_needed'], 13123)
        #self.assertEqual(parsed_data['expertise'], "📕")
        self.assertEqual(parsed_data['diamonds'], 12)
        self.assertIsNotNone(parsed_data['equipment'])


if __name__ == '__main__':
    # Force TZ!
    import os
    os.environ['TZ'] = 'UTC'

    unittest.main()
