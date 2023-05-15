import os
import sys

_dir = __file__.split('\\')[:-2]
if _dir[0].endswith(':'): _dir[0] += '\\'
sys.path.insert(0, os.path.join(*_dir))

from core.packet_handler.io import builder, reader

class PacketBase(object):
    """Packet base"""
    def __init__(self) -> None:
        self._builder = builder.PacketBuilder()

    def build(self):
        return self._builder.build()
    def read(self):
        return ...
