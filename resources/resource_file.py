from ..errors import ResourceFileError
from typing import Literal
from os.path import join, isfile, isdir, normpath
from sys import path

_dir = __file__.split('\\')[:-2]
if _dir[0].endswith(':'):
    _dir[0] += '\\'
_basedir = join(*_dir)
path.insert(0, _basedir)


class ResourceFile:
    """Resource file, verifies that file"""

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
            raise ResourceFileError(
                f"\"{self._path}\" is not a file (directory).")

    def getPath(self) -> str | None:
        """
            * Get file path
            Returns the file path if exists else returns None
        """
        return self._path

    def getPathFromResource(self, resource) -> str:
        """
            Get The relative file path
        """
        return normpath(f"{resource.get_name()}\\{''.join(self._path.split(resource.getPath()))}")

    def is_cachedable(self) -> Literal[False] | bool:
        """Is file cachable"""
        return self._cache

    def get_buffer(self) -> str:
        """Get File Content"""
        with open(self._path, 'r') as _file:
            return _file.read()
