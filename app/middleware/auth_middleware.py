from fastapi import (
    Request,
    HTTPException
)


from starlette.middleware.base import (
    BaseHTTPMiddleware
)


from app.core.security import (
    decode_access_token
)


from app.core.logging import (
    get_logger
)





logger = get_logger(
    __name__
)





class AuthMiddleware(
    BaseHTTPMiddleware
):

    """
    JWT authentication middleware.
    """



    #
    # Public endpoints
    #

    PUBLIC_PATHS = [

        "/",

        "/health",

        "/auth/login",

        "/auth/register",

        "/auth/health"

    ]





    async def dispatch(
        self,
        request: Request,
        call_next
    ):

        path = request.url.path



        #
        # Allow public APIs
        #

        if path in self.PUBLIC_PATHS:


            return await call_next(

                request

            )





        #
        # Read Authorization Header
        #

        auth_header = request.headers.get(

            "Authorization"

        )



        if not auth_header:


            logger.warning(

                f"Missing token for {path}"

            )


            raise HTTPException(

                status_code=401,

                detail="Authorization token required"

            )





        try:


            scheme, token = (

                auth_header.split()

            )


            if scheme.lower() != "bearer":


                raise Exception()




        except Exception:


            raise HTTPException(

                status_code=401,

                detail="Invalid authorization format"

            )





        #
        # Validate JWT
        #

        payload = decode_access_token(

            token

        )



        if not payload:


            logger.warning(

                "Invalid JWT token"

            )


            raise HTTPException(

                status_code=401,

                detail="Invalid token"

            )





        #
        # Attach user information
        #

        request.state.user = {


            "username":

                payload.get(
                    "sub"
                ),


            "role":

                payload.get(
                    "role"
                ),


            "type":

                payload.get(
                    "type"
                )

        }





        logger.info(

            f"Authenticated user: "
            f"{request.state.user['username']}"

        )



        return await call_next(

            request

        )