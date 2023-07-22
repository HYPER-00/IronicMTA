from .queries import QueryLight
from common import MASTER_SERVER_LIST_URL

import xmltodict
import requests


class MasterServerListAnnouncement:
    def __init__(self, server):
        self.logger = server.getLogger()
        self._server = server

        self._settings_manager = server.getSettingsManager()
        self._settings_manager.try2load()
        self.settings = self._settings_manager.get()

        self._ip, self._port = self._settings_manager.getServerAddr()
        self.version = '1.6.0-1.0'
        self.extra = '0_0_0_0_0'
        self.url = f'{MASTER_SERVER_LIST_URL}?g={self._port}&a={self._port + 123}&h={self._settings_manager.getHttpPort()}&v={self.version}&x={self.extra}&ip={self._ip}'

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
