from typing import Union
from os.path import isfile

from IronicMTA import Server

import mysql.connector
from mysql.connector.cursor import CursorBase
import sqlite3

from ..errors import (
    MySQLConnectionDetected,
    MySQLNoConnection,
    MySQLUnkownError,
    SQLQueryUnkownConditionType,
)

CONNECTION = Union[mysql.connector.MySQLConnection, sqlite3.Connection]
CURSOR = Union[CursorBase, sqlite3.Cursor]

class DatabaseManager(object):
    def __init__(self, server: Server):
        self._settings = server.get_settings()["databases"]
        
        self._mysql_connection = None
        self._sqlite3_connection = None

        if self.is_mysql_database_enabled():
            self._mysql_connection = mysql.connector.connect(*self._settings)

        if self.is_sqlite3_database_enabled():
            assert isfile(
                self._settings["sqlite3"]["database_path"]
            ), "Invalid database path"
            self._sqlite3_connection = sqlite3.connect(
                self._settings["sqlite3"]["database_path"]
            )

    def _query(self, func) -> None:
        if self.is_mysql_database_enabled():
            func(self._mysql_connection)
        
        if self.is_sqlite3_database_enabled():
            func(self._sqlite3_connection)
            
    def test(self):
        self._query()

    @property
    def mysql_connection(self) -> Union[mysql.connector.MySQLConnection, None]:
        """Get MySQL Database Connection

        Returns:
        --------
            mysql.connector.MySQLConnection: Database connection
        """
        return self._mysql_connection

    @property
    def sqlite3_connection(self) -> Union[sqlite3.Connection, None]:
        """Get SQLite3 Database Connection

        Returns:
        --------
            sqlite3.Connection: Database connection
        """
        return self._sqlite3_connection

    def is_mysql_database_enabled(self) -> bool:
        return self._settings["sqlite3"]["enabled"]

    def is_sqlite3_database_enabled(self) -> bool:
        return self._settings["mysql"]["enabled"]
