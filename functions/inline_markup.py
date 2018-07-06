from enum import IntFlag, auto

from core.types import (Session)

Session()


class QueryType(IntFlag):
    Order = auto()
    OrderOk = auto()
    Orders = auto()
    TriggerOrderPin = auto()
    TriggerOrderButton = auto()
    OtherReport = auto()
    GlobalBuildTop = auto()
    Forward = auto()
    ShowSkills = auto()

