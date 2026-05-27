from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


# ----- DB 엔진, 세션 -----
DATABASE_URL = "sqlite:///community.db"

engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=True
)

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# ----- DB 모델 베이스 -----
class Base(DeclarativeBase):
    pass

def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        