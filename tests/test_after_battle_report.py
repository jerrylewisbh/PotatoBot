import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

print(sys.path)

from core.functions.common import stock_compare_text, stock_split, get_weighted_diff, MSG_CHANGES_SINCE_LAST_UPDATE, \
    MSG_USER_BATTLE_REPORT_STOCK, TRIBUTE_NOTE
from core.functions.profile import get_stock_before_after_war, get_latest_report, format_report
from core.state import get_last_battle
from core.types import *

from core.functions.quest import *

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Logging for console
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)

api_users = Session.query(User).join(SquadMember).join(Squad).join(Character).filter(
    User.api_token is not None,
    SquadMember.approved == True,
).all()

for user in api_users:
    logging.info("report_after_battle for user_id='%s'", user.id)

    if user.is_api_profile_allowed and user.is_api_stock_allowed and \
            user.setting_automated_report and user.api_token:

        logging.info("Processing report_after_battle for user_id='%s'", user.id)

        # Get the oldest stock-report from after war for this comparison...
        before_war_stock, after_war_stock = get_stock_before_after_war(user)
        logging.debug("after_war_stock: %s", after_war_stock)
        logging.debug("Second before_war_stock stock: %s", before_war_stock)

        # Get previous character and calculate difference in exp + gold
        prev_character = Session.query(Character).filter(
            Character.user_id == user.id,
            Character.date < get_last_battle(),
        ).order_by(Character.date.desc()).first()

        if not prev_character:
            logging.warning("Couldn't find previous Character! This should only happen for a user with only ONE character.")
            continue
        logging.debug("Previous character: %s", prev_character)

        earned_exp = user.character.exp - prev_character.exp
        earned_gold = user.character.gold - prev_character.gold

        logging.debug("Current: %s", user.character)
        logging.debug("Previous: %s", prev_character)

        logging.debug("Diffs for '%s': exp=%s, gold=%s", user.id, earned_exp, earned_gold)

        stock_diff = "<i>Missing before/after war data to generate comparison. Sorry.</i>"
        gained_sum = 0
        lost_sum = 0
        diff_stock = 0
        if before_war_stock and after_war_stock:
            resources_new, resources_old = stock_split(before_war_stock.stock, after_war_stock.stock)
            resource_diff_add, resource_diff_del = get_weighted_diff(resources_old, resources_new)
            stock_diff = stock_compare_text(before_war_stock.stock, after_war_stock.stock)

            gained_sum = sum([x[1] for x in resource_diff_add])
            lost_sum = sum([x[1] for x in resource_diff_del])
            diff_stock = gained_sum + lost_sum

        # Only create a preliminary report if user hasn't already sent in a complete one.
        existing_report = get_latest_report(user.id)
        if not existing_report:
            logging.debug("Report does not exist yet. Creating preliminary Report.")
            logging.debug("Current: %s", user.character.name)
            r = Report()

            logging.info(user)
            r.user_id = user.id

            logging.info(user.character.name)
            r.name = user.character.name

            logging.info(datetime.utcnow())
            r.date = datetime.utcnow()

            r.level = user.character.level
            r.attack = user.character.attack
            r.defence = user.character.defence
            r.castle = user.character.castle
            r.earned_exp = earned_exp
            r.earned_gold = earned_gold
            r.earned_stock = diff_stock
            r.preliminary_report = True
            Session.add(r)
            Session.commit()

            text = format_report(r)
        else:
            text = format_report(existing_report)

        stock_text = MSG_USER_BATTLE_REPORT_STOCK.format(
            MSG_CHANGES_SINCE_LAST_UPDATE,
            stock_diff,
            before_war_stock.date.strftime("%Y-%m-%d %H:%M:%S") if before_war_stock else "Missing",
            after_war_stock.date.strftime("%Y-%m-%d %H:%M:%S") if after_war_stock else "Missing",
        )
        text += stock_text
        if user.character and user.character.characterClass == "Knight":
            text += TRIBUTE_NOTE

        print(

            user.id,
            text,
            ParseMode.HTML,
            None
        )
    logging.info("END report_after_battle for user_id='%s'", user.id)

