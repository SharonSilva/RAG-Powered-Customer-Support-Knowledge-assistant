from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship 
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector

from app.database import Base

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")
    
class Chunk(Base):
    __tablename__ = "chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(1536))        # matches OpenAI text-embedding-3-small dimension
    page_number = Column(Integer, nullable=True) # which page this chunk came from
    section_title = Column(String, nullable=True) #nearest heading, if detected
    document = relationship("Document", back_populates="chunks")