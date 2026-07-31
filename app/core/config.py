from functools import lru_cache
from urllib.parse import quote_plus


from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict
)





class Settings(
    BaseSettings
):

    """
    Application configuration.

    Values are loaded from
    environment variables.
    """



    #
    # Application
    #

    APP_NAME: str = (

        "AI DevOps Risk Platform"

    )


    APP_VERSION: str = (

        "1.0.0"

    )


    ENVIRONMENT: str = (

        "development"

    )





    #
    # Database
    #

    DATABASE_HOST: str = (

        "localhost"

    )


    DATABASE_PORT: int = (

        5432

    )


    DATABASE_NAME: str = "risk_analyzer_db"


    DATABASE_USER: str = (

        "postgres"

    )


    DATABASE_PASSWORD: str = "postgres"

    DATABASE_SSL_MODE: str = "prefer"



    @property
    def DATABASE_URL(
        self
    ):


        return (

            f"postgresql://"
            f"{self.DATABASE_USER}:"
            f"{quote_plus(self.DATABASE_PASSWORD)}@"
            f"{self.DATABASE_HOST}:"
            f"{self.DATABASE_PORT}/"
            f"{self.DATABASE_NAME}"

        )





    #
    # Azure OpenAI
    #

    AZURE_OPENAI_API_KEY: str = ""


    AZURE_OPENAI_ENDPOINT: str = ""


    AZURE_OPENAI_API_VERSION: str = (

        "2024-02-15-preview"

    )


    AZURE_OPENAI_DEPLOYMENT_NAME: str = (

        "gpt-4"

    )





    #
    # Security
    #

    JWT_SECRET_KEY: str = ""


    JWT_ALGORITHM: str = (

        "HS256"

    )


    ACCESS_TOKEN_EXPIRE_MINUTES: int = (

        60

    )





    #
    # Webhook Security
    #

    GITHUB_WEBHOOK_SECRET: str = ""
    AZURE_DEVOPS_WEBHOOK_SECRET: str = ""
    AZURE_DEVOPS_PAT: str = ""
    AZURE_DEVOPS_ORGANIZATION: str = ""
    CORS_ORIGINS: str = ""





    #
    # Logging
    #

    LOG_LEVEL: str = (

        "INFO"

    )





    DEBUG: bool = False


    #
    # Configuration file
    #

    model_config = SettingsConfigDict(

        env_file=".env",

        env_file_encoding="utf-8",

        case_sensitive=True

    )







@lru_cache()
def get_settings():

    """
    Cached configuration instance.
    """

    return Settings()





settings = get_settings()
