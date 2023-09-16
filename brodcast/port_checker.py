import requests
from IronicMTA.common import PORT_TESTER_URL


class PortChecker(object):
    def __init__(self, server) -> None:
        self._logger = server.get_logger()
        self._ip, self._port = server.get_address()
        self._http_port = server.get_http_port()
        self._server = server

        self._activated_port = True
        self._activated_httpport = True

    def check(self):
        try:
            _response = requests.post(PORT_TESTER_URL, timeout=15, data={
                "d": self._ip,
                "g": self._port,
                "h": self._http_port,
                "button": "Submit",
                "nodef": 1,
                "a": 1,
                "mslist": 1
            })
        except:
            self._logger.error(
                "Couldn't Check server ports. Please check network")
            return
        if _response.status_code != 200 or not _response.ok:
            self._logger.warn("Port Testing Service Unavailable!")
            return False

        _response_data = _response.content.decode()

        if len(_response_data.strip()) == 0:
            self._logger.warn("Unexpected Response For Port Testing Service.")

        if f"Port {self._port} UDP is closed." in _response_data:
            self._activated_port = False
            self._logger.warn("Server Port is closed. Players Can't Join!")

        if f"Port {self._http_port} TCP is closed." in _response_data:
            self._activated_httpport = False
            self._logger.warn("Http Port is closed. Players Can't Download!")

        if self._activated_httpport and self._activated_port:
            self._logger.success("All Ports Works Successfuly!")

        self._server.event.call("onServerPortsCheck", self._server,
                                self._activated_port, self._activated_httpport)
        return True
