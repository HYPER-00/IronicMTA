"""
    Join complete packet
"""

import os
import sys

_dir = __file__.split('\\')[:-2]
if _dir[0].endswith(':'): _dir[0] += '\\'
sys.path.insert(0, os.path.join(*_dir))

from object_manager import ElementID
from limits import MAX_HTTP_DOWNLOAD_URL
from core.packet_handler.io import builder
from common import HttpDownloadTypes

from ctypes import (
    c_int,
    c_char,
    c_char_p,
    c_uint,
    c_bool,
    c_ushort
)

class JoinCompletePacket(object):
    def __init__(
        self,
        player_id: ElementID,
        root_id: ElementID,
        http_download_type: int,
        http_download_port: int,
        http_download_url: str,
        max_connections_per_client: int,
        enable_client_checks: int,
        voice_enables: bool,
        sample_rate: str,
        voice_quality: int,
        bit_rate: int = 2400,
        fakelag: bool = False,
    ) -> None:
        self._httptypes = HttpDownloadTypes()
        
        self._player_id = player_id
        self._root_id = root_id
        self._http_download_type = http_download_type
        self._http_download_port = http_download_port
        self._http_download_url = http_download_url[:MAX_HTTP_DOWNLOAD_URL]
        self._max_connections_per_client = max_connections_per_client
        self._enable_client_checks = enable_client_checks
        self._isfakelag_enabled = fakelag
        self._voice_enabled = voice_enables
        self._sample_rate = sample_rate
        self._voice_quality = voice_quality
        self._bit_rate = bit_rate

    def build(self):
        _builder = builder.PacketBuilder()
        
        _players_count = 1 # Non zero single byte
        _builder.write(c_char(_players_count))
        _builder.write(self._root_id.value)

        _builder.write(c_int(self._enable_client_checks))
        _builder.write(c_bool(self._voice_enabled))
        _builder.writeBytesCapped(self._sample_rate, 2)
        _builder.writeByteCapped(self._voice_quality, 4)
        _builder.writeCompressed(bytearray(c_uint(self._bit_rate)), True)

        _builder.writeBit(self._isfakelag_enabled)
        _builder.writeBytes(bytearray(self._max_connections_per_client))
        _builder.writeBytes(bytearray(self._http_download_type))

        if self._http_download_type == self._httptypes.HTTP_DOWNLOAD_ENABLED_PORT:
            _builder.writeBytes(c_ushort(self._http_download_port))
        elif self._http_download_type == self._httptypes.HTTP_DOWNLOAD_ENABLED_URL:
            _builder.writeBytes(bytearray(c_ushort(self._http_download_port)))
            _builder.writeBytes(bytearray(c_ushort(self._http_download_url)))

        return _builder.build()
