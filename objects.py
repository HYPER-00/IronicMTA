from vectors import Vector2, Vector3
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

class ObjBase:
    def __init__(
        self,
        position:          Vector3,
        rotation:          Vector3,
        dimension: int   | float = 0,
        interior:  int   | float = 1,
        alpha:     float | int   = 100,
        isfrozen:  bool          = False,
    ) -> None:
        self._position = position
        self._rotation = rotation
        self._dimension = dimension
        self._interior = interior
        self._alpha = alpha
        self._isfrozen = isfrozen

    def setPosition(self, position: Vector3) -> T:
        self._position = position
        assert self._position == position
        return True
    
    def setRotation(self, rotation: Vector3) -> T:
        self._rotation = rotation
        assert self._rotation == rotation
        return True
    
    def setDimension(self, dimension: Dimension) -> T:
        self._dimension = dimension
        assert self._dimension == dimension
        return True

class Object(ObjBase):
    def __init__(
        self, 
        position: Vector3, 
        rotation: Vector3, 
        dimension: int   | float = 0, 
        interior:  int   | float = 1, 
        scale:     float | int   = 1,
        alpha:     float | int   = 100, 
        isfrozen:  bool          = False
    ) -> None:
        super(Object, self).__init__(
            position, 
            rotation, 
            dimension, 
            interior, 
            alpha, 
            isfrozen
        )
    def move(
        self,
        time: float,
        target_position: Vector3,
        target_rotation: Vector3,
        start_position: Vector3,
        start_rotation: Vector3,
    ): ...

class Color:
    def __init__(self, red: float | int, green: float | int, blue: float | int, alpha: float | int) -> None:
        self.red = red
        self.green = green
        self.blue = blue
        self.alpha = alpha
    def get(self) -> Tuple[float | int, float | int, float | int, float | int]:
        return (self.red, self.green, self.blue, self.alpha)
