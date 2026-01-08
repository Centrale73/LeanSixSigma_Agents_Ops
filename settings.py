import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Centralized configuration for the symbiotic system.
    """
    AGNO_API_KEY: str = os.getenv("AGNO_API_KEY", "")
    PERPLEXITY_API_KEY: str = os.getenv("PERPLEXITY_API_KEY", "")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+psycopg://user:pass@localhost:5432/lss_agents")
    
    # Cognitive Core Settings
    MODEL_NAME: str = "llama-3.1-sonar-large-128k-online"
    PERPLEXITY_BASE_URL: str = "https://api.perplexity.ai"

    class Config:
        env_file = ".env"

settings = Settings()