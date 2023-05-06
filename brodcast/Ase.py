import sys
import os

_dir = __file__.split('\\')[:-2]
if _dir[0].endswith(':'): _dir[0] += '\ '.strip()
sys.path.insert(0, os.path.join(*_dir))

import os
import socket
import time
import xmltodict
import requests
from player_manager import Player, Vector3
from brodcast.QueryHandler import *
from settings_manager import SettingsManager

settings_manager = SettingsManager()
settings = settings_manager.get()
port = settings_manager.getServerAddr()[1]

players = []
for i in range(5):
    players.append(
        Player(
            nick="0x",
            serial="855CDC19EF72614A35D872A63BEDBCB2",
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
    def __init__(self, logger, ip: str="0.0.0.0", announcement_port: int=34219) -> None:
        super().__init__(socket.AF_INET, socket.SOCK_DGRAM)
        self._buffer        = 1024
        self.server_addr    = (ip, announcement_port)
        self.logger         = logger

    def start(self):
        try:
            self.bind(self.server_addr)
            while True:
                self._data, self.addr = self.recvfrom(self._buffer)
                self.sendto(bytes(f"MTA-SERVER {port + 123}", "utf8"), self.addr) # Play Port = 50123 | Status = 50000
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
            settings_manager=SettingsManager()
        )
        self._response = requests.post(self.url, bytes(str(self._data), encoding='utf-8'))
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
    !    'r' -> QueryLightCached (Created to avoid ddos attack from server browsers)
    !    The Interval between 2 Query Light Cache is 10s 
    !
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    """
    def __init__(self, logger, ip: str="0.0.0.0", port: int=port + 123) -> None:
        super().__init__(socket.AF_INET, socket.SOCK_DGRAM)
        self._buffer                = 1024
        self.port                   = port
        self.server_addr            = (ip, port)
        self.logger                 = logger
        self.uptime                 = time.time()
        self._query_light           = ''
        self._last_query_sent       = None
        self._last_player_count     = None

    def start(self):
        try:
            self.bind(self.server_addr)
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
                self.query_light_data = {
                    'ase_version': AseVersion().v1_5,
                    'build_number': '1',
                    'build_type': '9',
                    'net_route': 30,
                    'ping': 30,
                    'up_time': str(self.uptime),
                    'settings_manager': SettingsManager(),
                    'players': players
                }
                self.uptime = time.time() - self.uptime
                _data = self.recvfrom(self._buffer)
                addr = _data[1]
                try:
                    self._qtype = _data[0].decode()
                except UnicodeDecodeError:
                    self._qtype = 'unkown'
                match self._qtype:
                    case 'unkown':
                        print('unkown')
                        return
                    case self.queryTypes.LightRelease:
                        if self._last_query_sent:
                            if (
                                time.time() - self._last_query_sent >= 10 
                                or self._current_players_count != self._last_player_count
                            ):
                                print('x')
                                self._query_light = str(QueryLight(**self.query_light_data))
                        else:
                            self._query_light = str(QueryLight(**self.query_light_data))

                        self._last_query_sent = time.time()
                        if not isinstance(self._query_light, bytes):
                            self._query_light = bytes(self._query_light, encoding='utf-8')
                        self.sendto(self._query_light, addr)

                    case self.queryTypes.Full:
                        print('Query Full')

                    case self.queryTypes.XFire:
                        print('Query XFire')

                    case self.queryTypes.Version:
                        print('Query Version')

                _data = self.recvfrom(self._buffer)
                self.logger.log(f'Server Brodcast Recived From {_data[1][0]}:{_data[1][1]} | {_data[0]}')

        except KeyboardInterrupt: ...
