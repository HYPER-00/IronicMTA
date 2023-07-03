"""
    MTASA net.dll wrapper
"""

from errors import (
    NetWrapperInitError,
    NetWrapperInterfaceError,
    NetWrapperLoadingError,
    NetWrapperStartError,
    NetWrapperVersionError
)
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
    c_ubyte,
    CFUNCTYPE,
    windll,
    WinError
)
import colorama

_dir = __file__.split('\\')[:-2]
if _dir[0].endswith(':'):
    _dir[0] += '\\'
_basedir = os.path.join(*_dir)
sys.path.insert(0, _basedir)


T = Literal[True] | None

sys.path.insert(0, _basedir)

colorama.init(autoreset=True)


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
        self.wrapperpath = f"{_basedir}\\core\\lib\\wrapper\\wrapper.x{architecture()[0][:2]}.debug.dll"

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
        """
        if self._wrapperdll.Setup:
            _func = self._wrapperdll.Setup
            # _func.restype = c_bool
            _func.argtypes = [c_char_p, c_char_p, c_char_p, c_ushort, c_char_p, c_uint,
                              ]
            _c_netdll_path = c_char_p(self._b(self.netpath))
            _c_idfile = c_char_p(self._b(os.path.join(_basedir, "id")))
            _c_ip = c_char_p(b"0.0.0.0")
            _c_port = c_ushort(self._port)
            _c_player_count = c_uint(playercount)
            _c_servername = c_char_p(self._b(servername))
            try:
                self._initialized = bool(_func(
                    _c_idfile,
                    _c_netdll_path,
                    _c_ip,
                    _c_port,
                    _c_servername,
                    _c_player_count,
                ))
                return self._initialized
            except Exception:
                kernel32 = windll.kernel32
                _log_err("Couldn't Start Net Wrapper")
                _log_err(WinError(kernel32.GetLastError()).strerror)
                exit(-1)
            # If Failed To Call Start Function
            if not _result:
                return _log_err("[ERROR] Unable to init net wrapper.")
            self._initialized = True
            return True

    def destroy(self) -> T:
        """Destroy net wrapper"""
        self._wrapperdll.destroyNetWrapper(self.__id)
        return True

    def start(self) -> T:
        """
            Start net wrapper with id
        """
        if not self._initialized:
            raise NetWrapperInitError(
                "net wrapper is not initialized. try to init()")

        if self._wrapperdll.Start:
            try:
                _isstarted = self._wrapperdll.Start()
                return _isstarted
            except Exception:
                kernel32 = windll.kernel32
                _log_err("Coudldn't Start Net Wrapper")
                _log_err(WinError(kernel32.GetLastError()).strerror)
        return False

    def send(
        self,
        packet_id,
        playerbin_addr: int,
        bitstream_version: int,
        content: bytearray,
        priority,
        reliability
    ) -> T:

        try:
            self._wrapperdll.SendPacket(
                c_ubyte(packet_id.value),
                c_uint(playerbin_addr),
                c_ushort(bitstream_version),
                c_char_p(content),
                c_int(sys.getsizeof(content)),
                c_uint(priority),
                c_uint(reliability),
            )
        except:
            kernel32 = windll.kernel32
            _log_err("Couldn't Send Packet!")
            _log_err(WinError(kernel32.GetLastError()).strerror)
            exit(-1)
        return True

    def _b(self, __str: str = "", encoding: str = "utf-8") -> bytes:
        return bytes(__str, encoding=encoding)
