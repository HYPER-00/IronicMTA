"""
    Packet Reader
"""

from ctypes import (
    c_uint,

    c_uint16, 
    c_uint32, 
    c_uint64, 

    c_int16,
    c_int32,
    c_int64,
    c_double
)
from math import ceil

class PacketReader:
    """
        Packet Reader Class
    """
    def __init__(self, data: str) -> None:
        self.data = data
        self.counter = 0
        self.size = len(data) * 8
        self.isfinished = self.counter == self.size

        self.data_index = 0
        self.byte_index = 128

    def getuint16(self) -> c_uint16:
        return c_uint16(self.getBytesFromData(2))

    def getuint32(self) -> c_uint16:
        return c_uint32(self.getBytesFromData(4))

    def getuint64(self) -> c_uint16:
        return c_uint64(self.getBytesFromData(8))

    ####################

    def getint16(self) -> c_uint16:
        return c_int16(self.getBytesFromData(2))

    def getint32(self) -> c_uint16:
        return c_int32(self.getBytesFromData(4))

    def getint64(self) -> c_uint16:
        return c_int64(self.getBytesFromData(8))

    def getdouble(self) -> c_double:
        return c_double(self.getBytesFromData(8))

    def getBitFromData(self) -> bool:
        """
            Returns bit from data
        """
        current = self.data[self.data_index]
        bit = (current and self.byte_index) > 0
        self.byte_index >>= 1
        if self.byte_index == 0:
            self.byte_index = 128
            self.data_index += 1

        self.counter += 1
        return bit

    def getByteFromData(self) -> bytes:
        """
            Returns byte from data
        """
        if (self.counter % 8) == 0:
            self.counter += 8
            return self.data[self.data_index]

        value = bytes(0)

        if self.getBitFromData():
            value += 128
        if self.getBitFromData():
            value += 64
        if self.getBitFromData():
            value += 32
        if self.getBitFromData():
            value += 16
        if self.getBitFromData():
            value += 8
        if self.getBitFromData():
            value += 4
        if self.getBitFromData():
            value += 2
        if self.getBitFromData():
            value += 1

        return value

    def getBytesFromData(self, count: int) -> bytearray:
        bytes_ = bytearray(count)
        for i in range(count):
            bytes_[i] = self.getBitFromData()
        return bytes_

    def getBits(self, count: int):
        """
            Returns bits from data
        """
        results = bool(count)
        for i in range(count):
            results[i] = self.getBitFromData()

        return results

    def getByteCapped(self, bit_count: int, alignament: bool = False) -> bytes:
        """
            Returns one byte capped from data
        """
        value = bytes(0)
        i = bit_count - 1
        for i in range(i, 0, -1):
            if self.getBitFromData():
                value += bytes(1 << i)

        return value

    def getBytesCapped(self, bit_count: int, alignament: bool = False) -> bytearray:
        """
            Returns bytes capped from data
        """
        byte_count = int(ceil(bit_count) / 8)
        values = bytearray()
        for i in range(byte_count):
            values[i] = self.getByteFromData()

        remaining_bits = bit_count - (byte_count - 1) * 8
        values[len(values) - 1] = self.getByteCapped(remaining_bits, alignament)

        return values

    def getStringChars(self, length: int) -> str:
        """
            Returns string chars from data
        """
        return self.getBytesFromData(length).decode()

    def getString(self) -> str:
        """
            Returns string from data
        """
        return self.getStringChars(self.getuint16())

    def getElementID(self) -> int:
        """
            `Returns` int: element id
        """
        __id = c_uint32(self.getBytesCapped(17).extend(bytearray(0)))
        maxvalue = (1 << 17) - 1
        if  id == maxvalue:
            return ... # Todo

        return id

    def getIntFromBytes(self, bytes_: bytearray) -> int:
        r = 0
        b0 = 0xFF

        if (bytes_[len(bytes_) - 1] and 0x80) != 0:
            r |= b0 << (len(bytes_) * 8)

        for i in range(len(bytes_)):
            r |= bytes_[len(bytes_) - 1 - i] << ((len(bytes_ - i - 1)) * 8)

        return r

    def getUIntFromBytes(self, bytes_: bytearray) -> c_uint:
        """
            `Returns:` Uint bytes
        """
        r = 0
        for i in range(len(bytes_)):
            r |= bytes_[len(bytes_) - 1 - i] << ((len(bytes_) - i - 1) * 8)

        return r

    def getFloat(self, int_bits: int, fractional_bits: int) -> float:
        int_bytes = self.getBytesCapped(int_bits + fractional_bits, True)
        int_value = self.getIntFromBytes(int_bytes)
        return float(int_value / (1 << fractional_bits))

    def getFloatFromBits(self, bit_count: int, __min: float, __max: float) -> float:
        if bit_count % 8 == 0:
            bytes_ = self.getBytesFromData(bit_count / 8)
        else:
            bytes_ = self.getBytesCapped(bit_count)
        integer = self.getUIntFromBytes(bytes_)

        return __min + integer / float((1 << bit_count) - 1) * (__max - __min)

    def alignToByteBoundary(self):
        self.byte_index = 128
        self.data_index += 1
