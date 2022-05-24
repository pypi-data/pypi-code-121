from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import sessionmaker


class PgClient:
    def __init__(self, uri):
        self.meta_data = MetaData()
        self.engine = create_engine(uri)
        self.conn = self.engine.connect()
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        print("👍 Connected to Postgres")
