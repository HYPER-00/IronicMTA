import socket
from common import (
    LOCAL_SERVER_LIST_ASE_PORT,
    LOCAL_SERVER_LIST_ASE_MESSAGE
)


class LocalServerListASE(socket.socket):
    # Status Port: Game Port - 123
    def __init__(self, server, ip: str = "0.0.0.0") -> None:
        super().__init__(socket.AF_INET, socket.SOCK_DGRAM)
        self._announcement_addr = (ip, LOCAL_SERVER_LIST_ASE_PORT)
        self.logger = server.getLogger()
        _settings_manager = server.getSettingsManager()
        self._ip, self._port = _settings_manager.getServerAddr()

    def start(self):
        """
            Start Local Server Ase
            Tells MTA Client local server list port
        """
        try:
            self.bind(self._announcement_addr)
            self.logger.log(
                f"Local Server List ASE Bind On {self._ip}:{self._port}.")
            while True:
                self._data, self.addr = self.recvfrom(512)
                # Play Port = 50123 | Status = 50000
                self.sendto(
                    bytes(f"{LOCAL_SERVER_LIST_ASE_MESSAGE} {self._port + 123}", "utf-8"), self.addr)
        except KeyboardInterrupt:
            ...
        except OSError as err:
            print(err)
            if 'Only one usage of each socket address' in err.strerror:
                self.logger.error('Server Address in use.')
                quit(-1)
