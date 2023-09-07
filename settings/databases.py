from typing import TypedDict


class MySQLSettings(TypedDict):
    enabled: bool
    host: str
    user: str
    password: str
    database: str
    port: int


class SQLite3Settings(TypedDict):
    enabled: bool
    database_path: str


class DatabasesSettings(TypedDict):
    mysql: MySQLSettings
    sqlite3: SQLite3Settings
