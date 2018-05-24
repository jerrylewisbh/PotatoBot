# -*- coding: utf-8 -*-
from core.texts import MSG_NO_SQUAD, MSG_WANTS_TO_JOIN, MSG_NO_PET, MSG_NO_PROFESSION
from core.types import User, Character, Profession


def fill_template(msg: str, user: User):
    if user.username:
        msg = msg.replace('%username%', '@' + user.username)
    else:
        msg = msg.replace('%username%', (user.first_name or '') + ' ' + (user.last_name or ''))
    msg = msg.replace('%first_name%', user.first_name or '')
    msg = msg.replace('%last_name%', user.last_name or '')
    msg = msg.replace('%id%', str(user.id))
    if user.character:
        msg = msg.replace('%ign%', str(user.character.name or ''))
    else:
        msg = msg.replace('%ign%', (user.first_name or '') + ' ' + (user.last_name or ''))
    return msg


def fill_char_template(msg: str, user: User, char: Character, profession: Profession,squad_request=False):
    msg = fill_template(msg, user)
    msg = msg.replace('%date%', str(char.date))
    msg = msg.replace('%name%', str(char.name))
    msg = msg.replace('%prof%', str(char.prof))
    msg = msg.replace('%petLevel%', str(char.petLevel))
    #msg = msg.replace('%maxStamina%', str(char.maxStamina))
    msg = msg.replace('%level%', str(char.level))
    msg = msg.replace('%attack%', str(char.attack))
    msg = msg.replace('%defence%', str(char.defence))
    msg = msg.replace('%exp%', str(char.exp))
    msg = msg.replace('%needExp%', str(char.needExp))
    msg = msg.replace('%castle%', str(char.castle))
    msg = msg.replace('%gold%', str(char.gold))
    msg = msg.replace('%pouches%', str(char.donateGold))
    if user.member is not None and user.member.approved:
        msg = msg.replace('%squad%', user.member.squad.squad_name)
    else:
        msg = msg.replace('%squad%', MSG_NO_SQUAD)
    if char.pet is not None:
        msg = msg.replace('%pet%', '{} {} lvl'.format(str(char.pet),
                                                      str(char.petLevel)))
    else:
        msg = msg.replace('%pet%', MSG_NO_PET)

    if squad_request:
        msg += MSG_WANTS_TO_JOIN.format(user.member.squad.squad_name)

    if char.characterClass:
        msg = msg.replace('%profession%', char.characterClass)
    elif profession is not None:
        msg = msg.replace('%profession%', profession.name)
    else:
        msg = msg.replace('%profession%', MSG_NO_PROFESSION)

    return msg
