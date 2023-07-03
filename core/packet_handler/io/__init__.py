from struct import pack, unpack
from errors import BitStreamError

class BitStream:
    def __init__(self, buffer: bytearray | bytes = bytearray()):
        if isinstance(buffer, bytes):
            self._buffer = bytearray(buffer)
        else:
            self._buffer = buffer
        self.write_offset = 0
        self._read_offset = 0

    def refresh(self, buffer: bytearray):
        self._buffer = buffer

    def reset(self):
        self._buffer = bytearray()

    def write_bytes(self, data: bytes):
        byte_count = len(data)
        self._buffer.extend(data)
        self.write_offset += byte_count

    def write_elementid(self, element):
        self.write_bytes_capped(bytes(element.value), 17)

    def read_bytes(self, byte_count):
        if self._read_offset + byte_count > len(self._buffer):
            raise BitStreamError("Trying to read beyond the end of the bitstream")
        result = self._buffer[self._read_offset:self._read_offset + byte_count]
        self._read_offset += byte_count
        return result
    
    def write_ushort(self, value):
        self.write_uint16(value)
    
    def write_uint16(self, value):
        self.write_bits(value, 16)

    def write_bytes_capped(self, byte_data, max_bytes):
        if len(byte_data) > max_bytes:
            raise BitStreamError("Byte data exceeds the maximum allowed length")
        self.write_uint16(len(byte_data))
        self.write_bytes(byte_data)

    def write_bit(self, bit):
        if bit:
            self._buffer.append(0x01)
        else:
            self._buffer.append(0x00)
        self.write_offset += 1

    def write_bits(self, value, num_bits):
        if num_bits < 0 or num_bits > 32:
            raise BitStreamError("Invalid number of bits for writing")
        for i in range(num_bits):
            bit = (value >> (num_bits - 1 - i)) & 1
            self.write_bit(bit)

    def write_int(self, value, num_bits):
        if num_bits < 0 or num_bits > 32:
            raise BitStreamError("Invalid number of bits for writing an integer")
        value &= (1 << num_bits) - 1
        self.write_bits(value, num_bits)

    def write_float(self, value):
        byte_data = pack('!f', value)
        self.write_bytes(byte_data)

    def write_range(self, value, min_value, max_value):
        if value < min_value or value > max_value:
            raise BitStreamError("Value is outside the specified range")
        range_size = max_value - min_value + 1
        num_bits = (range_size - 1).bit_length()
        normalized_value = value - min_value
        self.write_bits(normalized_value, num_bits)

    def write_float_from_bits(self, value, num_bits):
        if num_bits < 0 or num_bits > 32:
            raise BitStreamError("Invalid number of bits for writing a float")
        packed_value = pack('!f', value)
        int_value = unpack('!I', packed_value)[0]
        truncated_value = (int_value >> (32 - num_bits)) & ((1 << num_bits) - 1)
        self.write_bits(truncated_value, num_bits)

    def read_bit(self):
        if self._read_offset >= len(self._buffer):
            raise BitStreamError("Trying to read beyond the end of the bitstream")
        bit = bool(self._buffer[self._read_offset])
        self._read_offset += 1
        return bit

    def read_bits(self, num_bits):
        if num_bits <= 0:
            return 0
        num_bytes = (num_bits + 7) // 8
        byte_data = self.read_bytes(num_bytes)
        value = 0
        for i in range(num_bytes):
            value |= byte_data[i] << (8 * i)
        value &= (1 << num_bits) - 1
        return value

    def read_byte(self):
        return self.read_bits(8)
    
    def write_string_without_len(self, string: str):
        self.write_bytes(string.encode())

    def write_string(self, string: str):
        encoded_string = string.encode('utf-8')
        string_length = len(encoded_string)
        self.write_bytes(string_length.to_bytes(2, byteorder='little'))
        self.write_bytes(encoded_string)

    def read_char(self):
        byte_value = self.read_byte()
        char_value = chr(byte_value)
        return char_value

    def read_string_characters(self, num_characters):
        characters = ""
        for _ in range(num_characters):
            character = self.read_char()
            characters += character
        return characters

    def read_string(self):
        string_length = int.from_bytes(self.read_bytes(2), byteorder='little')
        encoded_string = self.read_bytes(string_length)
        return encoded_string.decode('utf-8')

    def get_bytes(self):
        return bytes(self._buffer)
    
    def read_uint16(self):
        if self._read_offset + 2 > len(self._buffer):
            raise BitStreamError("Trying to read beyond the end of the bitstream")
        value = (self._buffer[self._read_offset] << 8) | self._buffer[self._read_offset + 1]
        self._read_offset += 2
        return value

    def read_uint32(self):
        if self._read_offset + 4 > len(self._buffer):
            raise BitStreamError("Trying to read beyond the end of the bitstream")
        value = (self._buffer[self._read_offset] << 24) | (self._buffer[self._read_offset + 1] << 16) | \
                (self._buffer[self._read_offset + 2] << 8) | self._buffer[self._read_offset + 3]
        self._read_offset += 4
        return value

    def read_uint64(self):
        if self._read_offset + 8 > len(self._buffer):
            raise BitStreamError("Trying to read beyond the end of the bitstream")
        value = (self._buffer[self._read_offset] << 56) | (self._buffer[self._read_offset + 1] << 48) | \
                (self._buffer[self._read_offset + 2] << 40) | (self._buffer[self._read_offset + 3] << 32) | \
                (self._buffer[self._read_offset + 4] << 24) | (self._buffer[self._read_offset + 5] << 16) | \
                (self._buffer[self._read_offset + 6] << 8) | self._buffer[self._read_offset + 7]
        self._read_offset += 8
        return value

    def read_int16(self):
        value = self.read_uint16()
        if value & 0x8000:
            value = -((value ^ 0xFFFF) + 1)
        return value

    def read_int32(self):
        value = self.read_uint32()
        if value & 0x80000000:
            value = -((value ^ 0xFFFFFFFF) + 1)
        return value

    def read_int64(self):
        value = self.read_uint64()
        if value & 0x8000000000000000:
            value = -((value ^ 0xFFFFFFFFFFFFFFFF) + 1)
        return value

    def read_float(self):
        if self._read_offset + 4 > len(self._buffer):
            raise BitStreamError("Trying to read beyond the end of the bitstream")
        bytes_data = self._buffer[self._read_offset : self._read_offset + 4]
        self._read_offset += 4
        return unpack('!f', bytes_data)[0]

    def read_double(self):
        if self._read_offset + 8 > len(self._buffer):
            raise BitStreamError("Trying to read beyond the end of the bitstream")
        bytes_data = self._buffer[self._read_offset : self._read_offset + 8]
        self._read_offset += 8
        return unpack('!d', bytes_data)[0]

    def read_bytes_capped(self, max_bytes):
        length = self.read_uint16()
        if length > max_bytes:
            raise BitStreamError("Capped byte length exceeds the maximum allowed")
        return self.read_bytes(length)

    def get_size(self):
        return len(self._buffer)
