"""
    MTASA net.dll wrapper
"""
import os
import sys
from platform import architecture
from typing import Literal, Any, Tuple, Union
from ctypes import (
    cdll,
    PyDLL,
    py_object,
    c_char_p,
    c_ushort,
    c_short,
    c_int,
    c_float,
    c_uint,
    c_ulong,
    c_bool,
    c_longlong,
    windll,
    Structure,
    WinError,
    POINTER,
    c_ubyte,
)
import colorama


from IronicMTA.core.packet_ids import PacketPriority, PacketReliability
from IronicMTA.errors import NetworkWrapperInitError, NetworkWrapperError
from IronicMTA.core.packet_handler import PacketHandler
from IronicMTA.common import BuildType


kernel32 = windll.kernel32

colorama.init(autoreset=True)


def _log_err(err: str) -> None:
    print(f"{colorama.Fore.RED}[Net-Wrapper ERROR] {err}.")


class ThreadCPUTimes(Structure):
    """Server Thread statistics"""

    _fields_ = [
        ("uiProcessorNumber", c_uint),
        ("fUserPercent", c_float),
        ("fKernelPercent", c_float),
        ("fTotalCPUPercent", c_float),
        ("fUserPercentAvg", c_float),
        ("fKernelPercentAvg", c_float),
        ("fTotalCPUPercentAvg", c_float),
    ]


class BandwidthStatistics(Structure):
    """Server Network Bandwidth statistics"""

    _fields_ = [
        ("llOutgoingUDPByteCount", c_longlong),
        ("llIncomingUDPByteCount", c_longlong),
        ("llIncomingUDPByteCountBlocked", c_longlong),
        ("llOutgoingUDPPacketCount", c_longlong),
        ("llIncomingUDPPacketCount", c_longlong),
        ("llIncomingUDPPacketCountBlocked", c_longlong),
        ("llOutgoingUDPByteResentCount", c_longlong),
        ("llOutgoingUDPMessageResentCount", c_longlong),
        ("threadCPUTimes", ThreadCPUTimes),
    ]


class SPacketStat(Structure):
    """Client Packets Stats"""

    _fields_ = [("iCount", c_int), ("iTotalBytes", c_int), ("totalTime", c_ulong)]


class PlayerAddress(Structure):
    """Client Address (Ip, Port)"""

    _fields_ = [("szIP", c_char_p), ("usPort", c_ushort)]


MTA_DM_SERVER_NET_MODULE_VERSION = 0x0AB


