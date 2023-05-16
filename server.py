"""
    Server class (PyMTA core)
"""

import time
from threading import Thread
from typing import List, Dict
from brodcast import ase
from player_manager import Player
from settings_manager import SettingsManager
from core import wrapper
from logger import Logger
from limits import MAX_MAP_NAME_LENGTH, MAX_ASE_GAME_TYPE_LENGTH
from errors import (
    MaxMapNameLength,
    MaxGameTypeLength,
    ServerNotRunning,
)

class Server(object):
    def __init__(self, settings_file: str, logger: Logger) -> None:
        self._logger = logger
        self._settings_manager = SettingsManager()
        self._settings_manager.setSettingsFilePath(settings_file)

        if not self._settings_manager.isloaded:
            self._settings_manager.load()
        self._settings = self._settings_manager.get()

        self._netwrapper = wrapper.NetWrapper(self)

        self._isrunning = False
        self._start_time = 0
        self._map_name = self._settings['mapname'][:MAX_MAP_NAME_LENGTH - 3] + "..."
        self._players: List[Player]

        # Setup Threads
        # Ase
        self._ase = ase.LocalServerAnnouncement(self, self._logger)
        self._ase_thread = Thread(target=self._ase.start, args=())

        # Server Brodcast
        self._brodcast = ase.ServerBrodcast(self._logger, 
                                            port=self._settings_manager.getServerAddr()[1] + 123,
                                            server=self)
        self._brodcast_thread = Thread(target=self._brodcast.start, args=())

        self._master_announcer = ase.MasterServerAnnouncement(
            logger=self._logger,
            server_url='http://updatesa.mtasa.com/sa/master/',
            settings_manager=self._settings_manager,

        )

    def getSettingsManager(self) -> SettingsManager:
        return self._settings_manager

    def isRunning(self) -> bool:
        """
            Check if server is running
        """
        return self._isrunning

    def getMapName(self) -> str:
        """
            Get server map name
        """
        return self._map_name

    def getServerName(self) -> str | None:
        """
            Get Server name
        """
        return self._settings['servername']

    def getSettings(self) -> Dict[str, int | bool | str]:
        """
            Get server settings
        """
        return self._settings

    def setMapName(self, map_name: str):
        """
            Set server map name
        """
        if map_name and map_name.strip() != '':
            if len(map_name.strip()) <= MAX_MAP_NAME_LENGTH:
                self._map_name = map_name
                assert self._map_name == map_name
            else:
                raise MaxMapNameLength(
                    f'map name length ({len(map_name.strip())}) is gretter than max map name length ({MAX_MAP_NAME_LENGTH})')

    def setGameType(self, game_type: str):
        """
            Set server game type
        """
        if game_type and game_type.strip() != '':
            if len(game_type.strip()) <= MAX_ASE_GAME_TYPE_LENGTH:
                self._map_name = game_type
                assert self._map_name == game_type
            else:
                raise MaxGameTypeLength(
                    f'game type length ({len(game_type.strip())}) is gretter than max game type length ({MAX_ASE_GAME_TYPE_LENGTH})')

    def startLocalAnnouncement(self):
        """
            Start server local annoucement\n
            Show server in local server list
        """
        self._logger.success('Local Server Announcement Started Successfuly!')
        self._ase_thread.start()

    def startMasterServerAnnouncement(self):
        """
            Start master server annoucement\n
            Show server in server list
        """
        _is_announced = self._master_announcer.announce()
        if _is_announced:
            self._logger.success(
                'Announced on Master Server List Successfuly!')
        else:
            self._logger.error(
                'Failed To Announce Server on Master Server List!')

    def startServerBrodcast(self):
        """
            Start master server annoucement\n
            Show server data in server list
        """
        self._logger.success('Server Brodcast Started Successfuly!')
        self._brodcast_thread.start()

    def startServerNetworking(self):
        """
            Start server networking
        """
        self._netwrapper.init(playercount=self.getPlayerCount(),
                              servername=self.getServerName())
        self._netwrapper.start()

    def start(self):
        """
            Start Server\n
            Starts all services
        """
        self._isrunning = True
        self._start_time = time.time()
        self.startLocalAnnouncement()
        self.startServerBrodcast()
        self.startMasterServerAnnouncement()
        self.startServerNetworking()

    def getUptime(self) -> float | int:
        """
            Get server uptime
        """
        if self._isrunning:
            return time.time() - self.start_time
        else:
            raise ServerNotRunning('Server is not working!!')

    def getAllPlayers(self) -> List[Player]:
        """
            Get all server players
        """
        return self._players

    def getPlayerCount(self) -> int:
        """
            Get server player count
        """
        try:
            return len(self._players)
        except AttributeError:
            return 0

