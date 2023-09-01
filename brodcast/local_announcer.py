from ..common import QueryTypes
import socket
import time
from .queries import QueryLight, QueryFull, QueryXFireLight


class LocalServerListAnnouncer(socket.socket):
    """
        Server ASE Queries Brodcaster
        Shows server in local game server list.
    """

    def __init__(self, server, ip: str = "0.0.0.0") -> None:
        super().__init__(socket.AF_INET, socket.SOCK_DGRAM)
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._buffer = 100
        self.port = server.get_address()[1]
        self._announcement_addr = (ip, self.port + 123)
        self.logger = server.get_logger()
        self.uptime = time.time()
        self._query = ""
        self._last_query_sent = 0
        self._last_player_count = 0
        self._server = server
        self._current_player_count = 0

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

        self._server.event.call("onAseServerStart")

        try:
            while True:
                if self._server.is_running():
                    self._current_player_count = self._server.get_player_count()
                self.uptime = time.time() - self.uptime
                _data = self.recvfrom(self._buffer)
                addr = _data[1]
                if len(_data[0]) == 1:
                    match _data[0]:
                        case QueryTypes.LightRelease.value:
                            if (
                                self._query == ""
                                or time.time() - self._last_query_sent > 10  # Query Light Cache Interval
                                or self._current_player_count != self._last_player_count
                            ):
                                self._last_player_count = self._current_player_count
                                self._last_query_sent = time.time()
                                self._query = str(QueryLight(self._server))

                        case QueryTypes.Full.value:
                            self._last_player_count = self._current_player_count
                            self._last_query_sent = time.time()
                            self._query = str(QueryFull(self._server))

                        case QueryTypes.XFire.value:
                            self._last_player_count = self._current_player_count
                            self._last_query_sent = time.time()
                            self._query = str(QueryXFireLight(self._server))

                        case QueryTypes.Version.value:
                            self._query = self._server.get_ase_version().name

                    if self._query != "":
                        self.sendto(bytes(self._query, encoding="utf-8"), addr)

        except KeyboardInterrupt:
            ...
