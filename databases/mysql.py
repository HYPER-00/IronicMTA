"""
    IronicMTA Server database manager
    Supported databases: MySQL, SQLite
"""

from typing import Any, Literal, List, Dict
from errors import (
    MySQLConnectionDetected,
    MySQLNoConnection,
    MySQLUnkownError,
    SQLQueryUnkownConditionType,
)
import mysql.connector
from settings_manager import SettingsManager


class MySQL:
    def __init__(self, database_credentials: Dict[str, str | Any]):
        self._database_credentials = database_credentials
        self.isconnected = False
        self.conditions_types = ['AND', 'OR', 'LIKE']

        self.db = None
        self.cursor = None

    def connect(self) -> Any:
        """
            Connect To Database
            * `Returns`: Database object
            * `Syntax`:\n
            >>> db = Mysql()
            >>> conn = db.connect()
        """
        if not self.isconnected:
            try:
                self.db = mysql.connector.connect(
                    **self._database_credentials)
                self.cursor = self.db.cursor()
                self.isconnected = True
            except Exception as err:
                print(err)
            return self.db
        else:
            raise MySQLConnectionDetected("Server Already connected to")

    def insert(self, table_name: str, data: dict):
        """
            * Insert data to table
            * `Syntax`\n
            >>> db = Mysql()
            >>> conn = db.connect()
            >>> db.insert(table_name="mytable", data={"name": "Any"})
        """

        if self.isconnected:
            self._sql = "insert into %s( %s ) values( %s )"
            self._data_keys = ', '.join(
                "'" + str(x).replace('/', '_') + "'" for x in data.keys())
            self._data_values = ', '.join(
                "'" + str(x).replace('/', '_') + "'" for x in data.values())
            self._sql = self._sql % (
                table_name,  self._data_keys.replace("'", ""), self._data_values)

            self._is_executed = self.cursor.execute(self._sql)
            self.db.commit()
            if self._is_executed:
                return True
        else:
            raise MySQLNoConnection("Cannot Detect MySQL Connection")

    def select(
        self,
        table_name: str,
        columns: List[str],
        condition: dict = None,
        condition_type: str = 'AND',
    ) -> Literal[True] | None:
        """
            * Select Data From Database\n
            * `Returns`: List[Tuple[]]
            * `Args`:\n
                table_name: str, \n
                columns: str = columns to select it, \n
                condition: dict = condition to verify data, \n
                condition_type: str = the link of the conditions must be "or", "and" or "like", 
            * `Syntax`\n
            >>> db = Mysql()
            >>> conn = db.connect()
            >>> db.select(table_name="mytable", columns=["name", "age"], condition={"started-in": "00-00-2022", "started-in": "00-00-2023"}, condition_type="or")
        """

        if self.isconnected:
            self._sql = f'SELECT {", ".join(columns)} FROM {table_name}'
            if condition:
                condition_type = condition_type.strip().upper()

                if not condition_type in self.conditions_types:
                    raise SQLQueryUnkownConditionType(
                        f'Unkown condition type \'{condition_type}\'\nCondition Type Must Be In {self.conditions_types}')

                self._conditions = []
                self._condition = '{}=\'{}\''

                for _key, _value in condition.items():
                    self._conditions.append(
                        self._condition.format(_key, _value))

                self._conditions = f' {condition_type} '.join(self._conditions)
                self._sql = self._sql + f' WHERE {self._conditions}'
            self.cursor.execute(self._sql)
            return self.cursor.fetchall()
        else:
            raise MySQLNoConnection("Cannot Detect MySQL Connection")

    def delete(
        self,
        table_name: str,
        condition: dict = None,
        condition_type: str = 'AND'
    ) -> bool:
        if self.isconnected:
            self._sql = f'DELETE FROM {table_name}'
            if condition:
                condition_type = condition_type.strip().upper()

                if not condition_type in self.conditions_types:
                    raise SQLQueryUnkownConditionType(
                        f'Unkown condition type \'{condition_type}\'\nCondition Type Must Be In {self.conditions_types}')

                self._conditions = []
                self._condition = '{}=\'{}\''

                for _key, _value in condition.items():
                    self._conditions.append(
                        self._condition.format(_key, _value))

                self._conditions = f' {condition_type} '.join(self._conditions)
                self._sql = self._sql + f' WHERE {self._conditions}'
            self._is_executed = self.cursor.execute(self._sql)
            self.db.commit()
            if self._is_executed:
                return True
        else:
            raise MySQLNoConnection("Cannot Detect MySQL Connection")

    def update(
        self,
        table_name: str,
        data: dict,
        condition: dict = None,
        condition_type: str = 'AND'
    ):
        """
            * Update Data From Database\n
            * `Args`\n
                table_name: str, \n
                data: dict = key => column of data, value => data to edit it \n
                condition: dict = condition to verify data, \n
                condition_type: str = the link of the conditions must be "or", "and" or "like", 
            * `Syntax`\n
            >>> db = Mysql()
            >>> conn = db.connect()
            >>> db.update(table_name="mytable", data={"name": "John"}, condition={"active": "true", "created-in": "00-00-2022"}, condition_type="an")
        """

        if self.isconnected:
            self._sql = 'UPDATE {} SET {}'
            self._format = '{} =\'{}\''
            self._data = []

            for _key, _value in data.items():
                self._data.append(
                    self._format.format(_key, _value))
            self._sql = self._sql.format(table_name, ', '.join(self._data))

            if condition:
                condition_type = condition_type.strip().upper()

                if not condition_type in self.conditions_types:
                    raise SQLQueryUnkownConditionType(
                        f'Unkown condition type \'{condition_type}\'\n\tCondition Type Must Be {self.conditions_types}')

                self._conditions = []
                self._condition = '{} = \'{}\''

                for _key, _value in condition.items():
                    self._conditions.append(
                        self._condition.format(_key, _value))
                self._conditions = f' {condition_type} '.join(self._conditions)
                self._sql = self._sql + f' WHERE {self._conditions}'
            self._is_executed = self.cursor.execute(self._sql)
            self.db.commit()
            if self._is_executed:
                return True
        else:
            raise MySQLNoConnection("Cannot Detect MySQL Connection")

    def disconnect(self):
        """
            Disconnect From Database
            * `Syntax`\n
            >>> db = Mysql()
            >>> conn = db.connect()
            >>> db.disconnect()
        """
        if self.isconnected:
            if self.db:
                self.cursor.close()
                self.db.close()
                self.isconnected = False
            else:
                raise MySQLUnkownError("Cannot Detect MySQL Connection")
        else:
            raise MySQLNoConnection("Cannot Detect MySQL Connection")
