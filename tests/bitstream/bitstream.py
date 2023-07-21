import os, sys

_dir = __file__.split('\\')[:-3]
if _dir[0].endswith(':'): _dir[0] += '\\'
sys.path.insert(0, os.path.join(*_dir))

from core.packet_handler.io import BitStream

bitstream = BitStream()
bitstream.write_string("Player1Stringqsd123") # Player Version
bitstream.write_string("Playqsder2String")
bitstream.write_string("Playazeer2String")
bitstream.write_string("Player2qsdString")

new_stream = BitStream(bitstream.get_bytes())

print(f"String1: '{new_stream.read_string()}'")
print(f"String2: '{new_stream.read_string()}'")
print(f"String2: '{new_stream.read_string()}'")
print(f"String2: '{new_stream.read_string()}'")
