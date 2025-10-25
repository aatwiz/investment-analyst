"""
Memo generation database models for Feature 5.
"""
from datetime import datetime

from sqlalchemy import (
    JSON,
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

from backend.config.database import Base


class Memo(Base):
    """
    Generated investment memos and reports.
    """
    __tablename__ = "memos"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Memo identification
    title = Column(String(500), nullable=False)
    memo_type = Column(
        Enum(
            "investment_memo",
            "due_diligence_report",
            "market_analysis",
            "financial_analysis",
            "executive_summary",
            "custom",
            name="memo_type_enum"
        ),
        nullable=False
    )
    
    # Target information
    company_name = Column(String(255))
    deal_size = Column(String(100))
    
    # Content
    executive_summary = Column(Text)
    full_content = Column(Text)
    
    # Generation metadata
    template_used = Column(String(100))
    llm_model = Column(String(100))
    
    # Source references (JSON array of document IDs or sources)
    source_documents = Column(JSON)
    references = Column(JSON)
    
    # Quality metrics
    confidence_score = Column(Float)
    completeness_score = Column(Float)
    
    # Status
    status = Column(
        Enum("draft", "review", "final", "archived", name="memo_status_enum"),
        default="draft",
        nullable=False
    )
    
    # Metadata
    generated_by = Column(String(100))
    reviewed_by = Column(String(100))
    tags = Column(String(1000))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    finalized_at = Column(DateTime)
    
    # Relationships
    sections = relationship("MemoSection", back_populates="memo", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("idx_memo_title", "title"),
        Index("idx_memo_type", "memo_type"),
        Index("idx_memo_company", "company_name"),
        Index("idx_memo_status", "status"),
        Index("idx_memo_created", "created_at"),
    )
    
    def __repr__(self):
        return f"<Memo(id={self.id}, title='{self.title}', type='{self.memo_type}')>"


class MemoSection(Base):
    """
    Individual sections within a memo for structured content.
    """
    __tablename__ = "memo_sections"
    
    id = Column(Integer, primary_key=True, index=True)
    memo_id = Column(Integer, ForeignKey("memos.id", ondelete="CASCADE"), nullable=False)
    
    # Section details
    section_title = Column(String(255), nullable=False)
    section_order = Column(Integer, nullable=False)  # Order within memo
    
    # Content
    content = Column(Text, nullable=False)
    structured_data = Column(JSON)  # For tables, charts, etc.
    
    # Section type
    section_type = Column(String(50))  # e.g., "introduction", "analysis", "conclusion"
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    memo = relationship("Memo", back_populates="sections")
    
    __table_args__ = (
        Index("idx_section_memo", "memo_id", "section_order"),
    )
    
    def __repr__(self):
        return f"<MemoSection(id={self.id}, memo_id={self.memo_id}, title='{self.section_title}')>"


from sqlalchemy import Float  # Add missing import
