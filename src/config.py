from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL:str
    SECRET_KEY:str
    JWT_ALGORITHM:str
    ACCESS_TOKEN_EXPIRE:int
    REFRESH_TOKEN_EXPIRE:int
    REDIS_HOST:str="localhost"
    REDIS_PORT:int
    GMAIL:str
    GMAIL_PASSWORD:str
    DOMAIN:str
    
    model_config=SettingsConfigDict(
        env_file=".env",
        extra="ignore"
        
    )

Config=Settings()