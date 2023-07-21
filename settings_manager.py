"""
    Settings manager
"""

from typing import Dict, Tuple, Literal
from errors import SettingsLoading, SettingsFile, InvalidPortNumber
from socket import gethostbyname, gethostname
from os.path import isfile, join, realpath
import json

class SettingsManager:
    """
        MTA Server Settings
    """
    def __init__(self) -> None:
        self._isloaded = False
        self._settings_file_path = None
        self.default_settings = {
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
                "max_http_connections": 32
            },
            "check_ports_before_start": True,
            "anticheat": {
                "disable_ac": [],
                "enable_sd": []
            },
            "version": {
                "minclientversion": "1.5.9-9.21437.0",
                "minclientversion_auto_update": 1,
                "recommendedclientversion": ""
            },
            "server_id_file": "server-id.keys",
            "log_file": "logs/server.log",
            "fpslimit": 60,
            "voice": {
                "enabled": False,
                "voice_samplerate": 1,
                "voice_quality": 4,
            },
            'databases': {
                'MySQL': {
                    'host': '127.0.0.1',
                    'user': 'root',
                    'password': '',
                    'database': 'IronicMTAdb',
                    'port': 3306
                },
                'SQLite3': {
                    'database_path': None
                }
            },
            "resources": {
                "resources_folders": [
                    "recources/",
                ],
                "resource_cores_files": []
            }
        }

    def load(self) -> Literal[True] | None:
        if self._isloaded:
            raise SettingsLoading("Settings already loaded. try to reload()")
        if not self._settings_file_path:
            raise SettingsLoading("Settings Manager has no settings file path. try to setSettingsFilePath()")
        with open(self._settings_file_path, 'r+') as file:
            try:
                self._content = json.load(file)
            except json.decoder.JSONDecodeError:
                file.write('{}')
                self._content = {}
            self._content = self._strip_keys(self._check_settings(self._content))
            file.seek(0)
            json.dump(self._content, file, indent=4)
            file.truncate()
        self._isloaded = True
        return True
    
    def setSettingsFilePath(self, path: str) -> Literal[True] | None:
        if isfile(path):
            self._settings_file_path = path
            return True
        raise SettingsFile(f"Settings file doesn't exists (Expected path: '{path}'). try to reformat your path.")

    def reload(self):
        if not self._isloaded:
            raise SettingsLoading("Settings is not loaded, try to reload()")
        with open('settings.json', 'r+') as file:
            try:
                self._content = json.load(file)
            except json.decoder.JSONDecodeError:
                file.write('{}')
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

    def getServerAddr(self) -> Tuple[str, int] | None:
        """
            `Returns`: (IP: str, Port: int)

        """
        self.try2load()
        _ip   = None
        # _port = self._content["server"]['port']
        _port = self._get_port("server", "port", "debug_port")
        _ip = self._content["server"]["ip"]
        if _ip == "auto":
            _ip = gethostbyname(gethostname())

        return (_ip, _port)
    
    def getHttpPort(self) -> int:
        return self._get_port("http_server", "http_port", "debug_http_port")
    
    def _get_port(self, section: str, release_port_key: str, debug_port_key: str) -> int:
        self.try2load()
        _port = self._content[section][release_port_key]
        if debug_port_key in self._content[section].keys():
            _debug_http_port = self._content[section][debug_port_key]
            if isinstance(_debug_http_port, int):
                if self.isValidPort(_debug_http_port):
                    return _debug_http_port
            elif isinstance(_debug_http_port, str):
                _debug_http_port = _debug_http_port.strip()
                if self.isValidPort(int(_debug_http_port)):
                    return _debug_http_port
            else:
                raise InvalidPortNumber("Invalid Port Number.")
        return _port

    def get(self) -> Dict[str, int | bool | str]:
        if not self._isloaded:
            raise SettingsLoading("Settings is not loaded, try to reload()")
        return self._content
    
    def isValidPort(self, port: int):
        try:
            if not isinstance(port, int):
                port = int(port)
            if 0 <= port <= 65535:  # Valid port range is from 0 to 65535
                return True
            else:
                return False
        except ValueError:
            return False

    @property
    def isloaded(self) -> bool:
        """
        `Returns`: bool
        Check if settings is loaded
        """
        return self._isloaded

    def try2load(self) -> Literal[True] | None:
        if self._isloaded:
            return True
        self.load()
