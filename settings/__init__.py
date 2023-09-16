from IronicMTA.errors import SettingsLoadingError, SettingsFileError, InvalidPortNumber

from socket import gethostbyname, gethostname
from os.path import isfile
from typing import TypedDict, Dict, Tuple
import json

from IronicMTA.settings.anticheat import AntiCheatSettings
from IronicMTA.settings.databases import DatabasesSettings
from IronicMTA.settings.http_server import HttpServerSettings
from IronicMTA.settings.resources import ResourcesSettings
from IronicMTA.settings.server import ServerSettings
from IronicMTA.settings.version import VersionSettings
from IronicMTA.settings.voice import VoiceSettings


class SettingsModel(TypedDict):
    """MTA:SA Server settings model"""

    server: ServerSettings
    http_server: HttpServerSettings
    check_ports_before_start: bool
    anticheat: AntiCheatSettings
    version: VersionSettings
    server_id_file: str
    log_file: str
    fpslimit: int
    voice: VoiceSettings
    databases: DatabasesSettings
    resources: ResourcesSettings


class SettingsManager(object):
    """IRonicMTA Settings manager"""

    def __init__(self, server) -> None:
        self._server = server
        self._isloaded = False
        self._settings_file_path = ""
        self.default_settings: SettingsModel = {
            "server": {
                "name": "Default IronicMTA Server",
                "ip": "auto",
                "port": 22000,
                "debug_port": 50000,
                "map_name": "San Adreas",
                "game_type": "Freeroam",
                "password": "",
                "max_players": 32,
            },
            "http_server": {
                "http_port": 22005,
                "debug_http_port": 60000,
                "max_http_connections": 32,
            },
            "check_ports_before_start": True,
            "anticheat": {"disabled_ac": [], "enabled_sd": []},
            "version": {
                "minclientversion": "1.5.9-9.21437.0",
                "minclientversion_auto_update": 1,
                "recommendedclientversion": "",
            },
            "server_id_file": "server-id.keys",
            "log_file": "server.log",
            "fpslimit": 60,
            "voice": {
                "enabled": False,
                "voice_samplerate": 1,
                "voice_quality": 4,
            },
            "databases": {
                "mysql": {
                    "enabled": True,
                    "host": "127.0.0.1",
                    "user": "root",
                    "password": "",
                    "database": "IronicMTA",
                    "port": 3306,
                },
                "sqlite3": {"enabled": False, "database_path": ""},
            },
            "resources": {
                "resources_folders": [
                    "resources/",
                ],
                "resource_cores_files": ["core"],
            },
        }

    def load(self) -> bool:
        """Load Settings

        Raises:
        -------
            SettingsLoading: Settings already loaded
            SettingsLoading: Settings file path not set

        Returns:
        --------
            Literal[True] | None: if all succeded
        """
        if self._isloaded:
            raise SettingsLoadingError("Settings already loaded. try to reload()")
        if not self._settings_file_path:
            raise SettingsLoadingError(
                "Settings file path not set. try to setSettingsFilePath()"
            )
        with open(self._settings_file_path, "r+") as file:
            try:
                self._content = json.load(file)
            except json.decoder.JSONDecodeError:
                file.write("{}")
                self._content = {}
            self._content = self._strip_keys(self._check_settings(self._content))
            file.seek(0)
            json.dump(self._content, file, indent=4)
            file.truncate()
        self._isloaded = True
        if self._server.is_running():
            self._server.event.call("onServerSettingsLoad", self._content)
        return True

    def set_settings_file_path(self, path: str) -> bool:
        """Set settings file path

        Args:
        -----
            path (str): Path of settings file

        Raises:
        -------
            SettingsFile: Settings file does not exists

        Returns:
        --------
            Literal[True] | None: if all succeded
        """
        if isfile(path):
            self._settings_file_path = path
            return True
        raise SettingsFileError(
            f'Settings file doesn"t exists (Expected path: "{path}"). try to reformat your path.'
        )

    def reload(self):
        """Reload settings

        Raises:
        -------
            SettingsLoading: Settings is not load
        """
        if not self._isloaded:
            raise SettingsLoadingError("Settings is not loaded, try to reload()")
        with open("settings.json", "r+") as file:
            try:
                self._content = json.load(file)
            except json.decoder.JSONDecodeError:
                file.write("{}")
                self._content = {}
            self._content = self._strip_keys(self._check_settings(self._content))
            file.seek(0)
            json.dump(self._content, file, indent=4)
            file.truncate()
        self._isloaded = True

    def _check_settings(self, data: dict) -> Dict[str, int | bool | None]:
        for key, value in self.default_settings.items():
            if not key in data.keys():
                data[key.strip()] = value
        return data

    def _strip_keys(self, data: dict) -> Dict[str, int | bool | None]:
        striped_keys = {}
        for key, value in data.items():
            striped_keys[key.strip()] = value
        return striped_keys

    def get_server_address(self) -> Tuple[str, int]:
        """Get Server Address

        Returns:
        --------
            Tuple[str, int] | None: Tuple of ip, port
        """
        self.try2load()
        _ip = None
        # _port = self._content["server"]["port"]
        _port = self._get_port("server", "port", "debug_port")
        _ip = self._content["server"]["ip"]
        if _ip == "auto":
            _ip = gethostbyname(gethostname())

        return (_ip, _port)

    def get_http_port(self) -> int:
        """Get Server HTTP Port

        Returns:
        --------
            int: HTTP prot
        """
        return self._get_port("http_server", "http_port", "debug_http_port")

    def _get_port(
        self, section: str, release_port_key: str, debug_port_key: str
    ) -> int:
        self.try2load()
        _port = self._content[section][release_port_key]
        if debug_port_key in self._content[section].keys():
            _debug_http_port = self._content[section][debug_port_key]
            if isinstance(_debug_http_port, int):
                if self.is_valid_port(_debug_http_port):
                    return _debug_http_port
            elif isinstance(_debug_http_port, str):
                _debug_http_port = _debug_http_port.strip()
                if self.is_valid_port(int(_debug_http_port)):
                    return int(_debug_http_port)
            else:
                raise InvalidPortNumber("Invalid Port Number.")
        return _port

    def get(self) -> SettingsModel:
        """Get Server settings

        Raises:
        -------
            SettingsLoading: Settings is not loaded

        Returns:
        --------
            Dict[str, int | bool | str]: Settings Dictionary
        """
        if not self._isloaded:
            raise SettingsLoadingError("Settings is not loaded, try to reload()")
        return self._content

    def is_valid_port(self, port: int) -> bool:
        """Check if that port is valid

        Args:
        -----
            port (int): port

        Returns:
        --------
            bool: True if is valid port
        """
        try:
            if not isinstance(port, int):
                port = int(port)
            if 0 < port <= 65535:  # Valid port range is from 0 to 65535
                return True
            else:
                return False
        except ValueError:
            return False

    @property
    def isloaded(self) -> bool:
        """Check if settings loaded

        Returns:
        --------
            bool: True if settings loaded
        """
        return self._isloaded

    def try2load(self) -> bool:
        """Try to load settings

        Returns:
        --------
            Literal[True] | None: if settings already loaded
        """
        if not self._isloaded:
            self.load()
        return True
