import os
import sys
from datetime import datetime

from sqlalchemy import or_

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from functions.user import disable_api_functions
from core.types import Ban, Session, User, SquadMember

Session()

non_squad_members_with_settings = Session.query(User).filter(
    or_(
        User.setting_automated_sniping == True,
        User.setting_automated_hiding == True,
        User.setting_automated_report == True,
        User.setting_automated_deal_report == True
    ),
    User.member == None,
).all()
for user in non_squad_members_with_settings:
    print("Disable squad only functions for non-squad-member: user_id={}".format(user.id))
    disable_api_functions(user)


non_squad_members_with_settings = Session.query(User).filter(
    or_(
        User.setting_automated_sniping == True,
        User.setting_automated_hiding == True,
        User.setting_automated_report == True,
        User.setting_automated_deal_report == True
    ),
    SquadMember.approved == False,
).join(SquadMember).all()
for user in non_squad_members_with_settings:
    print("Disable squad only functions for unapproved squad member: user_id={}".format(user.id))
    disable_api_functions(user)
