from time import sleep
import socket
import os
from threading import Thread
from typing import Tuple, Literal

ADDRESS = Tuple[str, int]


class HTTPServer(socket.socket):
    def __init__(self, server):
        super().__init__(socket.AF_INET, socket.SOCK_STREAM)
        self._server = server
        self._logger = server.getLogger()
        self._settings = server.getSettings()
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.bind(("127.0.0.1", self._settings["http_server"]["http_port"]))
        self._http_client_files = []

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
        path = path.replace("/", "\\")[1:]
        if not self._is_valid_request(protocol):
            return False

        for _client_file in self._http_client_files:
            if _client_file[0] == path:
                return self.send_response(connection, _client_file[1].getBuffer())
            
        self._logger.debug(f"Invalid url path for resource to download resource ({path}).")

    def _request_handler(self):
        while True:
            _conn, _addr = self.accept()
            thread = Thread(target=self._handle_request, args=(_conn, _addr))
            thread.start()

    def _setup(self):
        self._resources = self._server.getAllResources()
        self._settings = self._server.getSettings()
        self._resource_cache_path = os.path.join(self._server.getBaseDirectory(),
                                                 self._settings["resources"]["resource_cache_folder"])
        if not os.path.isdir(self._resource_cache_path):
            os.mkdir(self._resource_cache_path)

        for _resource in self._resources:
            for _client_file in _resource.getClientFiles():
                self._http_client_files.append((_client_file.getPathFromResource(_resource),
                                                _client_file))

    def start(self):
        """Start HTTP Server"""
        self._setup()
        self.listen(self._settings["http_server"]["max_http_connections"])
        _request_handler_thread = Thread(
            target=self._request_handler, args=(), name="HTTP Server")
        _request_handler_thread.start()

    def send_response(
        self,
        connection: socket.socket,
        message: str,
        status_code: int = 200,
        status_message: str = "OK",
        content_type: str = "text"
    ) -> Literal[True] | None:

        response = f"HTTP/1.1 {status_code} {status_message}\nContent-Type:{content_type}\n\n" + message
        connection.send(response.encode())
        connection.close()
