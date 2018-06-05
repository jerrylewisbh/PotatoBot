# -*- coding: utf-8 -*-
import logging
from datetime import datetime
from enum import Enum

from sqlalchemy import (BigInteger, Boolean, Column, DateTime, ForeignKey,
                        Integer, Text, UnicodeText, UniqueConstraint,
                        create_engine)
from sqlalchemy.dialects.mysql import DATETIME
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, scoped_session, sessionmaker

from config import DB


class AdminType(Enum):
    SUPER = 0
    FULL = 1
    GROUP = 2

    WARLORD = 10
    SQUAD_CONTROLLER = 11

    NOT_ADMIN = 100


class MessageType(Enum):
    TEXT = 0
    VOICE = 1
    DOCUMENT = 2
    STICKER = 3
    CONTACT = 4
    VIDEO = 5
    VIDEO_NOTE = 6
    LOCATION = 7
    AUDIO = 8
    PHOTO = 9



ENGINE = create_engine(DB,
                       echo=False,
                       pool_size=200,
                       max_overflow=50,
                       isolation_level="READ UNCOMMITTED")

# FIX: имена констант?
LOGGER = logging.getLogger('sqlalchemy.engine')
Base = declarative_base()
Session = scoped_session(sessionmaker(bind=ENGINE))
Session()


class UserQuestItem(Base):
    __tablename__ = 'user_quest_item'

    user_quest_id = Column(BigInteger, ForeignKey('user_quest.id'), primary_key=True)
    item_id = Column(BigInteger, ForeignKey('item.id'), primary_key=True)
    count = Column(Integer)


class Group(Base):
    __tablename__ = 'groups'

    id = Column(BigInteger, primary_key=True)  # FIX: invalid name
    username = Column(UnicodeText(250))
    title = Column(UnicodeText(250))
    welcome_enabled = Column(Boolean, default=False)
    allow_trigger_all = Column(Boolean, default=False)
    allow_pin_all = Column(Boolean, default=False)
    bot_in_group = Column(Boolean, default=True)

    group_items = relationship('OrderGroupItem', back_populates='chat')
    squad = relationship('Squad', back_populates='chat')
    orders = relationship('Order', back_populates='chat')


class User(Base):
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True)
    username = Column(UnicodeText(250))
    first_name = Column(UnicodeText(250))
    last_name = Column(UnicodeText(250))
    date_added = Column(DateTime, default=datetime.now())

    # We save the history of all Builds, Characters, etc. Below are also convenience functions to allow getting
    # the latest one...
    characters = relationship('Character', back_populates='user', order_by='Character.date.desc()', lazy='dynamic')
    equipments = relationship('Equip', back_populates='user', order_by='Equip.date.desc()', lazy='dynamic')
    stocks = relationship('Stock', back_populates='user', order_by='Stock.date.desc()', lazy='dynamic')

    orders_confirmed = relationship('OrderCleared', back_populates='user')

    member = relationship('SquadMember', back_populates='user', uselist=False)

    report = relationship('Report', back_populates='user', order_by='Report.date.desc()')

    build_report = relationship('BuildReport', back_populates='user', order_by='BuildReport.date.desc()')

    profession = relationship('Profession', back_populates='user', order_by='Profession.date.desc()', uselist=False)

    quests = relationship('UserQuest', back_populates='user')

    hide_settings = relationship('UserStockHideSetting', back_populates='user', lazy='dynamic')
    sniping_settings = relationship('UserExchangeOrder', back_populates='user', lazy='dynamic')

    # API Token and temporary stuff we need after we get an async answer...
    api_token = Column(UnicodeText(250))
    api_user_id = Column(UnicodeText(250))
    api_request_id = Column(UnicodeText(250))
    api_grant_operation = Column(UnicodeText(250))

    is_api_profile_allowed = Column(Boolean())
    is_api_stock_allowed = Column(Boolean())
    is_api_trade_allowed = Column(Boolean())

    sniping_suspended = Column(Boolean(), default=False)

    setting_automated_report = Column(Boolean(), default=True)
    setting_automated_deal_report = Column(Boolean(), default=True)
    setting_automated_hiding = Column(Boolean(), default=False)
    setting_automated_sniping = Column(Boolean(), default=False)

    # Relationship
    admin_permission = relationship("Admin")

    ban = relationship("Ban", back_populates='user', order_by="Ban.to_date.desc()", lazy='dynamic')

    @hybrid_property
    def equip(self):
        return self.equipments.first()

    @hybrid_property
    def stock(self):
        return self.stocks.first()

    @hybrid_property
    def character(self):
        return self.characters.first()

    @hybrid_property
    def is_banned(self):
        # Get longest running ban still valid...
        ban = self.ban.first()
        if ban is not None and datetime.now() < ban.to_date:
            return True
        return False

    @hybrid_property
    def is_squadmember(self):
        if self.member and self.member.approved:
            return True
        return False

    @hybrid_property
    def is_tester(self):
        # Check if user is a tester based on testing-squad membership
        if not self.is_squadmember:
            return False

        if self.member and self.member.approved and self.member.squad and self.member.squad.testing_squad:
            return True
        return False

    def __repr__(self):
        user = ''
        if self.first_name:
            user += self.first_name + ' '
        if self.last_name:
            user += self.last_name + ' '
        if self.username:
            user += '(@' + self.username + ')'
        return user

    def __str__(self):
        user = ''
        if self.first_name:
            user += self.first_name + ' '
        if self.last_name:
            user += self.last_name
        return user


