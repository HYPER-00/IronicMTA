"""
    Join complete packet
"""

import os
import sys

_dir = __file__.split('\\')[:-4]
if _dir[0].endswith(':'): _dir[0] += '\\'
sys.path.insert(0, os.path.join(*_dir))

from object_manager import ElementID
from network.packet_base import PacketBase
from player_manager import Player
from core.packet_handler.io.reader import PacketReader

from ctypes import c_ushort

class SpawnPlayerPacket(PacketBase):
    def __init__(self, player: Player) -> None:
        super().__init__()

        self._player_id = player.getID()
        self._spawn_flags = bytes()
        self._position = player.getPosition()
        self._rotation = bytes()
        self._skin = player.getSkin()
        self._interior = player.getInterior()
        self._dimension = player.getDimension()
        self._teamid = 0 # TODO
        self._time_context = bytes(0)

    def read(self, data: bytearray):
        _reader = PacketReader(data)
        self._player_id = _reader.getElementID()
        self._spawn_flags = _reader.getByteFromData()
        self._position = _reader.getVector3()
        self._rotation = _reader.getBytesFromData(4)
        self._skin = _reader.getuint16()
        self._interior = _reader.getByteFromData()
        self._dimension = _reader.getuint16()
        self._teamid = _reader.getElementID()
        self._time_context = _reader.getByteFromData()

    def build(self):
        self._builder.writeElementID(ElementID(self._player_id))
        self._builder.writeBytes(bytearray(self._spawn_flags))
        self._builder.writeVector3(bytearray(self._position))
        self._builder.writeBytes(bytes(self._rotation))
        self._builder.writeBytes(bytes(c_ushort(self._skin)))
        self._builder.writeBytes(bytes(self._interior))
        self._builder.writeBytes(bytes(c_ushort(self._dimension)))
        self._builder.writeElementID(self._teamid)
        self._builder.writeBytes(bytes(self._time_context))

        return self._builder.build()
        
