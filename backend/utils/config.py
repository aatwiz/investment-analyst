"""
Configuration settings for the application
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from typing import List


class Settings(BaseSettings):
    """Application settings"""
    
    # Pydantic v2 configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )
    
    # Application
    APP_NAME: str = "Investment Analyst AI Agent"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    
    # Backend
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    API_PREFIX: str = "/api/v1"
    
    # File Upload
    MAX_UPLOAD_SIZE_MB: int = 100
    UPLOAD_DIR: str = "./data/uploads"
    PROCESSED_DIR: str = "./data/processed"
    OUTPUT_DIR: str = "./data/outputs"
    ALLOWED_EXTENSIONS: str = "pdf,docx,doc,xlsx,xls,csv,txt,pptx,ppt,jpg,jpeg,png"
    
    # API Keys
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    
    # Database
    DATABASE_URL: str = ""
    MONGODB_URL: str = ""
    
    # Vector Database
    VECTOR_DB_TYPE: str = "faiss"
    VECTOR_DB_PATH: str = "./data/vector_db"
    
    # LLM Settings
    LLM_PROVIDER: str = "openai"
    LLM_MODEL: str = "gpt-4-turbo-preview"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 4000
    
    # Ollama Settings
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "mistral"
    
    # OCR
    OCR_ENABLED: bool = True
    OCR_LANGUAGE: str = "eng"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"
    
    def get_allowed_extensions_list(self) -> List[str]:
        """Get allowed extensions as a list"""
        return [ext.strip() for ext in self.ALLOWED_EXTENSIONS.split(",")]
    
    def get_max_upload_size_bytes(self) -> int:
        """Get max upload size in bytes"""
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024


settings = Settings()
