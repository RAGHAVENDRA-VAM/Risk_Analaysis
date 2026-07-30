from typing import (
    Optional,
    List
)


from sqlalchemy.orm import (
    Session
)


from app.models.commit import (
    Commit
)


from app.core.logging import (
    get_logger
)





logger = get_logger(
    __name__
)





class CommitRepository:
    """
    Database operations for commits.
    """



    def __init__(
        self,
        db: Session
    ):

        self.db = db





    def create(
        self,
        commit_data: dict
    ) -> Commit:

        """
        Create new commit record.
        """



        commit = Commit(

            **commit_data

        )



        self.db.add(

            commit

        )


        self.db.commit()



        self.db.refresh(

            commit

        )



        logger.info(

            f"Commit stored: {commit.commit_id}"

        )



        return commit





    def get_by_commit_id(
        self,
        commit_id: str
    ) -> Optional[Commit]:

        """
        Find commit using SHA.
        """



        return (

            self.db.query(

                Commit

            )

            .filter(

                Commit.commit_id == commit_id

            )

            .first()

        )





    def exists(
        self,
        commit_id: str
    ) -> bool:

        """
        Check duplicate commit.
        """



        commit = self.get_by_commit_id(

            commit_id

        )


        return commit is not None





    def update_status(
        self,
        commit_id: str,
        status: str
    ):

        """
        Update commit processing state.
        """



        commit = self.get_by_commit_id(

            commit_id

        )



        if not commit:

            return None



        commit.status = status



        self.db.commit()



        self.db.refresh(

            commit

        )



        logger.info(

            f"Commit {commit_id} status updated to {status}"

        )



        return commit





    def get_by_repository(
        self,
        repository_name: str
    ) -> List[Commit]:

        """
        Get commits for repository.
        """



        return (

            self.db.query(

                Commit

            )

            .filter(

                Commit.repository_name == repository_name

            )

            .order_by(

                Commit.created_at.desc()

            )

            .all()

        )





    def get_latest_commits(
        self,
        limit: int = 10
    ) -> List[Commit]:

        """
        Get latest analyzed commits.
        """



        return (

            self.db.query(

                Commit

            )

            .order_by(

                Commit.created_at.desc()

            )

            .limit(

                limit

            )

            .all()

        )