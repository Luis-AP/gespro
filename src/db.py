from mysql.connector.pooling import MySQLConnectionPool
from mysql.connector.connection import MySQLConnection
from mysql.connector.errors import Error, PoolError

from flask import current_app as app

class DbError(Exception):
    pass

class Database:
    def __init__(self, config):
        """Initialize the connection pool."""
        try:
            self.pool = MySQLConnectionPool(pool_name="pileta",
                                            pool_size=5,
                                            host=config.DB_HOST,
                                            database=config.DB_NAME,
                                            user=config.DB_USER,
                                            password=config.DB_PASSWORD)
        except Error as err:
            app.logger.critical("%s - %s - %s", err.msg, err.errno, err.sqlstate)
            app.logger.debug("db_host: %s, db_database: %s, db_user: %s",
                             config.DB_HOST, config.DB_DATABASE, config.DB_USER)
            raise DbError(f"Error al conectar con la base de datos. {err.msg}")

    def get_connection(self) -> MySQLConnection:
        try:
            conn = self.pool.get_connection()
        except PoolError as err:
            app.logger.critical("Connection pool exhausted. %s", err.msg)
            raise DbError(f"Pool de conexiones agotada. {err}")
        else:
            return conn
