"""
Document-related database models.
Stores uploaded documents, their content, and vector embeddings for semantic search.
"""
import os
from datetime import datetime
from typing import Optional

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from config.database import Base

# Get embedding dimensions from environment
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIMENSIONS", "1536"))


class Document(Base):
    """
    Stores metadata and content for uploaded documents.
    Similar to open-notebook's Source model.
    """
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    
    # Metadata
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False)  # pdf, docx, xlsx, etc.
    file_size = Column(Integer)  # in bytes
    
    # Document classification
    document_type = Column(
        Enum(
            "financial_statement",
            "pitch_deck",
            "business_plan",
            "market_research",
            "due_diligence",
            "other",
            name="document_type_enum"
        ),
        default="other"
    )
    
    # Content
    title = Column(String(500))
    full_text = Column(Text)  # Extracted text content
    page_count = Column(Integer)
    
    # Processing status
    is_processed = Column(Boolean, default=False)
    is_vectorized = Column(Boolean, default=False)
    processing_error = Column(Text)
    
    # Metadata
    upload_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    processed_date = Column(DateTime)
    vectorized_date = Column(DateTime)
    
    # User/project association (optional)
    user_id = Column(String(100))
    project_id = Column(String(100))
    
    # Tags and topics (JSON-like storage)
    tags = Column(String(1000))  # Comma-separated tags
    topics = Column(String(1000))  # Comma-separated topics
    
    # Relationships
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    embeddings = relationship("DocumentEmbedding", back_populates="document", cascade="all, delete-orphan")
    analyses = relationship("Analysis", back_populates="document", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("idx_document_filename", "filename"),
        Index("idx_document_type", "document_type"),
        Index("idx_document_upload_date", "upload_date"),
        Index("idx_document_user", "user_id"),
    )
    
    def __repr__(self):
        return f"<Document(id={self.id}, filename='{self.filename}', type='{self.document_type}')>"


class DocumentChunk(Base):
    """
    Stores text chunks from documents for better embedding granularity.
    Similar to open-notebook's source_embedding model.
    """
    __tablename__ = "document_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    
    # Chunk information
    chunk_index = Column(Integer, nullable=False)  # Order of chunk in document
    content = Column(Text, nullable=False)
    page_number = Column(Integer)  # Original page in document
    
    # Metadata
    char_count = Column(Integer)
    word_count = Column(Integer)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    document = relationship("Document", back_populates="chunks")
    
    # Indexes
    __table_args__ = (
        Index("idx_chunk_document", "document_id", "chunk_index"),
    )
    
    def __repr__(self):
        return f"<DocumentChunk(id={self.id}, document_id={self.document_id}, chunk={self.chunk_index})>"


class DocumentEmbedding(Base):
    """
    Stores vector embeddings for documents and chunks.
    Uses pgvector for semantic search.
    """
    __tablename__ = "document_embeddings"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    chunk_id = Column(Integer, ForeignKey("document_chunks.id", ondelete="CASCADE"))
    
    # Vector embedding
    embedding = Column(Vector(EMBEDDING_DIM), nullable=False)
    
    # Content reference (for search results)
    content = Column(Text, nullable=False)  # Snippet of text that was embedded
    
    # Embedding metadata
    embedding_model = Column(String(100), default="text-embedding-3-small")
    embedding_dimensions = Column(Integer, default=EMBEDDING_DIM)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    document = relationship("Document", back_populates="embeddings")
    
    # Indexes for vector search
    __table_args__ = (
        Index("idx_embedding_document", "document_id"),
        # Note: Vector indexes will be created separately with specific operators
    )
    
    def __repr__(self):
        return f"<DocumentEmbedding(id={self.id}, document_id={self.document_id}, model='{self.embedding_model}')>"
