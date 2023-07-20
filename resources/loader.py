"""
    SafeMTA Resource Loader
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


class ResourceLoader:
    def __init__(
        self,
        core_names: List[str],
        directories: List[str],
        server_base_dir: str,
    ) -> None:
        self.BASE_DIR = '\\'.join(__file__.split('\\')[:-1])
        self.resource_cores_names = core_names
        self.resource_cores = []
        self._directories = directories
        self._server_base_dir = server_base_dir

        # Supported Extensions must be starts with dot
        self.supported_exts = [".json"]  # TODO add .yaml

        self._info_keys = [
            ["name", "title", "n", "t"],
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
        for _dir in directories:
            self.get_dirs(os.path.join(server_base_dir, _dir))

    def start_loading(self) -> bool:
        for directory in self._directories:
            directory = os.path.join(self._server_base_dir, directory).replace("/", "\\")
            for _resource in self.resource_cores:
                if _resource.endswith(self.supported_exts[0]):  # .json
                    _resource = os.path.join(directory, _resource)
                    print("_resource: ", _resource)
                    with open(_resource, "r+", encoding="utf-8") as _file:
                        try:
                            _resource_buffer = json.load(_file)
                        except json.decoder.JSONDecodeError:
                            _file.write('{}')
                            _resource_buffer = {}
                        for __key, __value in _resource_buffer.items():
                            # Collect Resource Info:

                            # Default Values:
                            _name = "SafeMTA Resource"
                            _author = "<unknown>"
                            _description = ""
                            _version = "V1.0"
                            _oop = False

                            if __key in self._info_keys[0]:  # Name
                                _name = __value
                            elif __key in self._info_keys[1]:  # Author
                                _author = __value
                            elif __key in self._info_keys[2]:  # Description
                                _description = __value
                            elif __key in self._info_keys[3]:  # Version
                                _version = __value
                            elif __key in self._info_keys[4]:  # OOP
                                if isinstance(__value, bool) or isinstance(__value, int):
                                    _oop = bool(__value)
                                elif isinstance(__value, str):
                                    if __value.strip().lower() == "true":
                                        _oop = True
                                else:
                                    _oop = False
                            _resource_info = ResourceInfo(
                                name=_name,
                                author=_author,
                                description=_description,
                                version=_version,
                                oop=_oop
                            )

                            _extra_files = []
                            if __key in self._core_keys[0]:  # Extra
                                _extra_files = self._get_files(__value, _resource)
                            else:
                                _extra_files = []

                            if __key in self._core_keys[1]:  # Client
                                _client_files = self._get_files(__value, _resource)
                            else:
                                _client_files = []

                            if __key in self._core_keys[2]:  # Server
                                _server_files = self._get_files(__value, _resource)
                            else:
                                _server_files = []

                            self._resources.append(Resource(
                                client_files=_client_files,
                                extra_files=_extra_files,
                                server_files=_server_files,
                                core_path=self._get_resource_base_dir(_resource),
                                info=_resource_info,
                            ))

            print(self._resources)
        return True

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
        if os.path.isdir(directory):
            print(f"Got Dir: {directory}")
            for __dir in os.listdir(directory):
                if (
                    __dir.startswith('[')
                    and __dir.endswith(']')
                    and __dir.count('[') == 1
                    and __dir.count(']') == 1
                ):
                    print("recursion")
                    self.get_dirs(os.path.join(directory, __dir))
                else:
                    # Check if the filename in core names
                    print("AtHere")
                    print(__dir)
                    for _resource_file in os.listdir(f"{directory}\{__dir}"):
                        if _resource_file.strip() in self.resource_cores_names:
                            self.resource_cores.append(
                                os.path.join(directory, __dir, _resource_file).replace("/", "\\"))
