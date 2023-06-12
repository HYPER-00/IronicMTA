"""
    MTASA net.dll wrapper
"""

import os
import sys
from platform import architecture
from typing import Literal, Any
from ctypes import (
    cdll,
    c_char,
    c_char_p,
    c_ushort,
    c_int,
    c_uint,
    c_ulong,
    c_bool,
    c_byte,
    CFUNCTYPE,
    windll,
    WinError
)
import colorama

_dir = __file__.split('\\')[:-2]
if _dir[0].endswith(':'): _dir[0] += '\\'
_basedir = os.path.join(*_dir)
sys.path.insert(0, _basedir)

from core.packets.reliability import PacketReliability
from errors import (
    NetWrapperInitError,
    NetWrapperInterfaceError,
    NetWrapperLoadingError,
    NetWrapperStartError,
    NetWrapperVersionError
)

T = Literal[True] | None

sys.path.insert(0, _basedir)

colorama.init(autoreset=True)

def initcallback():
    print("Calllllllbackkkkkkkkkkk")
    return 1

def _log_err(err: str) -> None:
    print(f"{colorama.Fore.RED}[Net-Wrapper ERROR] {err}.")

class MTAVersionType:
    """
        MTA Version types
        * Custom
        * Experimental
        * Unstable
        * Untested
        * Release
    """
    def __init__(self):
        self.CUSTOM = 0x01
        self.EXPERIMENTAL = 0x03
        self.UNSTABLE = 0x05
        self.UNTESTED = 0x07
        self.REALEASE = 0x09

class WrapperCodes:
    """
        Wrapper Codes for net wrapper initialization
        * Sucess
        * Loading Error
        * Version Error
        * Interface Error
        * Initialization Error
        * Start Error
    """
    def __init__(self):
        self.sucess = 0
        self.loading_error = -1001
        self.version_error = -1003
        self.interface_error = -1004
        self.init_error = -1005
        self.start_error = -1006

version_type = MTAVersionType()

MTA_DM_SERVER_NET_MODULE_VERSION = 0x0AB
MTA_DM_SERVER_VERSION_TYPE = version_type.REALEASE

