"""
    IronicMTA object manager
"""

from .vectors import Vector3
from typing import Literal, Tuple

T = Literal[True]


class Dimension:
    def __init__(self, id: int) -> None:
        self._id = id

    @property
    def id(self) -> int:
        return self._id


class Interior:
    def __init__(self, id: int) -> None:
        self._id = id

    @property
    def id(self) -> int:
        return self._id

    @property
    def name(self) -> str:
        return ""


class ElementID(object):
    def __init__(self, value: int) -> None:
        self.value = value


class ObjBase(object):
    """
        Base objects for any object
    """

    def __init__(
        self,
        __id:              ElementID,
        position:          Vector3,
        rotation:          Vector3,
        dimension: int | float = 0,
        interior:  int | float = 1,
        alpha:     float | int = 100,
        isfrozen:  bool = False,
    ) -> None:
        self.__id = __id
        self._position = position
        self._rotation = rotation
        self._dimension = dimension
        self._interior = interior
        self._alpha = alpha
        self._isfrozen = isfrozen

    def getID(self) -> ElementID:
        return self.__id

    def setPosition(self, position: Vector3) -> T:
        """
            Set Player Position
            `Params:` Vector3
            >>> myobj.setPosition(Vector3(0, 0, 5))
        """
        self._position = position
        assert self._position == position
        return True

    def setRotation(self, rotation: Vector3) -> T:
        """
            Set Object rotation
            `Params:` Vector3
            >>> myobj.setRotation(Vector3(0, 0, 5))
        """
        self._rotation = rotation
        assert self._rotation == rotation
        return True

    def setDimension(self, dimension: Dimension) -> T:
        """
            Set Object dimension
            `Params:` Dimension
            >>> myobj.setRotation(Vector3(0, 0, 5))
        """
        self._dimension = dimension
        assert self._dimension == dimension
        return True

    def getDimension(self) -> int:
        """
            Get Object Dimension
            >>> dimension = myobj.getDimension()
        """
        return self._dimension

    def getInterior(self) -> int:
        """
            Get Object Interior
            >>> interior = myobj.getInterior()
        """
        return self._interior

    def getPosition(self) -> Vector3:
        """
            Get Player Position
            >>> position = myobj.getPosition()
        """
        return self._position

    def getRotation(self) -> Vector3:
        """
            Get Player Rotation
            >>> roration = myobj.getRotation()
        """
        return self._rotation

    def getDimension(self) -> Vector3:
        """
            Get Player Dimension
            >>> dimension = myobj.getDimension()
        """
        return self._rotation


class Object(ObjBase):
    def __init__(
        self,
        position: Vector3,
        rotation: Vector3,
        dimension: int | float = 0,
        interior:  int | float = 1,
        scale:     float | int = 1,
        alpha:     float | int = 100,
        isfrozen:  bool = False
    ) -> None:
        super(Object, self).__init__(
            position,
            rotation,
            dimension,
            interior,
            alpha,
            isfrozen
        )


class Color:
    def __init__(self, red: float | int, green: float | int, blue: float | int, alpha: float | int) -> None:
        self.red = red
        self.green = green
        self.blue = blue
        self.alpha = alpha

    def get(self) -> Tuple[float | int, float | int, float | int, float | int]:
        return (self.red, self.green, self.blue, self.alpha)
