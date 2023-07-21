import struct

class BitStream:
    def __init__(self, buffer: bytearray | bytes = bytearray()):
        if isinstance(buffer, bytes):
            self._buffer = bytearray(buffer)
        else:
            self._buffer = buffer
        self.write_offset = 0
        self._read_offset = 0

    def refresh(self, buffer: bytearray):
        self._buffer.clear()
        self._buffer.extend(buffer)

    def reset(self):
        self._buffer = bytearray()

    def write_bytes(self, data):
        self._buffer.extend(data)

    def read_bytes(self, length):
        data = self._buffer[:length]
        del self._buffer[:length]
        print("Data: ", data)
        return data

    def write_ushort(self, value):
        self._buffer.extend(struct.pack('<H', value))

    def write_uint16(self, value):
        self.write_ushort(value)

    def write_bytes_capped(self, data, max_length):
        self._buffer.extend(data[:max_length])

    def write_bit(self, value):
        if self._read_offset == 0:
            self._buffer.append(0)
        if value:
            self._buffer[-1] |= 1 << self._read_offset
        self._read_offset = (self._read_offset + 1) % 8

    def write_bits(self, value, num_bits):
        for _ in range(num_bits):
            self.write_bit(value & 1)
            value >>= 1

    def write_int(self, value):
        self._buffer.extend(struct.pack('<i', value))

    def write_float(self, value):
        self._buffer.extend(struct.pack('<f', value))

    def write_float_from_bits(self, value):
        self.write_int(value)

    def read_bit(self):
        if not self._buffer:
            return False
        value = bool(self._buffer[0] & (1 << self._read_offset))
        self._read_offset = (self._read_offset + 1) % 8
        return value

    def reset_read_offset(self):
        self._read_offset = 0

    def read_bits(self, num_bits: int):
        value = 0
        for _ in range(num_bits):
            value |= self.read_bit() << _
        self._read_offset += num_bits
        return value

    def read_byte(self):
        return self.read_bits(8)

    def write_string_without_len(self, string):
        self._buffer.extend(string.encode())

    def write_string(self, string):
        self.write_ushort(len(string))
        self.write_string_without_len(string)

    def read_char(self):
        return chr(self.read_byte())

    def read_string_characters(self, length):
        return ''.join([self.read_char() for _ in range(length)])

    def read_string(self):
        length = self.read_ushort()
        print(f"String Length: {length}")
        return self.read_string_characters(length)

    def read_ushort(self):
        return struct.unpack('<H', self.read_bytes(2))[0]

    def read_uint(self):
        return self.read_ushort()

    def read_uint16(self):
        return self.read_ushort()

    def read_uint32(self):
        return struct.unpack('<I', self.read_bytes(4))[0]

    def read_uint64(self):
        return struct.unpack('<Q', self.read_bytes(8))[0]

    def read_int16(self):
        return struct.unpack('<h', self.read_bytes(2))[0]

    def read_int32(self):
        return struct.unpack('<i', self.read_bytes(4))[0]

    def read_int64(self):
        return struct.unpack('<q', self.read_bytes(8))[0]

    def read_float(self):
        return struct.unpack('<f', self.read_bytes(4))[0]

    def read_double(self):
        return struct.unpack('<d', self.read_bytes(8))[0]

    def read_bytes_capped(self, length):
        return self.read_bytes(length)

    def get_bytes(self):
        return bytes(self._buffer)
