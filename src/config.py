from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL:str
    SECRET_KEY:str
    JWT_ALGORITHM:str
    ACCESS_TOKEN_EXPIRE:int
    REFRESH_TOKEN_EXPIRE:int
    REDIS_HOST:str="localhost"
    REDIS_PORT:int
    GOOGLE_CLIENT_ID:str
    CLIENT_SECRET:str
    GOOGLE_REDIRECT_URI:str
    
    model_config=SettingsConfigDict(
        env_file=".env",
        extra="ignore"
        
    )

Config=Settings()