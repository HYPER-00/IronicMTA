"""
    Settings manager
"""

from typing import Dict, Tuple, Literal
from errors import SettingsLoading, SettingsFile
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
            "servername": "Default MTA Server",
            "mapname": "San Adreas",
            "gametype": "freeroam",
            "owner_email_address": "",
            "serverip": "auto",
            "serverport": 22000,
            "debugport": 50000,
            "maxplayers": 32,
            "httpport": 22005,
            "httpdownloadurl": "",
            "httpmaxconnectionsperclient": 5,
            "httpdosthreshold": 20,
            "http_dos_exclude": "",
            "allow_gta3_img_mods": "none",
            "disableac": 3,
            "enablesd": 0,
            "minclientversion": "1.5.9-9.21437.0",
            "minclientversion_auto_update": 1,
            "recommendedclientversion": "",
            "ase": 1,
            "donotbroadcastlan": 0,
            "password": "",
            "bandwidth_reduction": "medium",
            "player_sync_interval": 100,
            "lightweight_sync_interval": 1500,
            "camera_sync_interval": 500,
            "ped_sync_interval": 400,
            "unoccupied_vehicle_sync_interval": 400,
            "keysync_mouse_sync_interval": 100,
            "keysync_analog_sync_interval": 100,
            "bullet_sync": 1,
            "vehext_percent": 0,
            "vehext_ping_limit": 150,
            "latency_reduction": 0,
            "idfile": "server-id.keys",
            "logfile": "logs/server.log",
            "authfile": "logs/server_auth.log",
            "dbfile": "logs/db.log",
            "acl": "acl.xml",
            "scriptdebuglogfile": "logs/scripts.log",
            "scriptdebugloglevel": 0,
            "htmldebuglevel": 0,
            "filter_duplicate_log_lines": 1,
            "fpslimit": 60,
            "voice": 0,
            "voice_samplerate": 1,
            "voice_quality": 4,
            "backup_path": "backups",
            "backup_interval": 3,
            "backup_copies": 5,
            "compact_internal_databases": 1,
            "crash_dump_upload": 1,
            "auth_serial_groups": "Admin",
            "auth_serial_http": 1,
            "auth_serial_http_ip_exceptions": "127.0.0.1",
            "database_credentials_protection": 1,
            'databases': {
                'MySQL': {
                    'host': '127.0.0.1',
                    'user': 'root',
                    'password': '',
                    'database': 'pymtadb',
                    'port': 3306
                },
                'SQLite3': {
                    'database_path': None
                }
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
        path = realpath(path)
        print(path)
        if isfile(path):
            self._settings_file_path = path
            return True
        raise SettingsFile(f"Settings file doesn't exists (Expected path: '{path}'). try to reformat your path.")
    
    def _setup_path(self, path: str):
        if path.startswith(".") or path.startswith("/"):
            path = path[1:]
            path = self._setup_path(path)
        else:
            print("Returning,", path)
            return path

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
        _ip   = None
        _port = None
        if not self._isloaded:
            raise SettingsLoading("Settings is not loaded, try to load()")
        if (
            self._content['debugport']
            and str(self._content['debugport']).strip() != ''
            or self._content['debugport'] != 0
        ):
            _port = int(self._content['debugport'])
        _port =  int(self._content['serverport'])
        _ip = self._content['serverip']
        if _ip == "auto":
            _ip = gethostbyname(gethostname())

        return (_ip, _port)

    def get(self) -> Dict[str, int | bool | str]:
        if not self._isloaded:
            raise SettingsLoading("Settings is not loaded, try to reload()")
        return self._content

    @property
    def isloaded(self) -> bool:
        """
        `Returns`: bool
        Check if settings is loaded
        """
        return self._isloaded
