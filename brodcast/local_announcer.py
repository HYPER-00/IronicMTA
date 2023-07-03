from .types import QueryTypes
import socket
import time
from core import PacketID, PacketPriority, PacketReliability

from .queries import QueryLight


class LocalServerListAnnouncer(socket.socket):
    """
        Server ASE Queries Brodcaster
        Shows server in local game server list.
    """

    def __init__(self, server, ip: str = "0.0.0.0") -> None:
        super().__init__(socket.AF_INET, socket.SOCK_DGRAM)
        self._buffer = 1024
        self.port = server.getAddress()[1]
        self._announcement_addr = (ip, self.port + 123)
        self.logger = server.getLogger()
        self.uptime = time.time()
        self._query = ""
        self._last_query_sent = 0
        self._last_player_count = 0
        self._server = server

    def start(self):
        try:
            self.bind(self._announcement_addr)
        except OSError as err:
            print(err)
            if 'Only one usage of each socket address' in err:
                self.logger.error('Server Address in use.')
                input("Press Enter to continue...")
                exit(-1)
        except err:
            print(err)

        self.query_types = QueryTypes()

        try:
            while True:
                if self._server.isRunning():
                    _current_player_count = self._server.getPlayerCount()
                self.uptime = time.time() - self.uptime
                _data = self.recvfrom(self._buffer)
                addr = _data[1]
                if len(_data[0]) == 1:
                    match _data[0]:
                        case self.query_types.LightRelease:
                            if (
                                self._query == ""
                                or time.time() - self._last_query_sent > 10  # Query Light Cache Interval
                                or _current_player_count != self._last_player_count
                            ):
                                self._last_player_count = _current_player_count
                                self._last_query_sent = time.time()
                                self._query = str(QueryLight(self._server))
                        case self.query_types.Full:
                            print('Query Full')

                        case self.query_types.XFire:
                            print('Query XFire')

                        case self.query_types.Version:
                            print('Query Version')

                    if self._query != "":
                        self.sendto(bytes(self._query, encoding="utf-8"), addr)

        except KeyboardInterrupt:
            ...
