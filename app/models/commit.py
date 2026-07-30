from uuid import uuid4

from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime
)


from sqlalchemy.sql import (
    func
)


from app.core.database import (
    Base
)





class Commit(Base):

    """
    Stores source control commit details.
    """



    __tablename__ = "commits"



    id = Column(

        String(36),

        primary_key=True,

        default=lambda: str(uuid4()),

        index=True

    )



    commit_id = Column(

        String(200),

        unique=True,

        nullable=False,

        index=True

    )



    repository_name = Column(

        String(200)

    )



    branch_name = Column(

        String(100)

    )



    author = Column(

        String(200)

    )



    commit_message = Column(

        Text

    )



    provider = Column(

        String(50)

    )



    status = Column(

        String(50),

        default="NEW"

    )



    created_at = Column(

        DateTime,

        server_default=func.now()

    )



    updated_at = Column(

        DateTime,

        onupdate=func.now()

    )