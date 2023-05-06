from typing import Tuple

class Vector2:
    def __init__(self, x: float | int, y: float | int) -> None:
        self.x = x
        self.y = y
    def get(self) -> Tuple[float | int, float | int]:
        return (self.x, self.y)

class Vector3:
    def __init__(self, x: float | int, y: float | int, z: float | int) -> None:
        self.x = x
        self.y = y
        self.z = z
    def get(self) -> Tuple[float | int, float | int, float | int]:
        return (self.x, self.y, self.z)