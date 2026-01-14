from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:qwerty123@localhost:5432/image_processing_db"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024
    
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    CACHE_TTL_PLANS: int = 600
    CACHE_TTL_USER: int = 300
    CACHE_TTL_SUBSCRIPTION: int = 300
    
    class Config:
        env_file = ".env"


settings = Settings()
