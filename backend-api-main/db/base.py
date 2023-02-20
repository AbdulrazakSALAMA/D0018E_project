import os
import sqlalchemy

import os

from google.cloud.sql.connector import Connector, IPTypes

import pymysql

import sqlalchemy


# ToDo: modify if required
USERNAME = os.getenv('DB_USERNAME', 'root')
PASSWORD = os.getenv('DB_PASSWORD', 'root')
HOST = os.getenv('DB_HOST', 'localhost')
DB_NAME = os.getenv('DB_NAME', 'bookstore')

POOL_SIZE = os.getenv('DB_POOLSIZE', 4)

CONNECTION_STRING = f"mysql+mysqldb://{USERNAME}:{PASSWORD}@{HOST}"


def connect_with_connector(db_name: str = None) -> sqlalchemy.engine.base.Engine:
    
    instance_connection_name = "bookstore:europe-north:bookstore-stg"
    db_user = USERNAME  # e.g. 'my-db-user'
    db_pass = PASSWORD  # e.g. 'my-db-password'

    ip_type = IPTypes.PUBLIC

    connector = Connector(ip_type)

    def getconn() -> pymysql.connections.Connection:
        conn: pymysql.connections.Connection = connector.connect(
            instance_connection_name,
            "pymysql",
            user=db_user,
            password=db_pass,
            db=db_name,
        )
        return conn

    pool = sqlalchemy.create_engine(
        "mysql+pymysql://",
        creator=getconn,
        # ...
    )
    return pool


# ToDo: research useful options
if os.getenv("ENV", "dev") == "dev":
    engine = sqlalchemy.create_engine(f"{CONNECTION_STRING}/{DB_NAME}", pool_size=POOL_SIZE)
    general_engine = sqlalchemy.create_engine(CONNECTION_STRING, pool_size=POOL_SIZE)
else:
    engine = connect_with_connector(DB_NAME)
    general_engine = connect_with_connector()


