from vectors import Vector3
from object_manager import ObjBase, ElementID
from typing import Literal
from client_manager import Client
from team_manager import Team

T = Literal[True]


class Player(ObjBase):
    def __init__(
        self,
        __id: ElementID,
        nick: str,
        position: Vector3,
        rotation: Vector3,
        client: Client,
        team: Team,
        dimension: int | float = 0,
        interior: int | float = 1,
        alpha: float | int = 100,
        isfrozen: bool = False,
        skin: int = 0,
    ) -> None:
        super().__init__(position, rotation, dimension, interior, alpha, isfrozen)
        self._id = __id
        self._nick = nick
        self._client = client
        self._team = team
        self._skin = skin

    def getID(self) -> ElementID:
        return self._id

    def getNick(self) -> str:
        return self._nick

    def getSkin(self) -> int:
        return self._skin

    def getTeam(self) -> Team:
        return self._team
