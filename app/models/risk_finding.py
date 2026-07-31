from sqlalchemy import (
    Column,
    Integer,
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





class RiskFinding(Base):

    """
    Stores individual security findings.
    """



    __tablename__ = "risk_findings"



    id = Column(

        Integer,

        primary_key=True,

        index=True

    )



    commit_id = Column(

        String(200),

        nullable=False,

        index=True

    )


    file_path = Column(

        String(500)

    )


    rule_name = Column(

        String(200)

    )



    category = Column(

        String(100)

    )



    title = Column(

        String(500)

    )



    description = Column(

        Text

    )



    severity = Column(

        String(50)

    )



    risk_score = Column(

        Integer

    )


    status = Column(

        String(50),

        default="OPEN"

    )


    created_at = Column(

        DateTime,

        server_default=func.now()

    )