from json import load
from common import PacketTypes

def load(packet_type: int) -> dict:
    _packet_types = PacketTypes()
    str_packet = None

    match (packet_type):
        case _packet_types.ELEMENT_RPC:
            str_packet = "element_rpc"
        case _packet_types.MAIN_PACKETS:
            str_packet = "main_packets"
        case _packet_types.PACKET_ID:
            str_packet = "packetid"

    if not str_packet:
        raise Exception("Invalid packet type.")

    with open(str(str_packet) + "json", "r") as file:
        _content = load(file)

    return _content
