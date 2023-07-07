import os, sys

_dir = __file__.split('\\')[:-3]
if _dir[0].endswith(':'): _dir[0] += '\\'
sys.path.insert(0, os.path.join(*_dir))

from server import Server

server = Server(settings_file=os.path.realpath("tests\\server\\settings.json"))
server.start()
