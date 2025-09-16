import mysql.connector
from . import connect


class BaseDAO:
    def __init__(self) -> None:
        """
        Initialize the BaseDAO with database connection parameters.
        """
        self.host = connect.dbhost
        self.user = connect.dbuser
        self.password = connect.dbpass
        self.database = connect.dbname
        self.port = connect.dbport
        self.connection = None
        self.cursor = None

    def connect(self):
        """
        Establish a connection to the database.

        This method initializes the database connection and cursor if they are not already established.
        """
        if self.connection is None:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port,
                autocommit=False,
            )
            self.cursor = self.connection.cursor()

    def disconnect(self):
        """
        Close the connection to the database.

        This method closes the database cursor and connection if they are open.
        """
        if self.cursor:
            self.cursor.close()
            self.cursor = None
        if self.connection:
            self.connection.close()
            self.connection = None

    def execute_query(self, query, params=()):
        """
        Execute a SELECT query and fetch all results.

        Args:
            query (str): The SQL query to execute.
            params (tuple, optional): The parameters to pass to the query. Defaults to ().

        Returns:
            list: The fetched results of the query.
        """
        self.connect()
        self.cursor.execute(query, params)
        result = self.cursor.fetchall()
        self.disconnect()
        return result

    def execute_non_query(self, query, params=()):
        """
        Execute an INSERT, UPDATE, or DELETE query.

        Args:
            query (str): The SQL query to execute.
            params (tuple, optional): The parameters to pass to the query. Defaults to ().
        """
        self.connect()
        self.cursor.execute(query, params)
        self.connection.commit()
        lastrowid = self.cursor.lastrowid
        self.disconnect()

        return lastrowid

    def build_query(self, base_query, conditions):
        """
        Build a SQL query with optional conditions.

        Args:
            base_query (str): The base SQL query.
            conditions (list): A list of conditions to append to the query.

        Returns:
            str: The constructed SQL query with conditions.
        """
        if conditions:
            if base_query.lower().find("where") == -1:
                base_query += " WHERE " + " AND ".join(conditions)
            else:
                base_query += " AND " + " AND ".join(conditions)

        return base_query

    def execute_transaction(self, queries_and_params):
        """
        Execute a series of queries within a transaction.

        Args:
            queries_and_params (list): A list of tuples, where each tuple contains a query and its parameters.

        Raises:
            Exception: If any query execution fails, the transaction is rolled back.
        """
        try:
            self.connect()
            for query, params in queries_and_params:
                self.cursor.execute(query, params)
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            raise e
        finally:
            self.disconnect()
    
    def execute_many(self, sql, data):
        """
        Execute a series of transaction in batch way
        e.g. insert a list of rows
        """
        try:
            self.connect()
            self.cursor.executemany(sql, data)
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            raise e
        finally:
            self.disconnect()
            