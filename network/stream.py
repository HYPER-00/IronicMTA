import math
import struct

class Struct(struct.Struct):
	# cast-like syntax for packing
	def __call__(self, value):
		return self.pack(value)

	def __str__(self):
		return "<Struct %s>" % self.format

c_bool = Struct("?")
c_float = Struct("f")
c_double = Struct("d")
c_int = Struct("i")
c_uint = Struct("I")

c_byte = Struct("b")
c_ubyte = Struct("B")
c_short = Struct("h")
c_ushort = Struct("H")
c_long = Struct("l")
c_ulong = Struct("L")
c_longlong = Struct("q")
c_ulonglong = Struct("Q")

c_int8 = c_byte
c_uint8 = c_ubyte
c_int16 = c_short
c_uint16 = c_ushort
c_int32 = c_long
c_uint32 = c_ulong
c_int64 = c_longlong
c_uint64 = c_ulonglong

class c_bit:
	def __init__(self, boolean):
		self.value = boolean

# Note: a ton of the logic here assumes that the write offset is never moved back, that is, that you never overwrite things
# Doing so may break everything
class BitStream(bytearray):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._write_offset = len(self) * 8
		self._read_offset = 0

	def write(self, arg, compressed=False, allocated_length: str = None, length_type: str = None):
		if isinstance(arg, BitStream):
			self._write_bytes(arg)
			if arg._write_offset % 8 != 0:
				# This should work assuming the part after the arg's write offset is completely 0
				self._write_offset -= 8 - arg._write_offset % 8
				# In some cases it's possible we've written an unnecessary byte
				if self._write_offset//8 == len(self)-2:
					del self[-1]
			return
		if allocated_length is not None or length_type is not None:
			self._write_str(arg, allocated_length, length_type)
			return
		if isinstance(arg, (bytes, bytearray)):
			if compressed:
				self._write_compressed(arg)
			else:
				self._write_bytes(arg)
			return
		if isinstance(arg, c_bit):
			self._write_bit(arg.value)
			return

		raise TypeError(arg)

	def _write_str(self, str_, allocated_length, length_type):
		# Possibly include default encoded lengths for non-variable-length strings (seem to be 33 for string and 66 for wstring)
		if isinstance(str_, str):
			encoded_str = str_.encode("utf-16-le")
		else:
			encoded_str = str_

		if length_type is not None:
			# Variable-length string
			self.write(length_type(len(str_))) # Note: there's also a version that uses the length of the encoded string, should that be used?
		else:
			# Fixed-length string
			# null terminator
			if isinstance(str_, str):
				char_size = 2
			else:
				char_size = 1

			if len(encoded_str)+char_size > allocated_length:
				raise ValueError("String too long!")
			encoded_str += bytes(allocated_length-len(encoded_str))
		self._write_bytes(encoded_str)

	def _write_bit(self, bit):
		self._alloc_bits(1)
		if bit: # We don't actually have to do anything if the bit is 0
			self[self._write_offset//8] |= 0x80 >> self._write_offset % 8

		self._write_offset += 1

	def write_bits(self, value, number_of_bits):
		assert 0 < number_of_bits < 8
		self._alloc_bits(number_of_bits)

		if number_of_bits < 8: # In the case of a partial byte, the bits are aligned from the right (bit 0) rather than the left (as in the normal internal representation)
			value = value << (8 - number_of_bits) & 0xff # Shift left to get the bits on the left, as in our internal representation
		if self._write_offset % 8 == 0:
			self[self._write_offset//8] = value
		else:
			self[self._write_offset//8] |= value >> self._write_offset % 8 # First half
			if 8 - self._write_offset % 8 < number_of_bits: # If we didn't write it all out in the first half (8 - self._write_offset % 8 is the number we wrote in the first half)
				self[self._write_offset//8 + 1] = (value << 8 - self._write_offset % 8) & 0xff # Second half (overlaps byte boundary)

		self._write_offset += number_of_bits

	def _write_bytes(self, byte_arg):
		if self._write_offset % 8 == 0:
			self[self._write_offset//8:self._write_offset//8+len(byte_arg)] = byte_arg
		else:
			# Shift new input to current shift
			new = (int.from_bytes(byte_arg, "big") << (8 - self._write_offset % 8)).to_bytes(len(byte_arg)+1, "big")
			# Update current byte
			self[self._write_offset//8] |= new[0]
			# Add rest
			self[self._write_offset//8+1:self._write_offset//8+1+len(byte_arg)] = new[1:]
		self._write_offset += len(byte_arg)*8

	def _write_compressed(self, byte_arg):
		current_byte = len(byte_arg) - 1

		# Write upper bytes with a single 1
		# From high byte to low byte, if high byte is 0 then write 1. Otherwise write 0 and the remaining bytes
		while current_byte > 0:
			is_zero = byte_arg[current_byte] == 0
			self._write_bit(is_zero)
			if not is_zero:
				# Write the remainder of the data
				self._write_bytes(byte_arg[:current_byte + 1])
				return
			current_byte -= 1

		# If the upper half of the last byte is 0 then write 1 and the remaining 4 bits. Otherwise write 0 and the 8 bits.

		is_zero = byte_arg[0] & 0xF0 == 0x00
		self._write_bit(is_zero)
		if is_zero:
			self.write_bits(byte_arg[0], 4)
		else:
			self._write_bytes(byte_arg[:1])

	def align_write(self):
		if self._write_offset % 8 != 0:
			self._alloc_bits(8 - self._write_offset % 8)
			self._write_offset += 8 - self._write_offset % 8

	def _alloc_bits(self, number_of_bits):
		bytes_to_allocate = math.ceil((self._write_offset + number_of_bits) / 8) - len(self)
		if bytes_to_allocate > 0:
			self += bytes(bytes_to_allocate)

	def skip_read(self, byte_length):
		self._read_offset += byte_length * 8

	def read(self, arg_type, compressed=False, length: str = None, allocated_length: str = None, length_type: str = None):
		if isinstance(arg_type, struct.Struct):
			if compressed:
				if arg_type in (c_float, c_double):
					raise NotImplementedError
				read = self._read_compressed(arg_type.size)
			else:
				read = self._read_bytes(arg_type.size)
			return arg_type.unpack(read)[0]
		if issubclass(arg_type, c_bit):
			return self._read_bit()
		if allocated_length is not None or length_type is not None:
			return self._read_str(arg_type, allocated_length, length_type)
		if issubclass(arg_type, bytes):	
			return self._read_bytes(length)
		if issubclass(arg_type, BitStream):
			r = self._read_offset
			output = BitStream(self._read_bytes(length//8))
			if length % 8 != 0:
				endbyte = (self[self._read_offset//8] << self._read_offset % 8) & 0xff
				if self._read_offset % 8 != 0 and length % 8 > 8 - self._read_offset % 8:
					endbyte |= self[self._read_offset//8 + 1] >> 8 - self._read_offset % 8
				endbyte &= ~((1 << 8-length%8)-1)
				output._write_bytes(bytes([endbyte]))
				output._write_offset -= 8 - length % 8
				self._read_offset += length % 8
			return output
		raise TypeError(arg_type)

	def _read_str(self, arg_type, allocated_length, length_type):
		if issubclass(arg_type, str):
			char_size = 2
		else:
			char_size = 1

		if length_type is not None:
			# Variable-length string
			length = self.read(length_type)
			byte_str = self.read(bytes, length=length*char_size)
		else:
			# Fixed-length string
			byte_str = bytearray()
			while len(byte_str) < allocated_length:
				char = self._read_bytes(char_size)
				if sum(char) == 0:
					self.skip_read(allocated_length - len(byte_str) - char_size)
					break
				byte_str += char

		if issubclass(arg_type, str):
			return byte_str.decode("utf-16-le")
		return byte_str

	def _read_bit(self):
		bit = self[self._read_offset//8] & 0x80 >> self._read_offset % 8 != 0
		self._read_offset += 1
		return bit

	def read_bits(self, number_of_bits):
		assert 0 < number_of_bits < 8

		output = (self[self._read_offset//8] << self._read_offset % 8) & 0xff # First half
		if self._read_offset % 8 != 0 and number_of_bits > 8 - self._read_offset % 8: # If we have a second half, we didn't read enough bytes in the first half
			output |= self[self._read_offset//8 + 1] >> 8 - self._read_offset % 8 # Second half (overlaps byte boundary)
		output >>= 8 - number_of_bits
		self._read_offset += number_of_bits
		return output

	def _read_bytes(self, length):
		if self._read_offset % 8 == 0:
			output = self[self._read_offset//8:self._read_offset//8+length]
		else:
			output = self[self._read_offset//8:self._read_offset//8+length+1]
			# clear the part before the struct
			output[0] &= (1 << 8-self._read_offset%8) - 1
			# shift back
			output = (int.from_bytes(output, "big") >> (8-self._read_offset%8)).to_bytes(length, "big")
		self._read_offset += length*8
		return output

	def _read_compressed(self, number_of_bytes):
		current_byte = number_of_bytes - 1

		while current_byte > 0:
			if self._read_bit():
				current_byte -= 1
			else:
				# Read the rest of the bytes
				return bytearray(number_of_bytes - current_byte - 1) + self._read_bytes(current_byte + 1)

		# All but the first bytes are 0. If the upper half of the last byte is a 0 (positive) or 16 (negative) then what we read will be a 1 and the remaining 4 bits.
		# Otherwise we read a 0 and the 8 bits
		if self._read_bit():
			start = bytes([self.read_bits(4)])
		else:
			start = self._read_bytes(1)
		return start + bytearray(number_of_bytes - current_byte - 1)

	def align_read(self):
		if self._read_offset % 8 != 0:
			self._read_offset += 8 - self._read_offset % 8

	def all_read(self):
		# This is not accurate to the bit, just to the byte
		return math.ceil(self._read_offset / 8) == len(self)