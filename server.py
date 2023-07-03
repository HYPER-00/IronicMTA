"""
    Server class (SafeServer core)
"""

import time
from typing import List, Dict, Tuple
from brodcast import *
from player_manager import Player, ElementID, Client, Team
from settings_manager import SettingsManager
from core import *
from common import MAX_ASE_GAME_TYPE_LENGTH, MAX_ASE_MAP_NAME_LENGTH
from logger import Logger
from vectors import *
from limits import MAX_MAP_NAME_LENGTH, MAX_ASE_GAME_TYPE_LENGTH
from errors import (
    MaxMapNameLength,
    MaxGameTypeLength,
    ServerNotRunning,
)
from ctypes import c_byte, c_ulong, c_ushort, c_char_p, c_uint

class Server(object):
    def __init__(self, settings_file: str, logger: Logger, ase_version: AseVersion = AseVersion.v1_6n,
                build_type: BuildType = BuildType.release) -> None:
        self._logger = logger
        self._settings_manager = SettingsManager()
        self._settings_manager.setSettingsFilePath(settings_file)
        self._ase_version = ase_version
        self._build_type = build_type

        self._settings_manager.try2load()
        self._settings = self._settings_manager.get()

        self._netwrapper = NetWrapper(self._settings_manager.getServerAddr()[1])

        self._isrunning = False
        self._start_time = 0
        self._map_name = self._settings['mapname']
        self._game_type = self._settings['gametype']
        self._players: List[Player] = []

        self._brodcast_manager = BrodcastManager(self)

    def getSettingsManager(self) -> SettingsManager:
        return self._settings_manager
    
    def getAseVersion(self) -> AseVersion:
        return self._ase_version
    
    def getBuildType(self) -> BuildType:
        return self._build_type
    
    def getAddr(self) -> Tuple[str, int]:
        """
            Get Server Address\n
            [0] = IP\n
            [1] = Port\n
        """
        return self._settings_manager.getServerAddr()

    def isRunning(self) -> bool:
        """
            Check if server is running
        """
        return self._isrunning

    def getMapName(self) -> str:
        """
            Get server map name
        """
        return self._map_name[:MAX_MAP_NAME_LENGTH - 3] + "..."

    def getName(self) -> str | None:
        """
            Get Server name
        """
        return self._settings['servername']

    def getSettings(self) -> Dict[str, int | bool | str]:
        """
            Get server settings
        """
        return self._settings
    
    def isPassworded(self) -> bool:
        return str(self._settings['password']).strip() != ""
    
    def getPassword(self) -> str | None:
        if self.isPassworded():
            return self._settings['password']

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
                self._game = game_type
                assert self._game_type == game_type
            else:
                raise MaxGameTypeLength(
                    f'game type length ({len(game_type.strip())}) is gretter than max game type length ({MAX_ASE_GAME_TYPE_LENGTH})')

    def startLocalServerListAnnouncements(self):
        """
            Start server local annoucement\n
            Show server data in server list
        """
        self._logger.success('Local Server Announcements Started Successfuly!')
        self._brodcast_manager.startLocalServerListAnnouncements()

    def startServerBrodcast(self):
        """
            Start master server annoucement\n
            Show server in local server list
        """
        self._brodcast_manager.startLocalServerListAse()

    def startMasterServerAnnouncement(self):
        """
            Start master server annoucement\n
            Show server in server list
        """
        self._brodcast_manager.startMasterServerListAnnoucements()

    def startServerNetworking(self):
        """
            Start server networking
        """
        if not self._netwrapper.init(playercount=self.getPlayerCount() + 1,
                              servername=self.getName()):
            self._logger.error("Failed To Initialize Network Wrapper.")
        if self._netwrapper.start():
            self._logger.success("Server Network Has Been Started Successfuly!")
        else:
            self._logger.error("Failed To Start Server Network :(")
        return True

    def start(self):
        """
            Start Server\n
            Starts all services
        """
        self._isrunning = True
        self._start_time = time.time()
        self.startServerBrodcast()
        self.startLocalServerListAnnouncements()
        self.startMasterServerAnnouncement()

        self.startServerNetworking()
        _addr = self.getAddr()
        self._logger.success(f"Server Running On {_addr[0]}:{_addr[1]}")

    def send(
        self,
        packet_id: PacketID,
        playerbin_addr: int,
        bitstream_version: int,
        content: bytearray,
        priority: PacketPriority,
        reliability: PacketReliability,
    ):
        self._netwrapper.send(
            packet_id,
            playerbin_addr,
            bitstream_version,
            content,
            priority,
            reliability,
        )
        return True


    def getUptime(self) -> float | int:
        """
            Get server uptime
        """
        if self._isrunning:
            return time.time() - self._start_time
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
        
    def getMaxPlayers(self) -> int:
        """Get Server Max Players Can Be Joined"""
        return self._settings['maxplayers']
    
    def getGameType(self) -> str:
        return self._settings['gametype'][:MAX_ASE_GAME_TYPE_LENGTH - 3] + "..."
        
    def getLogger(self) -> Logger:
        """
            Get Server Logger
        """
        return self._logger
