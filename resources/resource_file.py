from os.path import join, isfile, isdir
from sys import path

_dir = __file__.split('\\')[:-2]
if _dir[0].endswith(':'): _dir[0] += '\\'
_basedir = join(*_dir)
path.insert(0, _basedir)
print(_basedir)

from typing import Literal
from errors import ResourceFileError

class ResourceFile:
    """Resource file, verifies  the file"""
    def __init__(self, path: str, cache: bool = False) -> None:
        self._path = path
        self._cache = cache
        if not path[2] == ":":
            self._path = join(_basedir, path).replace("/", "\\")
        if not isfile(self._path):
            raise ResourceFileError(f"Resource file doesn't exists"
                                    f"(given path: \"{path}\")"
                                    f"(abstract path: {self._path})")
        if isdir(self._path):
            raise ResourceFileError(f"\"{self._path}\" is not a file (directory).")

    def getPath(self) -> str | None:
        """Returns the file path if exists else returns None"""
        return self._path
    
    def isCachable(self) -> Literal[False] | bool:
        """Is file cachable"""
        return self._cache
