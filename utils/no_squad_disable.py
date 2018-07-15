import os
import sys

from sqlalchemy import or_

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# noinspection PyPep8
from functions.user.util import disable_api_functions
from core.db import Session
from core.model import User, SquadMember

Session()

non_squad_members_with_settings = Session.query(User).filter(
    or_(
        User.setting_automated_sniping.is_(True),
        User.setting_automated_hiding.is_(True),
        User.setting_automated_report.is_(True),
        User.setting_automated_deal_report.is_(True),
    ),
    User.member.is_(None),
).all()
for user in non_squad_members_with_settings:
    print("Disable squad only functions for non-squad-member: user_id={}".format(user.id))
    disable_api_functions(user)

non_squad_members_with_settings = Session.query(User).filter(
    or_(
        User.setting_automated_sniping.is_(True),
        User.setting_automated_hiding.is_(True),
        User.setting_automated_report.is_(True),
        User.setting_automated_deal_report.is_(True),
    ),
    SquadMember.approved.is_(False),
).join(SquadMember).all()
for user in non_squad_members_with_settings:
    print("Disable squad only functions for unapproved squad member: user_id={}".format(user.id))
    disable_api_functions(user)
