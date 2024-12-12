from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DB_URL = "postgresql://postgres:root@blog-postgres:5432/postgres?sslmode=disable"
engine = create_engine(SQLALCHEMY_DB_URL)#движок для подключения к бд
#создается сессию бд
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()#Создаёт базовый класс, который используется для определения ORM-моделей.


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        