class NetWrapper(object):
    """
        MTA net.dll wrapper (closed source)
    """
    def __init__(self, port: int) -> None:
        self._port = port


        self._codes = WrapperCodes()
        self.__id = c_ushort(0)

        if MTA_DM_SERVER_VERSION_TYPE != version_type.REALEASE:
            _log_err("SafeServer Server does not support network debug dlls")
            sys.exit(-1)

        self.netpath = f"{_basedir}\\core\\lib\\{'release' if MTA_DM_SERVER_VERSION_TYPE == version_type.REALEASE else 'debug'}\\net{'' if MTA_DM_SERVER_VERSION_TYPE == version_type.REALEASE else '_d'}.dll"
        self.wrapperpath = f"{_basedir}\\core\\lib\\wrapper\\wrapper.x{architecture()[0][:2]}.dll"

        self._initialized = False

        try:
            self._netlib = cdll.LoadLibrary(self.netpath)
        except OSError as err:
            _log_err("Cannot Open network dll:")
            _log_err(err)

        iscompatible = self._netlib.CheckCompatibility(
            MTA_DM_SERVER_NET_MODULE_VERSION, c_ulong(version_type.UNSTABLE))

        if not self._netlib.CheckCompatibility and iscompatible:
            _log_err("""
            Network module not compatible!
            If this is a custom build, try to:
                1. Update net.dll
                3. Check MTASA_VERSION_TYPE
            """)
            sys.exit(-1)

        try:
            self._wrapperdll = cdll.LoadLibrary(self.wrapperpath)
        except OSError as err:
            _log_err("Cannot open wrapper dll:")
            _log_err(err)

    def init(self, playercount: int, servername: str) -> T:
        """
            Init net wrapper for sending packet
            `Returns` server id
        """
        if self._wrapperdll.initNetWrapper:
            _func = self._wrapperdll.initNetWrapper
            _func.restype = c_int
            _c_callback_t = CFUNCTYPE(
                c_char,  # packetId
                c_ulong, # bin addr
                c_char,  # payload
                c_ulong, # payload size
                c_bool,  # has ping
                c_uint)  # ping
            _func.argtypes = [c_char_p, c_char_p, c_char_p, c_ushort, c_uint, c_char_p,
                                                _c_callback_t]
            _c_netdll_path = c_char_p(self._b(self.netpath))
            _c_idfile = c_char_p(self._b(os.path.join(_basedir, "id")))
            _c_ip = c_char_p(b"192.168.1.204")
            _c_port = c_ushort(self._port)
            _c_player_count = c_uint(playercount)
            _c_servername = c_char_p(self._b(servername))

            _result = _func(
                _c_netdll_path,
                _c_idfile,
                _c_ip,
                _c_port,
                _c_player_count,
                _c_servername,
                _c_callback_t(initcallback)
            )
            if _result < 0:
                return _log_err(f"ERROR Unable to init net wrapper. ({_result})")

            match _result:
                case self._codes.sucess:
                    self._initialized = True
                    return True
                case self._codes.loading_error:
                    raise NetWrapperLoadingError(f"Unable to load net wrapper dll. ({_result})")
                case self._codes.init_error:
                    raise NetWrapperInitError(f"Unable to init wrapper dll. ({_result})")
                case self._codes.interface_error:
                    raise NetWrapperInterfaceError(f"Unable to setup net wrapper interface. ({_result})")
                case self._codes.start_error:
                    raise NetWrapperStartError(f"Unable to start net wrapper. ({_result})")
                case self._codes.version_error:
                    raise NetWrapperVersionError(f"Version is incomptatible with net wrapper. ({_result})")

            self.__id = c_ushort(_result)

    def destroy(self) -> T:
        """Destroy net wrapper"""
        self._wrapperdll.destroyNetWrapper(self.__id)
        return True

    def start(self) -> T:
        """
            Start net wrapper with id
        """
        if not self._initialized:
            raise NetWrapperInitError("net wrapper is not initialized. try to init()")

        if self._wrapperdll.startNetWrapper:
            try:
                self._wrapperdll.startNetWrapper(self.__id)
            except Exception:
                kernel32 = windll.kernel32
                _log_err("Coudldn't Start Net Wrapper")
                _log_err(WinError(kernel32.GetLastError()).strerror)
        return True

    def stop(self) -> T:
        """Stop net wrapper"""
        self._wrapperdll.stopNetWrapper(self.__id)
        return True

    def sendPacket(
        self,
        bin_addr: int,
        packet_id: int,
        bitstream_version: int,
        payload: bytes,
        priority: int,
        reliability: PacketReliability
    ) -> T:
        _size = sys.getsizeof(bytes(0)) * len(payload)
        ptr = id(_size)

        self._wrapperdll.sendPacket(
            self.__id,
            c_uint(bin_addr),
            c_byte(packet_id),
            c_ushort(bitstream_version),
            c_int(hex(ptr)),
            c_uint(_size),
            c_byte(priority),
            c_byte(reliability),
        )
        return True

    def setSocketVersion(self, addr: int, version: int) -> T:
        """Set client bitstream version"""
        self._wrapperdll.setSocketVersion(self.__id, addr, version)

    def getClientSerialAndVersion(self, addr: int, serial: str, extra: str, version: str) -> Any:
        """Get client serial and version"""
        return self._wrapperdll.getClientSerialAndVersion(
            self.__id,
            c_ulong(addr),
            c_char_p(self._b(serial)),
            c_char_p(self._b(extra)),
            c_char_p(self._b(version)),
        )

    def setChecks(
        self,
        disable_combo_ac_map: str,
        disable_ac_map: str,
        enable_sd_map: str,
        enable_client_checks: int,
        hide_ac: bool,
        img_mods: str,
    ) -> T:
        """Set Anticheat checks"""
        self._wrapperdll.setChecks(
            self.__id,
            c_char_p(disable_combo_ac_map),
            c_char_p(disable_ac_map),
            c_char_p(enable_sd_map),
            c_int(enable_client_checks),
            c_bool(hide_ac),
            c_char_p(img_mods),
        )
        return True

    def resendModPackets(self, addr: int) -> T:
        """Resend mod packets"""
        self._wrapperdll.resendModPackets(self.__id, c_ulong(addr))
        return True

    def resendPlayerACInfo(self, addr: int) -> T:
        """Resend player anticheat info"""
        self._wrapperdll.resendPlayerACInfo(self.__id, c_ulong(addr))

    def _b(self, __str: str = "", encoding: str = "utf-8") -> bytes:
        return bytes(__str, encoding=encoding)
