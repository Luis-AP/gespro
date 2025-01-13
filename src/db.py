import mysql.connector.pooling
import mysql.connector

class DbError(Exception):
    pass

class Database:
    def __init__(self, config):
        """Initialize the connection pool."""
        try:
            self.pool = mysql.connector.pooling.MySQLConnectionPool(pool_name="pileta",
                                                                    pool_size=5,
                                                                    host=config.DB_HOST,
                                                                    database=config.DB_DATABASE,
                                                                    user=config.DB_USER,
                                                                    password=config.DB_PASSWORD)
        except mysql.connector.Error as err:
            # logger.exception("%s %d %s" % err.msg, err.errno, err.sqlstate)
            # logger.debug("db_host: %s, db_database: %s, db_user: %s" % (config.DB_HOST, config.DB_DATABASE, config.DB_USER))
            raise DbError(f"Error al conectar con la base de datos. {err.msg}")

    def get_connection(self):
        try:
            conn = self.pool.get_connection()
        except mysql.connector.PoolError as err:
            # logger.exception("Pool agotada D=", err.msg, err.errno)
            raise DbError("Pool de conexiones agotada.", err)
        else:
            return conn
