import socket
from IronicMTA.common import (
    LOCAL_SERVER_LIST_ASE_PORT,
    LOCAL_SERVER_LIST_ASE_MESSAGE
)


class LocalServerListASE(socket.socket):
    def __init__(self, server, ip: str = "0.0.0.0") -> None:
        super().__init__(socket.AF_INET, socket.SOCK_DGRAM)
        # Status Port: Game Port - 123
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._announcement_addr = (ip, LOCAL_SERVER_LIST_ASE_PORT)
        self.logger = server.get_logger()
        _settings_manager = server.get_settings_manager()
        self._ip, self._port = _settings_manager.get_server_address()
        self._server = server

    def start(self):
        """
            Start Local Server Ase
            Tells MTA Client local server list port
        """
        try:
            self.bind(self._announcement_addr)
            self.logger.log(
                f"Local Server List ASE Bind On {self._ip}:{self._port}.")
            while self._server.is_running():
                self._data, self.addr = self.recvfrom(31)
                self.sendto(
                    bytes(f"{LOCAL_SERVER_LIST_ASE_MESSAGE} {self._port + 123}", "utf-8"), self.addr)
        except KeyboardInterrupt:
            ...
        except OSError as err:
            print(err)
            if 'Only one usage of each socket address' in err.strerror:
                self.logger.error('Server Address in use.')
                quit(-1)
