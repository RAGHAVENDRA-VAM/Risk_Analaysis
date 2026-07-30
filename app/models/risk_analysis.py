from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    DateTime
)


from sqlalchemy.sql import (
    func
)


from app.core.database import (
    Base
)





class RiskAnalysis(Base):

    """
    Stores final risk assessment.
    """



    __tablename__ = "risk_analysis"



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



    repository_name = Column(

        String(200)

    )



    rule_score = Column(

        Integer

    )



    ai_score = Column(

        Integer

    )



    risk_score = Column(

        Integer

    )



    severity = Column(

        String(50)

    )



    decision = Column(

        String(50)

    )



    ai_summary = Column(

        Text

    )



    confidence = Column(

        Float

    )



    created_at = Column(

        DateTime,

        server_default=func.now()

    )