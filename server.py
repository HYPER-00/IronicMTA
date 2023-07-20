"""
    Server class (SafeMTA core)
"""

import time
from os.path import isfile, isdir, join
from typing import List, Dict, Tuple
from brodcast import *
from player_manager import Player
from settings_manager import SettingsManager
from core import NetworkWrapper, PacketID, PacketPriority, PacketReliability
from httpserver import HTTPServer
from logger import Logger
from vectors import *
from limits import MAX_MAP_NAME_LENGTH, MAX_ASE_GAME_TYPE_LENGTH
from resources import ResourceLoader, Resource
from errors import (
    MaxMapNameLength,
    MaxGameTypeLength,
    ServerNotRunning,
)


class Server(object):
    def __init__(
        self,
        main_file: str,
        settings_file: str,
        ase_version: AseVersion = AseVersion.v1_6,
        build_type: BuildType = BuildType.RELEASE,
    ) -> None:
        _dir = main_file.split('\\')[:-1]
        if _dir[0].endswith(':'):
            _dir[0] += '\\'
        self._server_base_dir = join(*_dir)

        self._settings_manager = SettingsManager()
        self._intialized = False

        if not isfile(settings_file) and not isdir(settings_file):
            print(settings_file)
            with open(settings_file, "w") as file:
                file.write("{}")
        self._settings_manager.setSettingsFilePath(settings_file)
        self._ase_version = ase_version
        self._build_type = build_type

        self._settings_manager.try2load()
        self._settings = self._settings_manager.get()
        with open(self._settings["log_file"], "a") as file:
            file.write("")

        self._logger = Logger(self._settings["log_file"])


        self._netwrapper = NetworkWrapper(self)

        self._isrunning = False
        self._start_time = 0
        self._map_name = self._settings["server"]["map_name"]
        self._game_type = self._settings["server"]["game_type"]
        self._players: List[Player] = []

        self._port_checker = PortChecker(self)
        self._brodcast_manager = BrodcastManager(self)
        self._http_server = HTTPServer(self)
        self._resource_loader = ResourceLoader(self)

        self._intialized = True

    def getBaseDirectory(self) -> str:
        """Get Server Running Directory"""
        return self._server_base_dir

    def getSettingsManager(self) -> SettingsManager:
        """
            Get Server Settings Manager
            *  Get Access for editing/get settings
        """
        return self._settings_manager

    def getSettings(self) -> Dict[str, int | bool | str]:
        """
            Get server settings
        """
        return self._settings

    def getAseVersion(self) -> AseVersion:
        """
            Get Server Ase Version (1.6 | 1.6n)
        """
        return self._ase_version

    def getBuildType(self) -> BuildType:
        """
            Get Server Build Type (Release, Custom, Unstable, Untested)
        """
        return self._build_type

    def getServerFileIDPath(self) -> str:
        """
            Get Server File ID Path
        """
        return self._settings["server_id_file"]

    def getAddress(self) -> Tuple[str, int]:
        """
            Get Server Address\n
            [0] = IP\n
            [1] = Port\n
        """
        return self._settings_manager.getServerAddr()

    def getHttpPort(self) -> int:
        """
            Get Server Http Port
        """
        return self._settings_manager.getHttpPort()

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
        return self._settings["server"]["name"]

    def isPassworded(self) -> bool:
        """
            Check If Server Passworded
        """
        return str(self._settings["server"]["password"]).strip() != ""

    def getPassword(self) -> str | None:
        """
            Get Server Password\n
            * If no The Server Haven't a Password it returns None
        """
        if self.isPassworded():
            return self._settings["server"]["password"]

    def setMapName(self, map_name: str):
        """
            Set server map name
        """
        if map_name and map_name.strip() != "":
            if len(map_name.strip()) <= MAX_MAP_NAME_LENGTH:
                self._map_name = map_name
                assert self._map_name == map_name
            else:
                raise MaxMapNameLength(
                    f"map name length ({len(map_name.strip())}) is gretter than max map name length ({MAX_MAP_NAME_LENGTH})")

    def setGameType(self, game_type: str):
        """
            Set server game type
        """
        if game_type and game_type.strip() != "":
            if len(game_type.strip()) <= MAX_ASE_GAME_TYPE_LENGTH:
                self._game = game_type
                assert self._game_type == game_type
            else:
                raise MaxGameTypeLength(
                    f"game type length ({len(game_type.strip())}) is gretter than max game type length ({MAX_ASE_GAME_TYPE_LENGTH})")

    def checkPorts(self):
        """
            Check Server Ports (Socket Port, Http Port)
        """
        self._port_checker.check()

    def startLocalServerListAnnouncements(self):
        """
            Start server local annoucement\n
            Show server data in server list
        """
        self._logger.success("Local Server Announcements Started Successfuly!")
        self._brodcast_manager.startLocalServerListAnnouncements()

    def startServerBrodcast(self):
        """
            Start master server annoucement\n
            Show server in local server list
        """
        self._brodcast_manager.startLocalServerListAse()

    def startHTTPServer(self):
        """
            Start Http Server\n
            Serve resources, handle apis, ...
        """
        self._http_server.start()
        self._logger.success("HTTP Server Has Been Started Successfuly on "
                             f"({self._settings_manager.getServerAddr()[0]}:{self._settings_manager.getHttpPort()}) "
                             f"With {self._settings['http_server']['max_http_connections']} as max http connections")

    def startMasterServerAnnouncement(self):
        """
            Start master server annoucement\n
            Show server in server list
        """
        self._brodcast_manager.startMasterServerListAnnoucements()

    def startResourceLoading(self):
        """Start Server Resources Loading"""
        self._resource_loader.start_loading()

    def startServerNetworking(self):
        """
            Start server networking
        """
        if not self._netwrapper.init():
            self._logger.error("Failed To Initialize Network Wrapper.")
        if self._netwrapper.start():
            self._logger.success(
                "Server Network Has Been Started Successfuly!")
        else:
            self._logger.error("Failed To Start Server Network :(")
        return True

    def startPacketListening(self):
        """
            Start Server Packet Listening
            * Receive All the packets esnt by the client
        """
        return self._netwrapper.startListening()

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
        self.startHTTPServer()
        if self._settings["check_ports_before_start"]:
            self.checkPorts()
        self.startServerNetworking()
        self.startResourceLoading()

        self.startPacketListening()

        _addr = self.getAddress()
        self._logger.success(f"Server Running On {_addr[0]}:{_addr[1]}")

    def getNetwork(self) -> NetworkWrapper:
        """
            Get Server Network
            - (Send Packets, ...)
        """
        return self._netwrapper

    def getUptime(self) -> float | int:
        """
            Get server uptime (Running Time)
        """
        if self._isrunning:
            return time.time() - self._start_time
        else:
            raise ServerNotRunning("Server is not working!!")

    def getAllPlayers(self) -> List[Player]:
        """
            Get all server joined players
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
        return self._settings["server"]["max_players"]

    def getGameType(self) -> str:
        return self._settings["server"]["game_type"][:MAX_ASE_GAME_TYPE_LENGTH - 3] + "..."

    def getLogger(self) -> Logger:
        """
            Get Server Logger
        """
        return self._logger

    def getAllResources(self) -> List[Resource]:
        """
            Get all server resources (running/stoped)\n
            ReturnType: Resource (object)
        """
        return self._resource_loader.get_all_resources()

    def getTotalResourcesCount(self) -> int:
        """Get Total Resources Count (running/stoped)"""
        return len(self._resource_loader.get_all_resources())

    def getAllResourcesNames(self) -> List[str]:
        """Get All resources names (running/stoped)"""
        _resources_names = []
        for _resource in self._resource_loader.get_all_resources():
            _resources_names.append(_resource.getName())
        return _resources_names
