from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    OLLAMA_HOST: str = Field(default="http://localhost:11434")
    OLLAMA_MODEL_PRIMARY: str = Field(default="llama3.1:8b-instruct-q4_K_M")
    OLLAMA_MODEL_FALLBACK: str = Field(default="phi3:3.8b-mini-instruct-q4_K_M")
    TEMPERATURE: float = Field(default=0.2)
    MAX_TOKENS: int = Field(default=2048)

    class Config:
        env_file = ".env"

settings = Settings()
