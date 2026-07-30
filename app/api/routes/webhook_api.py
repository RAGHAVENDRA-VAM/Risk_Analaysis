from fastapi import (
    APIRouter,
    Request,
    HTTPException,
    Depends
)


from app.services.commit_processor_service import (
    CommitProcessorService
)


from app.core.logging import (
    get_logger
)


from app.core.database import (
    get_db
)





logger = get_logger(
    __name__
)



router = APIRouter(
    prefix="/webhook",
    tags=["Webhook"]
)





@router.post(
    "/azure-devops"
)
async def azure_devops_webhook(
    request: Request,
    db=Depends(get_db)
):

    """
    Receive Azure DevOps push events.
    """



    try:


        payload = await request.json()



        logger.info(

            "Azure DevOps event received"

        )



        commit_data = (

            extract_commit_data(

                payload

            )

        )



        processor = (

            CommitProcessorService(

                db

            )

        )



        analysis_request = (

            processor.process_commit(

                commit_data

            )

        )



        return {


            "status":

                "analysis_started",


            "commit_id":

                analysis_request.get(

                    "commit_id"

                )

        }



    except Exception as error:


        logger.error(

            f"Webhook processing failed: {error}"

        )


        raise HTTPException(

            status_code=500,

            detail="Webhook processing failed"

        )





def extract_commit_data(
    payload: dict
):

    """
    Convert Azure DevOps payload
    into internal format.
    """



    resource = payload.get(

        "resource",

        {}

    )



    commits = resource.get(

        "commits",

        []

    )



    if not commits:

        raise ValueError(

            "No commit information found"

        )



    commit = commits[0]



    return {


        "commit_id":

            commit.get(

                "commitId"

            ),



        "message":

            commit.get(

                "comment"

            ),



        "author":

            commit.get(

                "author",

                {}

            ).get(

                "name"

            ),



        "files":

            []

    }