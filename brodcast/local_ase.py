import socket
from common import (
    LOCAL_SERVER_LIST_ASE_PORT,
    LOCAL_SERVER_LIST_ASE_MESSAGE
)

class LocalServerListASE(socket.socket):
    # Status Port: Game Port - 123
    def __init__(self, server, ip: str="0.0.0.0") -> None:
        super().__init__(socket.AF_INET, socket.SOCK_DGRAM)
        self._buffer = 1024
        self._announcement_addr = (ip, LOCAL_SERVER_LIST_ASE_PORT)
        self.logger = server.getLogger()
        _settings_manager = server.getSettingsManager()
        self._port = _settings_manager.getServerAddr()[1]

    def start(self):
        """
            Start Local Server Ase
            Tells MTA Client local server list port
        """
        try:
            self.bind(self._announcement_addr)
            while True:
                self._data, self.addr = self.recvfrom(self._buffer)
                self.sendto(bytes(f"{LOCAL_SERVER_LIST_ASE_MESSAGE} {self._port + 123}", "utf8"), self.addr) # Play Port = 50123 | Status = 50000
                self.logger.log(f'Local Server Announcement Recived From {self.addr[0]}:{self.addr[1]} | {self._data.decode("utf-8")}')
        except KeyboardInterrupt:
            ...
        except OSError as err:
            print(err)
            if 'Only one usage of each socket address' in err.strerror:
                self.logger.error('Server Address in use.')
                quit(-1)
