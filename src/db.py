import mysql.connector.pooling

from config import Config

config = {
    'user': Config.DB_USER,
    'database': Config.DB_NAME,
    'password': Config.DB_PASSWORD
    }

class Database:
    def __init__(self):
        """Initialize the connection pool."""
        self.pool = mysql.connector.pooling.MySQLConnectionPool(autocommit=True,              # D= para no tener q hacer commit :/
                                                                pool_name="pileta",
                                                                pool_size=5,
                                                                **config)

    def get_connection(self):
        try:
            conn = self.pool.get_connection()
        except mysql.connector.PoolError as err:
            # logger.exception("Pool agotada D=", err.msg, err.errno)
            raise
        except Exception as err:
            # logger.exception("Error inesperado", err)
            raise
        else:
            return conn