class NetworkWrapper(object):
    """MTA:SA net.dll wrapper

    Args:
    -----
        server (Server): IronicMTA Server
    """

    def __init__(self, server) -> None:
        self._ip, self._port = server.get_address()
        self._server = server

        self.__id = c_ushort(0)

        if server.get_build_type() != BuildType.RELEASE:
            _log_err("IronicMTA Server does not support network debug dlls")
            sys.exit()

        _dir = __file__.split("\\")[:-2]
        if _dir[0].endswith(":"):
            _dir[0] += "\\"
        _basedir = os.path.join(*_dir)

        self.netpath = f"{_basedir}\\core\\lib\\{'release' if server.get_build_type() == BuildType.RELEASE else 'debug'}\\net{'' if server.get_build_type() == BuildType.RELEASE else '_d'}.dll"
        self.wrapperpath = (
            f"{_basedir}\\core\\lib\\wrapper\\wrapper.x{architecture()[0][:2]}.dll"
        )

        self._initialized = False

        try:
            self._netlib = cdll.LoadLibrary(self.netpath)
        except OSError as err:
            _log_err("Cannot Open network dll:")
            _log_err(err.strerror)

        iscompatible = self._netlib.CheckCompatibility(
            MTA_DM_SERVER_NET_MODULE_VERSION, c_ulong(BuildType.UNSTABLE.value)
        )

        if not self._netlib.CheckCompatibility and iscompatible:
            _log_err(
                """
            Network module not compatible!
            If this is a custom build, try to:
                1. Update net.dll
                3. Check Server version type
            """
            )
            sys.exit(-1)

        try:
            self._wrapperdll = PyDLL(self.wrapperpath)
        except OSError as err:
            _log_err("Cannot open wrapper dll:")
            _log_err(err.strerror)

    def init(self) -> bool:
        """Init Network wrapper

        Returns:
        --------
            bool: True If the server has been started successfuly
        """
        if self._wrapperdll.Setup:
            _func = self._wrapperdll.Setup
            _func.restype = c_short
            _func.argtypes = [
                c_char_p,
                c_char_p,
                c_char_p,
                c_ushort,
                c_uint,
                c_char_p,
                POINTER(c_ulong),
            ]

            _result = _func(
                c_char_p(self._b(self._server.get_file_id_path())),
                c_char_p(self._b(self.netpath)),
                c_char_p(bytes(self._ip, encoding="utf-8")),
                c_ushort(self._port),
                c_uint(self._server.get_player_count() + 1),
                c_char_p(self._b(self._server.get_name())),
                c_ulong(self._server.get_build_type().value),
            )

            if _result < 0:
                _log_err(f"Unable to init network wrapper. ({_result})")
                return False
            self._initialized = True
            self.__id = c_ushort(_result)
            return True
        return False

    def start_listening(self) -> Literal[True]:
        """Start Server packet listening

        Returns:
        --------
            Literal[True]: True if all succeded
        """
        _packet_handler = PacketHandler(self._server)

        _func = self._wrapperdll.GetLastPackets
        _func.argtypes = [c_ushort]
        _func.restype = py_object
        if _func:
            while True:
                _packet = _func(self.__id)
                _packet_handler.onrecive(
                    packet=_packet[0],
                    player=_packet[1],
                    packet_index=_packet[2],
                    packet_content=_packet[3],
                )
        return True

    def destroy(self) -> Literal[True]:
        """Destroy network

        Returns:
        --------
            Literal[True]: True if network has been destroyed successfuly
        """
        self._wrapperdll.Destroy(self.__id)
        return True

    def start(self) -> Literal[True]:
        """Start Network Wrapper

        Raises:
        -------
            NetWrapperInitError: If network wrapper not initialized

        Returns:
        --------
            Literal[True]: True if network has been started successfuly
        """
        if not self._initialized:
            raise NetworkWrapperInitError(
                "Network wrapper is not initialized. try to init()"
            )

        if self._wrapperdll.Start:
            try:
                self._wrapperdll.Start(self.__id)
            except Exception:
                _log_err("Coudldn't Start Net Wrapper")
                _log_err(WinError(kernel32.GetLastError()).strerror)
        return True

    def stop(self) -> Literal[True]:
        """Stop network wrapper

        Returns:
        --------
            Literal[True]: True if network has benn stoped successfuly
        """
        self._wrapperdll.Stop(self.__id)
        return True

    def send(
        self,
        player_binaddr: int,
        packet_id: int,
        bitstream_version: int,
        data: bytes,
        reliability: PacketReliability = PacketReliability.RELIABLE,
        priority: PacketPriority = PacketPriority.HIGH,
    ) -> Literal[True]:
        """Send Client packet

        Args:
        -----
            player_binaddr (int): Client Player Binary Address
            packet_id (int): Packet ID
            bitstream_version (int): BitStream Version
            data (bytes): Sequence of bytes represents the data to send
            reliability (PacketReliability, optional): Packet reliability.
            Defaults to PacketReliability.RELIABLE.
            priority (PacketPriority, optional): Packet Priority. Defaults to PacketPriority.HIGH.

        Returns:
        --------
            Literal[True]: if packet has been sent successfuly (without errors)
        """
        _func = self._wrapperdll.Send
        _func.argtypes = [
            c_ushort,
            c_ulong,
            c_uint,
            c_ushort,
            c_char_p,
            c_ulong,
            c_ubyte,
            c_ubyte,
        ]
        _func(
            self.__id,
            c_ulong(player_binaddr),
            c_uint(packet_id),
            c_ushort(bitstream_version),
            data,
            c_ulong(len(data)),
            c_ubyte(priority.value),
            c_ubyte(reliability.value),
        )
        return True

    def is_valid_socket(self, player_binaddr: int) -> bool:
        """Check if socket is valid

        Args:
        -----
            player_binaddr (int): The Client Player Binary Address

        Returns:
        --------
            bool: True if is valid socket else False
        """
        _func = self._wrapperdll.IsValidSocket
        _func.argtypes = [c_ushort, c_ulong]
        _func.restype = c_bool
        return bool(_func(self.__id, c_ulong(player_binaddr)))  # Convert c_bool to bool

    def set_client_bitstream_version(
        self, client_binaddr: int, version: int
    ) -> Literal[True]:
        """Set BitStream Version

        Args:
        -----
            client_binaddr (int): Client player binary address
            version (int): bitstream version

        Returns:
        --------
            Literal[True]: Set client bitstream version
        """
        self._wrapperdll.SetClientBitStreamVersion(self.__id, client_binaddr, version)
        return True

    def get_player_address(self, player_binaddr: int) -> Tuple[str, int]:
        """Get Player Address (Ip, Port)

        Args:
        -----
            player_binaddr (int): Client player binary Address

        Raises:
        -------
            NetworkWrapperError: Invalid Client player binary address

        Returns:
        --------
            Tuple[str, int]: Tuple of Client Player address (IP, Port)
        """
        _func = self._wrapperdll.GetPlayerAddress
        _func.argtypes = [c_ushort, c_ulong]
        _func.restype = PlayerAddress
        _address = _func(self.__id, c_ulong(player_binaddr))
        if _address.usPort == 0:
            raise NetworkWrapperError("Invalid Player Binary Address")
        return _address.strIP, _address.usPort

    def get_client_data(
        self, player_binaddr: int, serial: str, extra: str, version: str
    ) -> Any:
        """Get Client Data (Serial, Extra, Version)

        Args:
        -----
            player_binaddr (int): Client player binary address
            serial (str): Serial variable to store-in serial
            extra (str): Extra Variable to store-in extra
            version (str): Version Variable to store-in version

        Returns:
        --------
            Any
        """
        return self._wrapperdll.GetClientData(
            self.__id,
            c_ulong(player_binaddr),
            c_char_p(self._b(serial)),
            c_char_p(self._b(extra)),
            c_char_p(self._b(version)),
        )

    def set_anticheat_checks(
        self,
        disable_combo_ac_map: str,
        disable_ac_map: str,
        enable_sd_map: str,
        enable_client_checks: int,
        hide_ac: bool,
        img_mods: str,
    ) -> Literal[True]:
        """Set anticheat Checks/Configurations

        Args:
        -----
            disable_combo_ac_map (str): combo ac map
            disable_ac_map (str): ac map
            enable_sd_map (str): sd map
            enable_client_checks (int): client checks
            hide_ac (bool): Hide anticheat
            img_mods (str): img mods

        Returns:
        --------
            Literal[True]: True if anticheat settings applied successfuly
        """
        self._wrapperdll.SetAntiCheatChecks(
            self.__id,
            c_char_p(self._b(disable_combo_ac_map)),
            c_char_p(self._b(disable_ac_map)),
            c_char_p(self._b(enable_sd_map)),
            c_int(enable_client_checks),
            c_bool(hide_ac),
            c_char_p(self._b(img_mods)),
        )
        return True

    def get_mod_packets(self, player_binaddr: int) -> Literal[True]:
        """Get Mod packets

        Args:
        -----
            player_binaddr (int): Client player binary address

        Returns:
        --------
            Literal[True]: True if mod packets has been resent
        """
        self._wrapperdll.GetModPackets(self.__id, c_ulong(player_binaddr))
        return True

    def resend_anticheat_info(self, player_binaddr: int) -> Literal[True]:
        """Resend anticheat info to specefic player

        Args:
        -----
            player_binaddr (int): Client player binary address

        Returns:
        --------
            Literal[True]: All succeded
        """
        self._wrapperdll.GetAntiCheatInfo(self.__id, c_ulong(player_binaddr))
        return True

    def get_net_route(self) -> Union[bytes, Literal[False]]:
        """Get Network route

        Returns:
        --------
            bytes: Network route
        """
        _func = self._wrapperdll.GetNetRoute
        if self._server.is_running():
            if _func:
                _func.argtypes = [c_ushort]
                _func.restype = c_char_p
                return _func(self.__id)
        return False

    def get_bandwidth_statistics(self) -> Literal[False] | BandwidthStatistics:
        """Get Bandwidth statistics

        Returns:
        --------
            BandwidthStatistics: Bandwidth statistics
        """
        _func = self._wrapperdll.GetBandwidthStatistics
        if _func:
            if self._server.is_running():
                _func.argtypes = [c_ushort]
                _func.restype = BandwidthStatistics
                return _func(self.__id)
        return False

    def get_packets_stats(self) -> Union[bool, SPacketStat]:
        """Get Packets stats

        Returns:
        --------
            SPacketStat: Packets stats
        """
        _func = self._wrapperdll.GetPacketStat
        if _func:
            if self._server.is_running():
                _func.argtypes = [c_ushort]
                _func.restype = SPacketStat
                return _func(self.__id)
        return False

    def get_ping_status(self) -> Union[bool, bytes]:
        """Get Ping status

        Returns:
        --------
            bytes: Ping status
        """
        _func = self._wrapperdll.GetPingStatus
        if _func:
            if self._server.is_running():
                _func.argtypes = [c_ushort]
                _func.restype = c_char_p
                return _func(self.__id)
        return False

    def _b(self, __str: str = "", encoding: str = "utf-8") -> bytes:
        return bytes(__str, encoding=encoding)
