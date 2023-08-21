from pip import main
import os, sys

_dir = __file__.split('\\')[:-4]
if _dir[0].endswith(':'): _dir[0] += '\\'
sys.path.insert(0, os.path.join(*_dir))

import IronicMTA

server = IronicMTA.Server(main_file=__file__, settings_file="settings.json")
logger = server.getLogger()

@server.event.onServerStart
def onstart(server):
    logger.debug(f"{server.getTotalResourcesCount()} Resources Loaded.")
    logger.debug(f"EVENT-TEST: Server Has Been Started ({server})")

server.start()