class Quest(Base):
    __tablename__ = 'quest'

    id = Column(BigInteger, autoincrement=True, primary_key=True)

    text = Column(UnicodeText(), nullable=False)
    approved = Column(Boolean(), default=False)

    user_quests = relationship('UserQuest', back_populates='quest')


class UserQuest(Base):
    __tablename__ = 'user_quest'

    id = Column(BigInteger, autoincrement=True, primary_key=True)
    user_id = Column(BigInteger, ForeignKey(User.id))

    from_date = Column(DATETIME(fsp=6), default=datetime.utcnow)
    # When was the msg originally received? servces as uniqueness-factor together with user_id
    forward_date = Column(DATETIME(fsp=6), nullable=False)

    exp = Column(BigInteger, default=0)
    level = Column(BigInteger)

    quest_id = Column(BigInteger, ForeignKey("quest.id"))
    quest = relationship('Quest', back_populates='user_quests')

    location_id = Column(BigInteger, ForeignKey("location.id"), nullable=True)
    location = relationship('Location', back_populates='user_locations')

    user = relationship('User', back_populates='quests')

    items = relationship(UserQuestItem)

    __table_args__ = (
        UniqueConstraint('user_id', 'forward_date', name='uc_usr_fwd_date'),
    )


class Location(Base):
    __tablename__ = 'location'

    id = Column(BigInteger, autoincrement=True, primary_key=True)
    name = Column(UnicodeText(250))

    user_locations = relationship('UserQuest', back_populates='location')


class WelcomeMsg(Base):
    __tablename__ = 'welcomes'

    chat_id = Column(BigInteger, primary_key=True)
    message = Column(UnicodeText(2500))


class Wellcomed(Base):
    __tablename__ = 'wellcomed'

    user_id = Column(BigInteger, ForeignKey(User.id), primary_key=True)
    chat_id = Column(BigInteger, ForeignKey(WelcomeMsg.chat_id), primary_key=True)


class Trigger(Base):
    __tablename__ = 'triggers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    trigger = Column(UnicodeText(2500))
    message = Column(UnicodeText(2500))
    message_type = Column(Integer, default=0)


class Admin(Base):
    __tablename__ = 'admins'

    user_id = Column(BigInteger, ForeignKey(User.id), primary_key=True)
    admin_type = Column(Integer)
    admin_group = Column(BigInteger, primary_key=True, default=0)


class OrderGroup(Base):
    __tablename__ = 'order_groups'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(UnicodeText(250))

    items = relationship('OrderGroupItem', back_populates='group', cascade="save-update, merge, delete, delete-orphan")


class OrderGroupItem(Base):
    __tablename__ = 'order_group_items'

    group_id = Column(Integer, ForeignKey(OrderGroup.id, ondelete='CASCADE'), primary_key=True)
    chat_id = Column(BigInteger, ForeignKey(Group.id), primary_key=True)

    group = relationship('OrderGroup', back_populates='items')
    chat = relationship('Group', back_populates='group_items')


