from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    REPLICATE_API_TOKEN: str
    DUMMY_IMAGE_URL: str
    DATABASE_USERNAME: str
    DATABASE_PASSWORD: str
    DATABASE_HOST: str
    DATABASE_NAME: str
    class Config:
        env_file = ".env"


settings = Settings()