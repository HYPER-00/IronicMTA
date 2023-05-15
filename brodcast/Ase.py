import sys
import os

_dir = __file__.split('\\')[:-2]
if _dir[0].endswith(':'): _dir[0] += '\\'
sys.path.insert(0, os.path.join(*_dir))

import os
import socket
import time
import xmltodict
from player_manager import Player, Vector3
from brodcast.query_handler import *
from settings_manager import SettingsManager
try:
    import requests
except:
    ...

players = []
for i in range(5):
    players.append(
        Player(
            nick="0x",
            serial="855CDC19EF7288FAKE8872A63BEDBCB2",
            ip="127.0.0.1",
            position=Vector3(0, 0, 0),
            rotation=Vector3(0, 0, 0),
            ping=2
        )
    )

class LocalServerAnnouncement(socket.socket):
    """
        Server Browser Port: 34219
        Status Port: Game Port - 123
    """
    def __init__(self, server, logger, ip: str="0.0.0.0", announcement_port: int=34219) -> None:
        super().__init__(socket.AF_INET, socket.SOCK_DGRAM)
        self._buffer        = 1024
        self._announcement_addr    = (ip, announcement_port)
        self.logger         = logger

        _settings_manager = server.getSettingsManager()
        self._port = _settings_manager.getServerAddr()[1]

    def start(self):
        try:
            self.bind(self._announcement_addr)
            while True:
                self._data, self.addr = self.recvfrom(self._buffer)
                self.sendto(bytes(f"MTA-SERVER {self._port + 123}", "utf8"), self.addr) # Play Port = 50123 | Status = 50000
                self.logger.log(f'Local Server Announcement Recived From {self.addr[0]}:{self.addr[1]} | {self._data.decode("utf-8")}')
        except KeyboardInterrupt:
            ...
        except OSError as err:
            print(err)
            if 'Only one usage of each socket address' in err.strerror:
                self.logger.error('Server Address in use.')
                quit(-1)

class MasterServerAnnouncement:
    def __init__(self, logger, server_url: str, settings_manager: SettingsManager):
        self.logger = logger
        self.server_url = server_url

        self._settings_manager = settings_manager
        if not self._settings_manager.isloaded:
            self._settings_manager.load()
        self.settings = self._settings_manager.get()

        self.port = self._settings_manager.getServerAddr()[1]
        self.version = '1.5.8-1.0'
        self.extra   = '0_0_0_0_0'
        self.url = f'{self.server_url}?g={self.port}&a={self.port + 123}&h={self.settings["httpport"]}&v={self.version}&x={self.extra}&ip=0.0.0.0'

    def announce(self):
        self._data = QueryLight(
            players=players,
            ase_version=AseVersion().v1_5,
            build_number='9',
            build_type='9',
            net_route=30,
            ping=30,
            up_time='10',
            settings_manager=self._settings_manager
        )
        try:
            self._response = requests.post(self.url, bytes(str(self._data), encoding='utf-8'), timeout=5)
        except:
            self.logger.warn("Couldn't Announce Server To Master Server List. check network")
            return {}
        return xmltodict.parse(self._response.text)

class ServerBrodcast(socket.socket):
    """
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    !
    !    When send 'MTA SERVER ASE-PORT' the information window port is ASE-PORT - 123
    !    PORT TO SEND ASE-PORT+123
    !    Debug Port: 50000
    !    Information Window port: 50000
    !    Game Port : 50123
    !    'r' -> QueryLightCached (to avoid ddos attack from server browsers)
    !    The Interval between 2 Query Light Cache is 10s 
    !
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    """
    def __init__(self, logger, server, port: int, ip: str="0.0.0.0") -> None:
        super().__init__(socket.AF_INET, socket.SOCK_DGRAM)
        self._buffer                = 1024
        self.port                   = port
        self._announcement_addr            = (ip, port)
        self.logger                 = logger
        self.uptime                 = time.time()
        self._query_light           = None
        self._first_query_sent       = None
        self._last_player_count     = 0
        self._server                = server

    def start(self):
        try:
            self.bind(self._announcement_addr)
        except OSError as err:
            print(err)
            if 'Only one usage of each socket address' in err:
                self.logger.error('Server Address in use.')
                input("Press Enter to continue...")
                exit(-1)
        except Exception as err:
            print(err)

        self.queryTypes = QueryTypes()

        try:
            while True:
                self._current_players_count = len(players)
                if self._server.isRunning():
                    self._last_player_count = self._server.getPlayerCount()
                self.query_light_data = {
                    'ase_version': AseVersion().v1_5,
                    'build_number': '1',
                    'build_type': '9',
                    'net_route': 30,
                    'ping': 30,
                    'up_time': str(self.uptime),
                    'settings_manager': self._server.getSettingsManager(),
                    'players': players
                }
                self.uptime = time.time() - self.uptime
                _data = self.recvfrom(self._buffer)
                addr = _data[1]
                try:
                    self._qtype = _data[0]
                    print(self._qtype)
                    self._qtype = self._qtype.decode()
                except UnicodeDecodeError:
                    self._qtype = 'GamePacket'
                match self._qtype:
                    case self.queryTypes.LightRelease:
                        if self._first_query_sent:
                            if (
                                time.time() - self._first_query_sent >= 10 # Query Light Interval
                                or self._current_players_count != self._last_player_count
                            ):
                                self._query_light = str(QueryLight(**self.query_light_data))
                        else:
                            self._query_light = str(QueryLight(**self.query_light_data))

                        self._first_query_sent = time.time()
                        if not isinstance(self._query_light, bytes):
                            self._query_light = bytes(self._query_light, encoding='utf-8')
                        self.sendto(self._query_light, addr)

                    case self.queryTypes.Full:
                        print('Query Full')

                    case self.queryTypes.XFire:
                        print('Query XFire')

                    case self.queryTypes.Version:
                        print('Query Version')

                    case 'GamePacket':
                        print('GamePacket')
                        return

                _data = self.recvfrom(self._buffer)
                self.logger.log(f'Server Brodcast Recived From {_data[1][0]}:{_data[1][1]} | {_data[0]}')

        except KeyboardInterrupt: ...
