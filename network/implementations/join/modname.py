"""
    Join Mod Name packet
"""

import os
import sys

_dir = __file__.split('\\')[:-2]
if _dir[0].endswith(':'): _dir[0] += '\\'
sys.path.insert(0, os.path.join(*_dir))

from object_manager import ElementID
from network.packet_base import PacketBase

from ctypes import (
    c_int,
    c_char,
    c_char_p,
    c_uint,
    c_bool,
    c_ushort
)

class ModNamePacket(PacketBase):
    def __init__(self, net_version: int, name: str) -> None:
        self._netversion = c_ushort(net_version)
        self._name = name

    def build(self):
        self._builder.writeBytes(bytearray(c_ushort(self._netversion)))
        self._builder.writeString(self._name)

        return self._builder.build()
