from fastapi import (
    Request
)


from fastapi.responses import (
    JSONResponse
)


from sqlalchemy.exc import (
    SQLAlchemyError
)


from starlette.status import (
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_503_SERVICE_UNAVAILABLE
)


from app.core.logging import (
    get_logger
)





logger = get_logger(
    __name__
)





async def global_exception_handler(
    request: Request,
    exc: Exception
):

    """
    Handle unexpected application errors.
    """



    logger.exception(

        f"Unhandled exception "
        f"for {request.url.path}: {exc}"

    )



    return JSONResponse(

        status_code=

            HTTP_500_INTERNAL_SERVER_ERROR,


        content={


            "error":

                "Internal server error",


            "message":

                "Unexpected error occurred",


            "path":

                request.url.path

        }

    )





async def database_exception_handler(
    request: Request,
    exc: SQLAlchemyError
):

    """
    Handle database failures.
    """



    logger.exception(

        f"Database error: {exc}"

    )



    return JSONResponse(

        status_code=

            HTTP_503_SERVICE_UNAVAILABLE,


        content={


            "error":

                "Database unavailable",


            "message":

                "Unable to process request"

        }

    )





def register_exception_handlers(
    app
):

    """
    Register global handlers
    with FastAPI application.
    """



    app.add_exception_handler(

        Exception,

        global_exception_handler

    )



    app.add_exception_handler(

        SQLAlchemyError,

        database_exception_handler

    )