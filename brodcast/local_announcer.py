from .types import QueryTypes
import socket
import time

from .queries import QueryLight
from .vars import AseVersion

class LocalServerListAnnouncer(socket.socket):
    """
        Server ASE Queries Brodcaster
        Shows server in local game server list.
    """
    def __init__(self, server, ip: str = "0.0.0.0") -> None:
        super().__init__(socket.AF_INET, socket.SOCK_DGRAM)
        self._buffer                = 1024
        self.port                   = server.getAddr()[1]
        self._announcement_addr     = (ip, self.port + 123)
        self.logger                 = server.getLogger()
        self.uptime                 = time.time()
        self._query                 = ""
        self._last_query_sent       = 0
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
                if self._server.isRunning():
                    self._current_player_count = self._server.getPlayerCount()
                self.query_light_data = {
                    'ase_version': AseVersion.v1_5,
                    'build_number': '1',
                    'build_type': '9',
                    'net_route': 30,
                    'ping': 30,
                    'up_time': str(self.uptime),
                    'settings_manager': self._server.getSettingsManager(),
                    'players': self._server.getAllPlayers()
                }
                self.uptime = time.time() - self.uptime
                _data = self.recvfrom(self._buffer)
                addr = _data[1]
                if len(_data[0]) == 1:
                    match _data[0]:
                        case self.queryTypes.LightRelease:
                            if (
                                self._query == ""
                                or time.time() - self._last_query_sent > 10 # Query Light Cache Interval
                                or self._current_player_count != self._last_player_count
                                ):
                                    self._last_player_count = self._current_player_count
                                    self._last_query_sent = time.time()
                                    self._query = str(QueryLight(**self.query_light_data))

                        case self.queryTypes.Full:
                            print('Query Full')

                        case self.queryTypes.XFire:
                            print('Query XFire')

                        case self.queryTypes.Version:
                            print('Query Version')

                    if self._query != "":
                        self.sendto(bytes(self._query, encoding="utf-8"), addr)

        except KeyboardInterrupt: ...
