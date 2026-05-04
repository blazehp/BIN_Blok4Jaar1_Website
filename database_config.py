# Documentation to MYSQL Connector: https://dev.mysql.com/doc/connector-python/en/connector-python-connectargs.html
from mysql import connector
import os
from dotenv import load_dotenv

# Load environment variables into the server
# This is the .env when in development mode
load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_DATABASE = os.getenv("DB_DATABASE")
DB_POOL_NAME = os.getenv("DB_POOL_NAME")
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE"))


class DB:
    """Custom Database class that contains all configs and handles errors"""
    
    def __init__(self):
        self.mysql_connector = connector
        self.conn = None
    
    def connect(self):
        """Create or use an existing connection to the database"""
        if self.conn is not None and self.conn.is_connected():
            return self.conn
        else:
            conn = self.mysql_connector.connect(
                user=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST,
                port=DB_PORT,
                database=DB_DATABASE,
                pool_name=DB_POOL_NAME,
                pool_size=DB_POOL_SIZE
            )
            self.conn = conn
            return conn


# Use this variable in other files to use the (connected) database
# This variable can be imported like this: `from database_config import db`
db = DB().connect()
