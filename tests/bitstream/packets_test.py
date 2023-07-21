import os, sys

_dir = __file__.split('\\')[:-3]
if _dir[0].endswith(':'): _dir[0] += '\\'
sys.path.insert(0, os.path.join(*_dir))

from network.packets.join.modname import Packet_PlayerJoinModName
from core.packet_handler.io import BitStream

def get_int_bytes(packet):
    packet_bytes = []
    for byte in packet.build():
        packet_bytes.append(byte)
    print(packet_bytes)
    return packet_bytes


modname_packet = Packet_PlayerJoinModName(117)
modname_packet_bytes = get_int_bytes(modname_packet) 
modname_original_bytes = [117, 0, 10, 0, 100, 101, 97, 116, 104, 109, 97, 116, 99, 104]
print(f"Modname Packet: {modname_packet_bytes == modname_original_bytes}")

newbittream = BitStream(modname_packet.build())
print(newbittream.read_string())