import socket
from threading import Thread
from typing import Tuple, Literal

ADDRESS = Tuple[str, int]


class HTTPServer(socket.socket):
    def __init__(self, server):
        super().__init__(socket.AF_INET, socket.SOCK_STREAM)
        self._logger = server.getLogger()
        self._settings = server.getSettings()
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.bind(("127.0.0.1", 8000))

    def _parse_request(self, request):
        return request.split("\r\n")[0].split(" ")

    def _is_valid_request(self, protocol: str) -> bool:
        return str(protocol) == "HTTP/1.1"

    def _handle_request(self, connection: socket.socket, address: ADDRESS):
        try:
            request = connection.recv(1024).decode()
        except:
            return False

        method, path, protocol = self._parse_request(request)
        if not self._is_valid_request(protocol):
            return False

        self.send_response(connection, "<h1>Works!</h1>")

    def _request_handler(self):
        while True:
            _conn, _addr = self.accept()
            thread = Thread(target=self._handle_request, args=(_conn, _addr))
            thread.start()

    def start(self):
        """Start HTTP Server"""
        self.listen(self._settings["http_server"]["max_http_connections"])
        _request_handler_thread = Thread(target=self._request_handler, args=(), name="HTTP Server")
        _request_handler_thread.start()

    def send_response(self, connection: socket.socket,
                      message: str,
                      status_code: int = 200,
                      status_message: str = "OK") -> Literal[True] | None:
        response = f"HTTP/1.1 {status_code} {status_message}\nContent-Type: text/html\n\n" + message
        connection.send(response.encode())
        connection.close()