class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, ForeignKey(Group.id))
    text = Column(UnicodeText(2500))
    confirmed_msg = Column(BigInteger)
    date = Column(DATETIME(fsp=6), default=datetime.now())

    cleared = relationship('OrderCleared', back_populates='order')
    chat = relationship('Group', back_populates='orders')


class OrderCleared(Base):
    __tablename__ = 'order_cleared'

    order_id = Column(Integer, ForeignKey(Order.id), primary_key=True)
    user_id = Column(BigInteger, ForeignKey(User.id), primary_key=True)
    date = Column(DATETIME(fsp=6), default=datetime.now())

    order = relationship('Order', back_populates='cleared')
    user = relationship('User', back_populates='orders_confirmed')


class Stock(Base):
    __tablename__ = 'stock'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey(User.id))
    stock = Column(UnicodeText(2500))
    date = Column(DATETIME(fsp=6), default=datetime.now())
    stock_type = Column(Integer)

    user = relationship('User', back_populates='stocks')


class Profession(Base):
    __tablename__ = 'profession'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey(User.id))
    skillList = Column(UnicodeText(2500))
    name = Column(UnicodeText(250))
    date = Column(DATETIME(fsp=6), default=datetime.now())

    user = relationship('User', back_populates='profession')


class Character(Base):
    __tablename__ = 'characters'

    user_id = Column(BigInteger, ForeignKey(User.id), primary_key=True)
    date = Column(DATETIME(fsp=6), primary_key=True)
    name = Column(UnicodeText(250))
    prof = Column(UnicodeText(250))
    pet = Column(UnicodeText(250), nullable=True, default=None)
    petLevel = Column(Integer, default=0)
    maxStamina = Column(Integer, default=5)
    level = Column(Integer)
    attack = Column(Integer)
    defence = Column(Integer)
    exp = Column(Integer)
    needExp = Column(Integer, default=0)
    castle = Column(UnicodeText(100))
    gold = Column(Integer, default=0)
    donateGold = Column(Integer, default=0)

    # Note: Technically this is also tracked in a characters profession-information. But this represents the
    # current state. Also this way we can display class info without having a users /class information which is not
    # (yet) available in the API
    characterClass = Column(UnicodeText(250))

    user = relationship('User', back_populates='characters')


class BuildReport(Base):
    __tablename__ = 'build_reports'

    user_id = Column(BigInteger, ForeignKey(User.id), primary_key=True)
    date = Column(DATETIME(fsp=6), primary_key=True)
    building = Column(UnicodeText(250))
    progress_percent = Column(Integer)
    report_type = Column(Integer)

    user = relationship('User', back_populates='build_report')


class Report(Base):
    __tablename__ = 'reports'

    user_id = Column(BigInteger, ForeignKey(User.id), primary_key=True)
    date = Column(DATETIME(fsp=6), primary_key=True)
    name = Column(UnicodeText(250))
    level = Column(Integer)
    attack = Column(Integer)
    defence = Column(Integer)
    castle = Column(UnicodeText(100))
    earned_exp = Column(Integer)
    earned_gold = Column(Integer)
    earned_stock = Column(Integer)

    preliminary_report = Column(Boolean(), default=False)

    user = relationship('User', back_populates='report')


class Squad(Base):
    __tablename__ = 'squads'

    chat_id = Column(BigInteger, ForeignKey(Group.id), primary_key=True)
    invite_link = Column(UnicodeText(250), default='')
    squad_name = Column(UnicodeText(250))
    thorns_enabled = Column(Boolean, default=True)
    silence_enabled = Column(Boolean, default=True)
    reminders_enabled = Column(Boolean, default=True)
    hiring = Column(Boolean, default=False)
    testing_squad = Column(Boolean, default=False)

    members = relationship('SquadMember', back_populates='squad')
    chat = relationship('Group', back_populates='squad')


class SquadMember(Base):
    __tablename__ = 'squad_members'

    squad_id = Column(BigInteger, ForeignKey(Squad.chat_id))
    user_id = Column(BigInteger, ForeignKey(User.id), primary_key=True)

    approved = Column(Boolean, default=False, nullable=False)

    squad = relationship('Squad', back_populates='members')
    user = relationship('User', back_populates='member')


class Equip(Base):
    __tablename__ = 'equip'

    user_id = Column(BigInteger, ForeignKey(User.id), primary_key=True)
    date = Column(DATETIME(fsp=6), primary_key=True)

    equip = Column(UnicodeText(250))

    user = relationship('User', back_populates='equipments')


