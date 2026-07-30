from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    BigInteger
)


from sqlalchemy.sql import (
    func
)


from app.core.database import (
    Base
)





class Recommendation(Base):

    """
    Stores remediation recommendations.
    """



    __tablename__ = "recommendations"



    id = Column(

        Integer,

        primary_key=True,

        index=True

    )



    finding_id = Column(

        BigInteger,

        nullable=False,

        index=True

    )



    commit_id = Column(

        String(200),

        index=True

    )



    title = Column(

        String(500)

    )



    description = Column(

        Text

    )



    remediation_steps = Column(

        Text

    )



    priority = Column(

        String(50)

    )



    status = Column(

        String(50),

        default="OPEN"

    )



    created_at = Column(

        DateTime,

        server_default=func.now()

    )



    updated_at = Column(

        DateTime,

        onupdate=func.now()

    )