"""
    Join complete packet
"""

from object_manager import ElementID
from limits import MAX_HTTP_DOWNLOAD_URL
from common import HttpDownloadTypes
from network.packet_base import PacketBase

from ctypes import (
    c_int,
    c_char,
    c_char_p,
    c_uint,
    c_bool,
    c_ushort
)


class Packet_PlayerJoinComplete(PacketBase):
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

        _players_count = 1  # Non zero single byte
        self.bitstream.write(self._root_id.value)

        self.bitstream.write(c_int(self._enable_client_checks))
        self.bitstream.write(c_bool(self._voice_enabled))
        self.bitstream.writeBytesCapped(self._sample_rate, 2)
        self.bitstream.writeByteCapped(self._voice_quality, 4)
        self.bitstream.writeCompressed(bytearray(c_uint(self._bit_rate)), True)

        self.bitstream.writeBit(self._isfakelag_enabled)
        self.bitstream.writeBytes(bytearray(self._max_connections_per_client))
        self.bitstream.writeBytes(bytearray(self._http_download_type))

        if self._http_download_type == self._httptypes.HTTP_DOWNLOAD_ENABLED_PORT:
            self.bitstream.writeBytes(c_ushort(self._http_download_port))
        elif self._http_download_type == self._httptypes.HTTP_DOWNLOAD_ENABLED_URL:
            self.bitstream.writeBytes(
                bytearray(c_ushort(self._http_download_port)))
            self.bitstream.writeBytes(
                bytearray(c_ushort(self._http_download_url)))

        return self.bitstream.build()
