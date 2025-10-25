"""
AI model configuration database model.
Similar to open-notebook's model management system.
"""
from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    Index,
    Integer,
    String,
    Text,
)

from backend.config.database import Base


class AIModel(Base):
    """
    AI model configurations for different providers and tasks.
    Inspired by open-notebook's model management.
    """
    __tablename__ = "ai_models"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Model identification
    name = Column(String(100), nullable=False, unique=True)
    display_name = Column(String(255), nullable=False)
    
    # Provider
    provider = Column(
        Enum(
            "openai",
            "anthropic",
            "google",
            "groq",
            "ollama",
            "azure",
            name="ai_provider_enum"
        ),
        nullable=False
    )
    
    # Model type
    model_type = Column(
        Enum(
            "language_model",  # For text generation (GPT-4, Claude, etc.)
            "embedding_model",  # For vector embeddings
            "image_model",  # For image processing
            "audio_model",  # For audio processing
            name="ai_model_type_enum"
        ),
        nullable=False
    )
    
    # Configuration
    api_endpoint = Column(String(500))
    model_version = Column(String(50))
    
    # Model parameters
    default_temperature = Column(Float, default=0.7)
    default_max_tokens = Column(Integer, default=3000)
    context_window = Column(Integer)  # Max context length
    
    # Capabilities
    supports_streaming = Column(Boolean, default=False)
    supports_function_calling = Column(Boolean, default=False)
    supports_vision = Column(Boolean, default=False)
    
    # Metadata
    description = Column(Text)
    capabilities = Column(JSON)  # List of specific capabilities
    limitations = Column(JSON)  # Known limitations
    
    # Usage tracking
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)  # Default for its type
    
    # Cost tracking
    input_cost_per_1k_tokens = Column(Float)
    output_cost_per_1k_tokens = Column(Float)
    
    # Performance metrics
    average_response_time = Column(Float)  # In seconds
    total_requests = Column(Integer, default=0)
    total_tokens_used = Column(Integer, default=0)
    total_cost_usd = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_used = Column(DateTime)
    
    __table_args__ = (
        Index("idx_model_name", "name"),
        Index("idx_model_provider", "provider"),
        Index("idx_model_type", "model_type"),
        Index("idx_model_active", "is_active"),
        Index("idx_model_default", "is_default", "model_type"),
    )
    
    def __repr__(self):
        return f"<AIModel(id={self.id}, name='{self.name}', provider='{self.provider}', type='{self.model_type}')>"
