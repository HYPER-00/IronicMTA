import os, sys

_dir = __file__.split('\\')[:-2]
if _dir[0].endswith(':'): _dir[0] += '\\'
print(os.path.join(*_dir))
sys.path.insert(0, os.path.join(*_dir))

from __init__ import *

logger = Logger(log_file="logger_test.logs")
logger.error("Error Test")
logger.log("Log Test")
logger.success("Success Test")
logger.warn("Warn Test")
