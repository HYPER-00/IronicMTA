from typing import List
from resource_file import ResourceFile
from resource_info import ResourceInfo

class Resource(object):
    """PyMTA Resource"""
    def __init__(
        self,
        core_path: str,

        client_files: List[ResourceFile],
        server_files: List[ResourceFile],
        extra_files: List[ResourceFile],

        info: ResourceInfo,
    ) -> None:
        self._core_path = core_path

        self._client_files = client_files
        self._server_files = server_files
        self._extra_files = extra_files

        self._info = info

    def getCorePath(self) -> str:
        """Returns resource core path (meta.xml, resource.json, ...)"""
        return self._core_path

    def getClientFiles(self) -> List[ResourceFile]:
        """Get client files"""
        return self._client_files

    def getServerFiles(self) -> List[ResourceFile]:
        """Get server files"""
        return self._server_files

    def getExtraFiles(self) -> List[ResourceFile]:
        """Get extra files"""
        return self._extra_files

    def getName(self) -> str:
        """Resource Name"""
        return self._info.getName()

    def getAuthor(self) -> str:
        """Resource Author"""
        return self._info.getAuthor()

    def getDescription(self) -> str:
        """Resource Description"""
        return self._info.getDescription()

    def getVersion(self) -> str:
        """Resource version"""
        return self._info.getVersion()

    def isOOPEnables(self) -> bool:
        """Returns True if OOP is enables else False"""
        return self._info.isOOPEnabled()

    def __str__(self) -> str:
        return self._info.getName()

    def __repr__(self) -> str:
        return f"<{self._info.getName()}>"
