from .mysql import MySQL
from .sqlite3 import SQLite3
from os.path import join

class DatabaseManager(object):
    def __init__(self, server) -> None:
        self._settings = server.getSettings()
        self._logger = server.getLogger()
        self._mysql_section = self._settings["databases"]["mysql"]
        self._can_connect_to_mysql = False
        self._can_connect_to_sqlite = False
        
        self._mysql_database = None
        self._sqlite3_database = None

        if bool(self._mysql_section["enabled"]): # Maybe the user typed 1
            if (
                str(self._mysql_section["host"]).strip() 
                and str(self._mysql_section["user"]).strip()
                and str(self._mysql_section["database"]).strip()
            ):
                try:
                    _mysql_port = int(self._mysql_section["port"])
                    if 0 <= _mysql_port <= 65535:
                        if _mysql_port == 0:
                            _mysql_port = 3306
                        self._can_connect_to_mysql = True
                except KeyError:
                    self._logger.error("Couldn't Find Mysql section in settings file.")

                except ValueError:
                    self._logger.error("'str' object cannot be interpreted as an integer"
                                       "(The Mysql Port Number Must Be of type int)")
        if bool(self._settings["databases"]["sqlite3"]["enabled"]):
            try:
                if "database_path" in self._settings["databases"]["sqlite3"]:
                    sqlite_path = self._settings["databases"]["sqlite3"]["database_path"]
                else:
                    sqlite_path = join(server.getBaseDirectory(), "default_database.db")
                self._can_connect_to_sqlite = True
            except KeyError:
                self._logger("'sqlite3' section is removed. cannot connect to sqlite3 database.")

        if self._can_connect_to_mysql:
            self._mysql_database = MySQL(self._settings["databases"]["mysql"])

        if self._can_connect_to_sqlite:
            self._sqlite3_database = SQLite3(sqlite_path)
