"""
    IronicMTA
    ~~~~~~~~~~

    An MTA:SA Server Written in python.
    :license: MIT, see LICENSE for more details.
"""

__title__ = "IronicMTA"
__author__ = "IronicMTA Developers & Hyper"
__license__ = "MIT"
__copyright__ = "Copyright 2022-2023 Hyper & 2021-present IronicMTA Developers"
__version__ = "0.1 Alpha"

from .interiors import InteriorIDs
from .object_manager import *
from .player_manager import Player
from .logger import Logger
from .server import Server

from .common import (
    HttpDownloadTypes,
    PacketTypes,
    AseVersion,
    BuildType,
    QueryTypes,
    PlayerDisconnectedTypes,
    LOCAL_SERVER_LIST_ASE_PORT,
    MASTER_SERVER_LIST_URL,
    PORT_TESTER_URL,
)

from .vectors import Vector2, Vector3
from .errors import (
    MaxMapNameLength,
    MaxGameTypeLength,
    MySQLUnkownError,
    MySQLConnectionDetected,
    SQLQueryUnkownConditionType,
    MySQLNoConnection,
    SQLite3NullPath,
    SQLite3ConnectionDetected,
    SQLite3NoConnection,
    SQLite3UnkownError,
    SettingsLoadingError,
    SettingsFileError,
    InvalidPortNumber,
    ServerNotRunning,
    ServerNetworkingError,
    ServerPasswordError,
    NetworkWrapperInitError,
    NetworkWrapperError,
    ResourceFileError,
    BitStreamError,
    EventHandlerError,
)
from .brodcast import BrodcastManager, PortChecker
from .httpserver import HTTPServer
from .resources import Resource, ResourceFile, ResourceInfo, ResourceLoader
from .event import ServerEventHandler
from .core import NetworkWrapper, BitStream, PacketID, PacketPriority, PacketReliability

from .network.packets import (
    Packet_PlayerJoinModName,
    Packet_PlayerJoinData,
    Packet_PlayerConnectComplete,
    Packet_PlayerDisconnected,
    Packet_AntiCheatTransgression,
)

from .settings import SettingsManager
from .limits import *
from .client_manager import Client
