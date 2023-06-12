import os, sys

_dir = __file__.split('\\')[:-3]
if _dir[0].endswith(':'): _dir[0] += '\\'
sys.path.insert(0, os.path.join(*_dir))

from __init__ import *

logger = Logger()
server = Server(logger=logger, settings_file=os.path.realpath("tests\\server\\settings.json"))
server.start()
