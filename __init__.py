"""
    MTA:SA Server Written in Python
    ~~~~~~~~~~~~~~~~~~~

    A basic wrapper for the Discord API.
    :license: MIT, see LICENSE for more details.
"""

__title__ = "IronicMTA"
__author__ = "IronicMTA Developers & Hyper"
__license__ = "MIT"
__copyright__ = "Copyright 2022-2023 Hyoer & 2021-present IronicMTA Developers"
__version__ = "0.1 Alpha"

from .interiors import InteriorIDs
from .object_manager import *
from .player_manager import Player
from .logger import Logger
from .server import Server
from .vectors import Vector2, Vector3
from .errors import *
from .brodcast import AseVersion, BrodcastManager, BuildType, PortChecker
from .httpserver import HTTPServer
from .resources import Resource, ResourceFile, ResourceInfo, ResourceLoader
from .event_manager import ServerEventHandler
from .core import NetworkWrapper, BitStream, PacketID, PacketPriority, PacketReliability
from .network.packets import *
from .settings_manager import SettingsManager
from .limits import *
from.client_manager import Client
