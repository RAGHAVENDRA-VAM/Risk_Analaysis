from sqlalchemy import create_engine


from sqlalchemy.orm import (
    sessionmaker,
    declarative_base
)


from sqlalchemy.pool import (
    QueuePool
)


from app.core.config import (
    settings
)





#
# Database Engine
#

engine = create_engine(

    settings.DATABASE_URL,


    poolclass=QueuePool,


    pool_size=10,


    max_overflow=20,


    pool_pre_ping=True,


    echo=False,


    connect_args={
        "sslmode": "require"
    }

)





#
# Database Session Factory
#

SessionLocal = sessionmaker(

    autocommit=False,


    autoflush=False,


    bind=engine

)





#
# Base class for SQLAlchemy models
#

Base = declarative_base()





def get_db():

    """
    FastAPI database dependency.

    Creates database session
    for every request.
    """



    db = SessionLocal()


    try:


        yield db



    finally:


        db.close()