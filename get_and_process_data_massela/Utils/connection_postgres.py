from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class ConnectionPostgres:
    def __init__(self):
        self.database_uri = None
        self.engine = None
        self.session = None

    @classmethod
    def connect(cls, connection):
        connection_database = cls()
        connection_database.database_uri = connection
        connection_database.engine = create_engine(
            connection_database.database_uri, echo=False, pool_recycle=1800
        )
        Session = sessionmaker(bind=connection_database.engine)
        connection_database.session = Session()

        return connection_database
