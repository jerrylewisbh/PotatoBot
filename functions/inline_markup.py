from enum import IntFlag, auto

from core.types import (Session)

Session()

class QueryType(IntFlag):
    GroupList = auto()
    GroupInfo = auto()
    DelAdm = auto()
    Order = auto()
    OrderOk = auto()
    Orders = auto()
    OrderGroup = auto()
    OrderGroupManage = auto()
    OrderGroupTriggerChat = auto()
    OrderGroupAdd = auto()
    OrderGroupDelete = auto()
    OrderGroupList = auto()
    ShowStock = auto()
    ShowEquip = auto()
    ShowHero = auto()
    MemberList = auto()
    LeaveSquad = auto()
    RequestSquad = auto()
    RequestSquadAccept = auto()
    RequestSquadDecline = auto()
    InviteSquadAccept = auto()
    InviteSquadDecline = auto()
    TriggerOrderPin = auto()
    SquadList = auto()
    GroupDelete = auto()
    TriggerOrderButton = auto()
    OtherReport = auto()
    GlobalBuildTop = auto()
    WeekBuildTop = auto()
    SquadGlobalBuildTop = auto()
    SquadWeekBuildTop = auto()
    BattleGlobalTop = auto()
    BattleWeekTop = auto()
    Forward = auto()
    ShowSkills = auto()

    DisableAPIAccess = auto()
    DisableAutomatedReport = auto()
    EnableAutomatedReport = auto()

    DisableDealReport = auto()
    EnableDealReport = auto()

    QuestFeedbackRequired = auto()
    ForayFeedbackRequired = auto()

    DisableSniping = auto()
    EnableSniping = auto()

    DisableHideGold = auto()
    EnableHideGold = auto()

    Yes = auto()
    No = auto()

    TopAtk = auto()
    TopDef = auto()
    TopExp = auto()
    TopAtt = auto()

    TopAtkSquad = auto()
    TopDefSquad = auto()
    TopExpSquad = auto()
    TopAttSquad = auto()

    TopAtkClass = auto()
    TopDefClass = auto()
    TopExpClass = auto()
    TopAttClass = auto()





