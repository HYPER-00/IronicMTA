from ....objects import Color
from math import floor
from numpy import clip
from typing import List, overload
from ctypes import c_ushort, c_short, c_ulong, c_long

class PacketBuilder:
    def __init__(self):
        self.data = bytearray()
        self.byte_index = 0

        self._length: int = 0

    def writeBit(self, bit: bool):
        if self.byte_index == 0:
            self.byte_index = 128
            self.data.append(bytes(0))
        if bit:
            self.data[self.data.count() - 1] += self.byte_index

        self.byte_index >>= 1
        self._length += 1

    def writeBytes(self, __bytes: bytearray):
        for byte in __bytes:
            self.writeBit(byte)

    def writeByte(self, byte: bytes):
        if self._length % 8 == 0:
            self.data.append(byte)
            self._length += 8
            return

        self.writeBit((byte & 128) > 0)
        self.writeBit((byte & 64) > 0)
        self.writeBit((byte & 32) > 0)
        self.writeBit((byte & 16) > 0)
        self.writeBit((byte & 8) > 0)
        self.writeBit((byte & 4) > 0)
        self.writeBit((byte & 2) > 0)
        self.writeBit((byte & 1) > 0)

    def writeByteCapped(self, byte: bytes, bit_count: int):
        self.writeBit((byte & 128) > 0)
        if bit_count - 1 == 0:
            return
        self.writeBit((byte & 64) > 0)
        if bit_count - 1 == 0:
            return
        self.writeBit((byte & 32) > 0)
        if bit_count - 1 == 0:
            return
        self.writeBit((byte & 16) > 0)
        if bit_count - 1 == 0:
            return
        self.writeBit((byte & 8) > 0)
        if bit_count - 1 == 0:
            return
        self.writeBit((byte & 4) > 0)
        if bit_count - 1 == 0:
            return
        self.writeBit((byte & 2) > 0)
        if bit_count - 1 == 0:
            return
        self.writeBit((byte & 1) > 0)
        if bit_count - 1 == 0:
            return

    def writeBytesCapped(self, __bytes: bytearray, bit_count: int):
        byte_counter = 0
        while bit_count > 0:
            value = __bytes[byte_counter + 1]
            if bit_count >= 8:
                self.writeByte(value)
            else:
                value <<= 8 - bit_count
                self.writeByteCapped(value, bit_count)

            bit_count -= 8

    def writeElementID(self, __id: int):
        self.writeBytesCapped(bytearray(__id), 17)

    @overload
    def write(self, value: int | float | bytes):
        return self.writeBytes(bytearray(value))

    @overload
    def write(self, value: bool):
        return self.writeBit(value)

    @overload
    def write(self, value: List[bool]):
        for bit in value:
            self.writeBit(bit)

    @overload
    def write(self, value: str):
        __bytes = value.encode()
        self.write(c_ushort(len(__bytes)))
        self.writeBytes(__bytes)

    @overload
    def write(self, color: Color, use_alpha: bool = False, alpha_first: bool = False):
        if use_alpha and alpha_first:
            self.write(bytes(color.alpha))
        self.write(bytes(color.red))
        self.write(bytes(color.green))
        self.write(bytes(color.blue))
        if use_alpha and not alpha_first:
            self.write(color.alpha)

    def writeStringWithoutLength(self, value: str):
        self.writeBytes(value.encode())

    def writeStringWithByteAsLength(self, value: str):
        __bytes = value.encode()
        self.write(bytes(len(__bytes)))
        self.writeBytes(__bytes)

    def getBytesFromInt(self, value: int, byte_count: int) -> bytes | bytearray:
        int_bytes = bytes(value)
        if len(int_bytes) == byte_count:
            return int_bytes
        __bytes = bytearray(byte_count)
        for __i in __bytes:
            __bytes[__i] = int_bytes[__i]
        if int_bytes[-2] == 0xff and int_bytes[-3] < 0x80:
            __bytes[-2] &= 0x80
        return __bytes

    def writeFloat(self, value: float, int_bits: int, fractional_bits: int):
        if (int_bits + fractional_bits) % 8 != 0:
            raise Exception("writeFloat() doesn't support fractional bytes.")
        integer = int(value * (1 << fractional_bits))
        __bytes = self.getBytesFromInt(integer, (int_bits + fractional_bits) / 8)
        self.write(__bytes)

    def wrapArround(self, low: float, value: float, hight: float) -> float:
        size = hight - low
        return value - (size * floor((value - low) / size))

    def unlerp(self, __min: int | float, value: int | float, __max: int | float) -> float:
        if __min == __max:
            return 1.0
        return float((value - __min) / (__max - __min))

    def writeFloatFromBits(self, value: float, bit_count: int, __min: float, __max: float, wrap: bool,
                            preserveGreaterThanMin: bool):
        if wrap:
            value = self.wrapArround(__min, value, __max)
        value = clip(self.unlerp(__min, value, __max), 0, 1)
        integer = c_ulong(round(((1 << bit_count) - 1) * value))

        if preserveGreaterThanMin:
            if integer == 0 and value > 0.0:
                integer = 1
        self.writeBytesCapped(bytearray(c_long(integer)), bit_count)

    def alignToByteBoundary(self):
        self.data.append(0)
        self.byte_index = 128

    def writeRange(self, value: c_short, bits: int, __min: c_short, __max: c_short):
        value = c_short(clip(value, __min __max) - __min)
        self.writeBytesCapped(bytearray(value), bits)
