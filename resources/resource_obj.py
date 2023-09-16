from typing import List

from IronicMTA.resources.resource_file import ResourceFile
from IronicMTA.resources.resource_info import ResourceInfo


class Resource(object):
    """IronicMTA Resource"""

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

    def get_core_path(self) -> str:
        """Returns resource core path (meta.xml, resource.json, ...)"""
        return self._core_path

    def get_path(self) -> str:
        """Returns resource path"""
        return "\\".join(self._core_path.split("\\")[:-1])

    def get_client_files(self) -> List[ResourceFile]:
        """Get client files"""
        return self._client_files

    def get_server_files(self) -> List[ResourceFile]:
        """Get server files"""
        return self._server_files

    def get_extra_files(self) -> List[ResourceFile]:
        """Get extra files"""
        return self._extra_files

    def has_client_files(self) -> bool:
        return True if len(self._client_files) else False

    def has_server_files(self) -> bool:
        return True if len(self._server_files) else False

    def has_extra_files(self) -> bool:
        return True if len(self._extra_files) else False

    def get_name(self) -> str:
        """Resource Name"""
        return self._info.get_name()

    def get_author(self) -> str:
        """Resource Author"""
        return self._info.get_author()

    def get_description(self) -> str:
        """Resource Description"""
        return self._info.get_description()

    def get_version(self) -> str:
        """Resource version"""
        return self._info.get_version()

    def is_oop_enabled(self) -> bool:
        """Returns True if OOP is enables else False"""
        return self._info.is_oop_enabled()

    def __str__(self) -> str:
        return self._info.get_name()
