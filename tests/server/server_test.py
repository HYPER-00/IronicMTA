import os, sys

_dir = __file__.split('\\')[:-3]
if _dir[0].endswith(':'): _dir[0] += '\\'
sys.path.insert(0, os.path.join(*_dir))

from server import Server
from logger import Logger

server = Server(main_file=__file__, settings_file="settings.json")
logger: Logger = server.getLogger()


@server.event.onServerStart
def onstart(server):
    print(f"{server.getTotalResourcesCount()} Resources Loaded.")
    logger.debug(f"EVENT-TEST: Server Has Been Started ({server})")

    for res in server.getAllResources():
        print(f"Running Resource Path: {res.getCorePath()}")

server.start()
