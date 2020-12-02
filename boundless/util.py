import sqlalchemy


def load_db_session(conn_string):
    engine = sqlalchemy.create_engine(conn_string)
    db_objs.Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()
