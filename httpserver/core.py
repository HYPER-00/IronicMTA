"""
    HTTP Server Core
"""

import socket
from threading import Thread
from typing import Tuple, Literal

ADDRESS = Tuple[str, int]


class HTTPServer(socket.socket):
    """HTTP Server

    Args:
        server (Server): MTA Server Instance
    """

    def __init__(self, server):
        super().__init__(socket.AF_INET, socket.SOCK_STREAM)
        self._server = server
        self._logger = server.get_logger()
        self._settings = server.get_settings()
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.bind(("127.0.0.1", self._server.get_http_port()))
        self._resources = []
        self._http_client_files = []
        self._server.event.onResourceLoad(self.on_resourceload)

    def _parse_request(self, request):
        return request.split("\r\n")[0].split(" ")

    def _is_valid_request(self, protocol: str) -> bool:
        return str(protocol) == "HTTP/1.1"

    def _handle_request(self, connection: socket.socket, address: ADDRESS):
        try:
            request = connection.recv(1024).decode()
        except Exception:
            return False

        method, path, protocol = self._parse_request(request)
        path = path.replace("/", "\\")[1:]
        if not self._is_valid_request(protocol):
            return False

        if path != "favicon.ico":  # Browsers grabs the icon
            for _client_file in self._http_client_files:
                if _client_file[0] == path:
                    return self.send_response(connection, _client_file[1].get_buffer())

            self._logger.debug(
                f"Invalid url path for resource to download resource ({path})."
            )

    def _request_handler(self):
        while True:
            _conn, _addr = self.accept()
            thread = Thread(target=self._handle_request, args=(_conn, _addr))
            thread.start()

    def on_resourceload(self, resource):
        for _client_file in resource.get_client_files():
            self._http_client_files.append(
                (_client_file.getPathFromResource(resource), _client_file)
            )

    def start(self) -> bool:
        """Start HTTP Server

        Returns:
            bool: If server has been started
        """
        self.listen(self._settings["http_server"]["max_http_connections"])
        _request_handler_thread = Thread(
            target=self._request_handler, args=(), name="HTTP Server"
        )
        _request_handler_thread.start()
        return True

    def send_response(
        self,
        connection: socket.socket,
        message: str,
        status_code: int = 200,
        status_message: str = "OK",
        content_type: str = "text",
    ) -> Literal[True]:
        """Send Response

        Args:
            connection (socket.socket): Client connection
            message (str): Message to send
            status_code (int, optional): Response status code. Defaults to 200.
            status_message (str, optional): Response string message code. Defaults to "OK".
            content_type (str, optional): Response content type. Defaults to "text".

        Returns:
            Literal[True]: if all succded
        """
        response = (
            f"HTTP/1.1 {status_code} {status_message}\nContent-Type:{content_type}\n\n"
            + message
        )
        connection.send(response.encode())
        connection.close()
        return True
