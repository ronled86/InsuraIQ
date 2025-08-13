from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # Authentication & JWT settings
    SUPABASE_URL: str = Field(default="", description="https://<project>.supabase.co")
    SUPABASE_JWKS_URL: str = Field(default="", description="Optional override")
    API_AUDIENCE: str = Field(default="", description="Optional audience to enforce")
    API_ISSUER: str = Field(default="", description="Expected issuer like https://<project>.supabase.co/auth/v1")
    
    # API configuration
    RATE_LIMIT_PER_MINUTE: int = Field(default=240, description="Global simple limit per IP")
    BASE_PATH: str = Field(default="/api", description="Mount path behind reverse proxy")
    
    # Database configuration
    SQLALCHEMY_DATABASE_URL: str = Field(default="postgresql+psycopg2://postgres:postgres@db:5432/insurance")
    
    # External integrations
    INSURER_API_BASE: str = Field(default="", description="Optional external insurer aggregator base URL")
    INSURER_API_KEY: str = Field(default="", description="Optional API key")
    OPENAI_API_KEY: str = Field(default="", description="OpenAI API key for AI analysis")
    
    # Development mode
    LOCAL_DEV: bool = Field(default=False, description="If true, relax auth and allow SQLite DB override")
    
    model_config = {"env_file": ".env"}

settings = Settings()