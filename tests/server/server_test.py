import os
import sys

# IronicMTA path setup
_dir = __file__.replace("/", "\\").split("\\")[:-4]
if _dir[0].endswith(":"):
    _dir[0] += "\\"
sys.path.insert(0, os.path.join(*_dir))
import IronicMTA


server = IronicMTA.Server(main_file=__file__, settings_file="settings.json")
logger = server.get_logger()  # Get server logger


@server.event.onServerStart
def onstart(s: IronicMTA.Server):
    logger.debug(f"{server.get_resources_count()} Resources Loaded.")
    logger.debug(f"EVENT-TEST: Server Has Been Started ({s})")


server.start()
