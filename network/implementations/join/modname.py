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

class ModNamePacket(PacketBase):
    def __init__(self, net_version: int, name: str) -> None:
        self._netversion = net_version
        self._name = name

    def build(self):
        self.bitstream.write_ushort(self._netversion)
        self.bitstream.write_string(self._name)

        return self.bitstream.get_bytes()