class LocalTrigger(Base):
    __tablename__ = 'local_triggers'

    id = Column(BigInteger, autoincrement=True, primary_key=True)
    chat_id = Column(BigInteger, ForeignKey(Group.id))
    trigger = Column(UnicodeText(2500))
    message = Column(UnicodeText(2500))
    message_type = Column(Integer, default=0)


class Ban(Base):
    __tablename__ = 'banned_users'

    user_id = Column(BigInteger, ForeignKey(User.id), primary_key=True)
    reason = Column(UnicodeText(2500))
    from_date = Column(DATETIME(fsp=6))
    to_date = Column(DATETIME(fsp=6))

    user = relationship(User, back_populates="ban", uselist=False)


class Log(Base):
    __tablename__ = 'log'

    id = Column(BigInteger, autoincrement=True, primary_key=True)
    user_id = Column(BigInteger, ForeignKey(User.id))
    chat_id = Column(BigInteger)
    date = Column(DATETIME(fsp=6))
    func_name = Column(UnicodeText(2500))
    args = Column(UnicodeText(2500))


class Auth(Base):
    __tablename__ = 'auth'

    id = Column(Text(length=32))
    user_id = Column(BigInteger, ForeignKey(User.id), primary_key=True)


class Item(Base):
    __tablename__ = 'item'

    id = Column(BigInteger, autoincrement=True, primary_key=True)
    cw_id = Column(UnicodeText(25), unique=True)

    tradable = Column(Boolean(), default=False, nullable=False)
    pillagable = Column(Boolean(), default=False, nullable=False)
    weight = Column(BigInteger, default=1, nullable=False)

    name = Column(UnicodeText(250))

    user_quests = relationship(UserQuestItem)
    user_orders = relationship('UserExchangeOrder', back_populates='item', lazy='dynamic')

class UserExchangeOrder(Base):
    __tablename__ = 'user_exchange'

    id = Column(BigInteger, autoincrement=True, primary_key=True )

    user_id = Column(BigInteger, ForeignKey(User.id))
    user = relationship(User, back_populates="sniping_settings")

    item_id = Column(BigInteger, ForeignKey(Item.id))
    item = relationship(Item, back_populates='user_orders')

    outstanding_order = Column(Integer, nullable=False)
    initial_order = Column(Integer, nullable=False)


    max_price = Column(Integer, nullable=False)

class UserStockHideSetting(Base):
    __tablename__ = 'user_autohide'

    id = Column(BigInteger, autoincrement=True, primary_key=True)

    user_id = Column(BigInteger, ForeignKey(User.id))
    user = relationship(User, back_populates="hide_settings")

    item_id = Column(BigInteger, ForeignKey(Item.id))
    item = relationship(Item)

    priority = Column(Integer, nullable=False)
    max_price = Column(Integer, nullable=True)

    __table_args__ = (
        UniqueConstraint('user_id', 'priority', name='uc_usr_item'),
    )


def check_admin(update, adm_type, allowed_types=()):
    allowed = False
    if adm_type == AdminType.NOT_ADMIN:
        allowed = True
    else:
        admins = Session.query(Admin).filter_by(user_id=update.message.from_user.id).all()
        for adm in admins:
            if (AdminType(adm.admin_type) in allowed_types or adm.admin_type <= adm_type.value) and \
                    (adm.admin_group in [0, update.message.chat.id] or
                     update.message.chat.id == update.message.from_user.id):
                if adm.admin_group != 0:
                    group = Session.query(Group).filter_by(id=adm.admin_group).first()
                    if group and group.bot_in_group:
                        allowed = True
                        break
                else:
                    allowed = True
                    break
    return allowed


def check_ban(update):
    ban = Session.query(Ban).filter_by(user_id=update.message.from_user.id
                                       if update.message else update.callback_query.from_user.id).first()
    if ban is None or ban.to_date < datetime.now():
        return True
    else:
        return False


def log(user_id, chat_id, func_name, args):
    if user_id:
        log_item = Log()
        log_item.date = datetime.now()
        log_item.user_id = user_id
        log_item.chat_id = chat_id
        log_item.func_name = func_name
        log_item.args = args
        Session.add(log_item)
        Session.commit()
        #Session.remove()


Base.metadata.create_all(ENGINE)
