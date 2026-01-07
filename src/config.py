from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL:str
    SECRET_KEY:str
    JWT_ALGORITHM:str
    ACCESS_TOKEN_EXPIRE:int
    REFRESH_TOKEN_EXPIRE:int
    model_config=SettingsConfigDict(
        env_file=".env",
        extra="ignore"
        
    )

Config=Settings()