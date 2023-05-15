"""
    Join Data packet
"""

import os
import sys

_dir = __file__.split('\\')[:-2]
if _dir[0].endswith(':'): _dir[0] += '\\'
sys.path.insert(0, os.path.join(*_dir))

from network.packet_base import PacketBase
from core.packet_handler.io import reader
from limits import MAX_PLAYER_NICK_LENGTH, MAX_SERIAL_LENGTH

from ctypes import c_ushort, c_char_p

class JoinDataPacket(PacketBase):
    """Join Data Packet"""
    def __init__(self) -> None:
        super().__init__()
        self._net_version = None
        self._mta_version = None
        self._bitstream_version = None
        self._player_version = None
        self._optional_update = None
        self._game_version = None
        self._nickname = None
        self._password = None
        self._serial = None


        
    def read(self, data: bytes):
        self._reader = reader.PacketReader(data)
        self._net_version = self._reader.getuint16()
        self._mta_version = self._reader.getuint16()
        self._bitstream_version = self._reader.getuint16()
        self._player_version = self._reader.getString()
        self._optional_update = self._reader.getBitFromData()
        self._game_version = self._reader.getByteFromData()
        self._nickname = self._reader.getStringChars(MAX_PLAYER_NICK_LENGTH)
        self._password = self._reader.getBytesFromData(16)
        self._serial = self._reader.getStringChars(MAX_SERIAL_LENGTH)


    def build(self):
        self._builder.write(c_ushort(self._net_version))
        self._builder.write(c_ushort(self._mta_version))
        self._builder.write(c_ushort(self._bitstream_version))
        self._builder.write(c_char_p())
