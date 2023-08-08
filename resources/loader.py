"""
    IronicMTA Resource Loader
"""

from errors import ResourceFileError
import os
import sys
import json
from typing import List
from .resource_file import ResourceFile
from .resource_info import ResourceInfo
from .resource_obj import Resource

_dir = __file__.split('\\')[:-2]
if _dir[0].endswith(':'):
    _dir[0] += '\\'
sys.path.insert(0, os.path.join(*_dir))


class ResourceLoader(object):
    """Resource Loader

    Args:
        server (Server): IronicMTA Server
    """    
    def __init__(self, server) -> None:
        _settings = server.getSettings()
        self.resource_cores_names = _settings["resources"]["resource_cores_files"]
        self._directories = _settings["resources"]["resources_folders"]
        self.resource_cores = []
        self._resources_names = []
        self._server_base_dir = server.getBaseDirectory()

        self._client_files = []
        self._extra_files = []
        self._server_files = []
        
        self._server = server

        # Supported Extensions must be starts with dot
        self.supported_exts = [".json"]  # TODO add .yaml

        self._info_keys = [
            ["author", "a"],
            ["description", "d"],
            ["version", "v"],
            ["oop", "o"]
        ]
        self._core_keys = [
            ["extra", "extrafiles", "files"],
            ["client", "clientfiles", "clientscripts", "luaclient"],
            ["server", "serverfiles", "serverscripts", "luaserver"]
        ]

        self._resources = []
        for _dir in self._directories:
            self.get_dirs(os.path.join(self._server_base_dir, _dir))

    def get_all_resources(self) -> List[Resource]:
        return self._resources
    
    def load_resource(self, resource_name: str) -> bool:
        for directory in self._directories:
            directory = os.path.join(
                self._server_base_dir, directory).replace("/", "\\")

    def start_loading(self) -> bool:
        """Start Resource loading from default folders

        Returns:
            bool: True if all resources has been loaded successfuly (without errors)
        """        
        for directory in self._directories:
            directory = os.path.join(
                self._server_base_dir, directory).replace("/", "\\")
            for _resource in self.resource_cores:
                if _resource.endswith(self.supported_exts[0]):  # .json
                    _resource = os.path.join(directory, _resource)
                    with open(_resource, "r+", encoding="utf-8") as _file:
                        try:
                            _resource_buffer = json.load(_file)
                        except json.decoder.JSONDecodeError:
                            _file.write('{}')
                            _resource_buffer = {}

                        # Default Values:
                        _author = "<unknown>"
                        _description = ""
                        _version = "V1.0"
                        _oop = False

                        for __key, __value in _resource_buffer.items():
                            # Collect Resource Info:
                            if __key in self._info_keys[0]:  # Author
                                _author = __value
                            elif __key in self._info_keys[1]:  # Description
                                _description = __value
                            elif __key in self._info_keys[2]:  # Version
                                _version = __value
                            elif __key in self._info_keys[3]:  # OOP
                                if isinstance(__value, bool) or isinstance(__value, int):
                                    _oop = bool(__value)
                                elif isinstance(__value, str):
                                    if __value.strip().lower() == "true":
                                        _oop = True
                                else:
                                    _oop = False
                            _resource_info = ResourceInfo(
                                name="".join(_resource.split("\\")[-2]),
                                author=_author,
                                description=_description,
                                version=_version,
                                oop=_oop
                            )

                            _extra_files = []
                            if __key in self._core_keys[0]:  # Extra
                                self._extra_files = self._get_files(
                                    __value, _resource)
                            
                            if __key in self._core_keys[1]:  # Client
                                self._client_files = self._get_files(
                                    __value, _resource)

                            if __key in self._core_keys[2]:  # Server
                                self._server_files = self._get_files(
                                    __value, _resource)

                        self.load_resource(
                            client_files=self._client_files,
                            extra_files=self._extra_files,
                            server_files=self._server_files,
                            core_path=_resource,
                            resource_info=_resource_info,
                        )
        return True
    
    def load_resource(
        self,
        client_files: List[ResourceFile],
        extra_files:  List[ResourceFile],
        server_files: List[ResourceFile],
        core_path: str,
        resource_info: ResourceInfo,
    ):      
        _resource = Resource(
            client_files=client_files,
            extra_files=extra_files,
            server_files=server_files,
            core_path=core_path,
            info=resource_info,
        )
        self._resources.append(_resource)
        self._server.event.call("onResourceLoad", _resource)

    def _get_files(self, __value, _resource) -> List[ResourceFile]:
        """Returns the files from the json buffer"""
        _files = []
        if isinstance(__value, list):
            for __file in __value:
                if isinstance(__file, str):
                    _file_path = os.path.join(
                        self._get_resource_base_dir(_resource), __file)
                    self._perform_checks(_resource, __file, _file_path)
                    _files.append(ResourceFile(_file_path))
        elif isinstance(__value, str):
            _file_path = os.path.join(
                self._get_resource_base_dir(_resource), __value)
            self._perform_checks(_resource, __value, _file_path)
            _files.append(ResourceFile(_file_path))

        return _files

    def _perform_checks(self, resource: str, file: str, file_path: str) -> None:
        """
            Raises Error when: file names as resource core name or file not found
        """
        _core_name_found = False
        for _core_name in self.resource_cores:
            if file.startswith(_core_name + "."):
                _core_name_found = True
        for _ext in self.supported_exts:
            if file.endswith(_ext) and _core_name_found:
                raise ResourceFileError(
                    "Cannot name resource file a resource core name.")

        if not os.path.isfile(file_path):
            raise ResourceFileError(
                f"Resource file not found in resource \"{self._get_resource_name_from_path(resource)}\"\n"
                f"  File path in resource core: \"{file}\"\n"
                f"  Expected Path: \"{file_path}\"\n"
            )

    def _get_resource_base_dir(self, _resource: str) -> str:
        _resource = _resource.split('\\')[:-1]
        if _resource[0].endswith(':'):
            _resource[0] += '\\'
        return os.path.join(*_resource)

    def _get_resource_name_from_path(self, _resource: str) -> str:
        return _resource.split('\\')[-2]

    def get_dirs(self, directory: str) -> None:
        """Returns resources cores from directory"""
        directory = directory.replace("/", "\\")
        if os.path.isdir(directory):
            for __dir in os.listdir(directory):
                if (
                    __dir.startswith('[')
                    and __dir.endswith(']')
                    and __dir.count('[') == 1
                    and __dir.count(']') == 1
                ):
                    self.get_dirs(os.path.join(directory, __dir))
                else:
                    # Check if the filename in core names
                    for _resource_file in os.listdir(f"{directory}\{__dir}"):
                        if "".join(_resource_file.strip().split(".")[:-1]) in self.resource_cores_names:
                            self._resources_names.append(__dir)
                            self.resource_cores.append(
                                os.path.join(directory, __dir, _resource_file).replace("/", "\\"))
