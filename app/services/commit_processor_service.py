from app.services.commit_context_builder import CommitContextBuilder
from app.repositories.commit_repository import CommitRepository
from app.core.logging import get_logger

logger = get_logger(__name__)


class CommitProcessorService:
    """
    Processes incoming SCM commits.
    """

    def __init__(self, db):
        self.commit_repository = CommitRepository(db)
        self.context_builder = CommitContextBuilder()

    def process_commit(self, commit_data: dict):
        """
        Main commit processing workflow.
        """

        logger.info(
            f"Processing commit {commit_data.get('commit_id')}"
        )

        # Step 1 - Build context
        context = self.context_builder.build_context(commit_data)

        commit = self.commit_repository.get_by_commit_id(
            context["commit_id"]
        )

        if commit:
            logger.info(
                f"Commit already exists: {commit.commit_id}. Updating status to PROCESSING."
            )
            self.commit_repository.update_status(
                commit.commit_id,
                "PROCESSING"
            )
        else:
            # Step 2 - Store commit
            commit = self.commit_repository.create({
                "commit_id": context["commit_id"],
                "author": context["author"],
                "commit_message": context["message"],
                "status": "PROCESSING"
            })

        # Step 3 - Prepare risk analysis input
        analysis_request = {
            "commit_id": commit.id,
            "context": context
        }

        logger.info("Commit processing completed")

        return analysis_request
