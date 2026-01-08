import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Centralized configuration for the symbiotic system.
    """
    # API Keys
    AGNO_API_KEY: str = os.getenv("AGNO_API_KEY", "")
    PERPLEXITY_API_KEY: str = os.getenv("PERPLEXITY_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "") # Required for Embeddings in Knowledge
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+psycopg://ai:ai@localhost:5532/ai")
    
    # Model Configurations
    PERPLEXITY_MODEL: str = "sonar-pro"
    
    class Config:
        env_file = ".env"

settings = Settings()