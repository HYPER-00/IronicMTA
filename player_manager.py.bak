from vectors import Vector3
from objects import ObjBase, Object
from typing import Literal

T = Literal[True]

class Player(ObjBase):
    def __init__(
        self, 
        ip: str,
        position: Vector3, 
        rotation: Vector3, 
        ping: int,
        nick: str,
        serial: str,
        name: str = "",
        level: int = 0,
        money: int = 0,
        team: str = None,
        muted: bool = False,
        version: str = "1.5",
        isdead: bool = False,
        isfrozen: bool = False,
        nametag: bool = True,
        nametag_text: str = "",
        alpha: float | int = 100, 
        interior: int | float = 1, 
        dimension: int | float = 0, 
        voice_enabled: bool = True,
        nametag_color: str = "#FFFFF",

    ) -> None:
        super(Player, self).__init__(position, rotation, dimension, interior, alpha, isfrozen)
        self._position               = position
        self._rotation               = rotation
        self._name                   = name
        self._nick                   = nick
        self._ip                     = ip
        self._serial                 = serial
        self._team                   = team
        self._ping                   = ping 
        self._level                  = level
        self._money                  = money
        self._muted                  = muted
        self._version                = version
        self._isdead                 = isdead
        self._isfrozen               = isfrozen
        self._nametag                = nametag
        self._nametag_text           = nametag_text
        self._alpha                  = alpha
        self._interior               = interior
        self._dimension              = dimension
        self._voice_enabled          = voice_enabled
        self._nametag_color          = nametag_color

    def getPlayerNick(self) -> str:
        return self._nick

    def setPlayerName(self, name: str) -> T:
        self._name = name
        assert self._name == name
        return True

    def setPlayerNick(self, nick: str) -> T:
        self._nick = nick
        assert self._name == nick
        return True
    
    def setPlayerSerial(self, serial: str) -> T:
        self._sder = serial
        assert self._serial == serial
        return True
    
    def setPlayerNametag(self, nametag: str) -> T:
        self._nametag = nametag
        assert self._nametag == nametag
        return True
    
    def setPlayerNametagColor(self, nametag_color: str) -> T:
        self._name_tag_color = nametag_color
        assert self._nametag_color == nametag_color
        return True
    
    def setPlayerDead(self, isdead: bool) -> T:
        self._isdead = isdead
        assert self._isdead == isdead
        return True

    def setModel(self, model_id: int) -> int | bool:                                                   ...
    def setCameraMatrix(self, camera_position: Vector3, camera_rotation: Vector3) -> Vector3 | bool:   ...
    def setCameraTarget(self, target: Object) -> bool:                                                 ...
    def setPosition(self, position: Vector3) -> Vector3:                                               ...