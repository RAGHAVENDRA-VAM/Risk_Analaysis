from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)


from sqlalchemy.orm import Session


from app.core.database import (
    get_db
)


from app.services.auth_service import (
    AuthService
)


from app.core.security import (
    decode_access_token
)


from app.repositories.user_repository import (
    UserRepository
)


from app.core.security import (
    hash_password
)





router = APIRouter(

    prefix="/auth",

    tags=["Authentication"]

)





def get_auth_service(
    db: Session = Depends(get_db)
):


    return AuthService(

        db

    )





@router.post("/login")
async def login(
    request: dict,
    service: AuthService =
        Depends(get_auth_service)
):

    """
    Authenticate platform user.

    Request:

    {
        username,
        password
    }

    """



    username = request.get(

        "username"

    )


    password = request.get(

        "password"

    )



    if not username or not password:


        raise HTTPException(

            status_code=400,

            detail="Username and password required"

        )



    return service.login(

        username,

        password

    )





@router.post("/service-token")
async def generate_service_token(
    request: dict,
    service: AuthService =
        Depends(get_auth_service)
):

    """
    Generate token for CI/CD tools.

    Example:

    GitHub Actions
    Jenkins
    Azure DevOps

    """



    service_name = request.get(

        "service_name"

    )



    if not service_name:


        raise HTTPException(

            status_code=400,

            detail="service_name required"

        )



    return service.generate_pipeline_token(

        service_name

    )





@router.post("/register")
async def register_user(
    request: dict,
    db: Session = Depends(get_db)
):

    """
    Create new platform user.
    """



    repository = UserRepository(

        db

    )



    existing_user = (

        repository.get_user_by_username(

            request.get(

                "username"

            )

        )

    )



    if existing_user:


        raise HTTPException(

            status_code=409,

            detail="Username already exists"

        )



    user_data = {


        "username":

            request.get(
                "username"
            ),


        "email":

            request.get(
                "email"
            ),


        "password_hash":

            hash_password(

                request.get(
                    "password"
                )

            ),


        "role":

            request.get(

                "role",

                "developer"

            )

    }



    user = repository.create_user(

        user_data

    )



    return {


        "message":

            "User created successfully",


        "username":

            user.username

    }





@router.get("/profile")
async def profile(
    token: str
):

    """
    Return authenticated user information.
    """



    payload = decode_access_token(

        token

    )



    if not payload:


        raise HTTPException(

            status_code=401,

            detail="Invalid token"

        )



    return {


        "username":

            payload.get(
                "sub"
            ),


        "role":

            payload.get(
                "role"
            )

    }





@router.get("/health")
async def auth_health():


    return {


        "service":

            "authentication-api",


        "status":

            "healthy"

    }