"""
    Join complete packet
"""

import os
import sys

_dir = __file__.split('\\')[:-4]
if _dir[0].endswith(':'): _dir[0] += '\\'
sys.path.insert(0, os.path.join(*_dir))

from network.packet_base import PacketBase

class JoinCompletePacket(PacketBase):
    def __init__(self, message: str, version: str) -> None:
        super().__init__()
        self._message = message
        self._version = version

    def build(self):
        self._builder.writeString(self._message)
        self._builder.writeString(self._version)

        return self._builder.build()
