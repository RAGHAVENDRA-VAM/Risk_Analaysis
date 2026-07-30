from datetime import (
    datetime,
    timedelta,
    timezone
)


from typing import (
    Optional
)


from jose import (
    jwt,
    JWTError
)


from passlib.context import (
    CryptContext
)


from app.core.config import (
    settings
)





#
# Password hashing configuration
#

pwd_context = CryptContext(

    schemes=[

        "bcrypt"

    ],

    deprecated="auto"

)





def hash_password(
    password: str
):

    """
    Convert plain password
    into secure hash.
    """



    return pwd_context.hash(

        password

    )





def verify_password(
    plain_password: str,
    hashed_password: str
):

    """
    Verify user password.
    """



    return pwd_context.verify(

        plain_password,

        hashed_password

    )





def create_access_token(
    data: dict,
    expires_minutes: Optional[int] = None
):

    """
    Generate JWT access token.
    """



    token_data = data.copy()



    if expires_minutes:


        expire = (

            datetime.now(

                timezone.utc

            )

            +

            timedelta(

                minutes=expires_minutes

            )

        )


    else:


        expire = (

            datetime.now(

                timezone.utc

            )

            +

            timedelta(

                minutes=

                settings.ACCESS_TOKEN_EXPIRE_MINUTES

            )

        )



    token_data.update(

        {

            "exp":

                expire

        }

    )



    encoded_token = jwt.encode(

        token_data,

        settings.JWT_SECRET_KEY,

        algorithm=

            settings.JWT_ALGORITHM

    )



    return encoded_token





def decode_access_token(
    token: str
):

    """
    Validate and decode JWT token.
    """



    try:


        payload = jwt.decode(

            token,

            settings.JWT_SECRET_KEY,

            algorithms=[

                settings.JWT_ALGORITHM

            ]

        )


        return payload



    except JWTError:


        return None





def create_service_token(
    service_name: str
):

    """
    Creates token for CI/CD systems.

    Example:

    GitHub Actions
    Jenkins
    Azure DevOps

    """



    return create_access_token(

        {

            "sub":

                service_name,


            "type":

                "service"

        }

    )