from IronicMTA.brodcast.queries import QueryLight
from IronicMTA.common import MASTER_SERVER_LIST_URL

import xmltodict
import requests


class MasterServerListAnnouncement:
    def __init__(self, server):
        self.logger = server.get_logger()
        self._server = server
        self.settings = server.get_settings()
        self._ip, self._port = server.get_address()
        self.version = self.settings["version"]["recommendedclientversion"]
        self.extra = f'{server.get_max_players()}_{int(server.is_passworded())}_0_0_0'
        self.url = f'{MASTER_SERVER_LIST_URL}?g={self._port}&a={self._port + 123}&h={server.get_http_port()}&v={self.version}&x={self.extra}&ip={self._ip}'

    def start(self):
        self._data = QueryLight(self._server)
        try:
            self._response = requests.post(self.url, bytes(
                str(self._data), encoding='utf-8'), timeout=8)
            self._server.event.call("onMasterServerAnnounce", self._server)
        except:
            self.logger.error(
                "Couldn't Announce Server To Master Server List. check network")
            return {}
        self.logger.success(
            "Server Announced on Master Server List Successfuly.")
        return xmltodict.parse(self._response.text)
        # TODO Add a timer
