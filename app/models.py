from sqlalchemy import Column, Integer, String, Text, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector

from app.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    category = Column(String, nullable=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")


class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(1536))

    page_number = Column(Integer, nullable=True)
    section_title = Column(String, nullable=True)

    document = relationship("Document", back_populates="chunks")


class QueryLog(Base):
    __tablename__ = "query_logs"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    embedding = Column(Vector(1536), nullable=True)
    category = Column(String, nullable=True)
    top_score = Column(Float, nullable=True)
    answered = Column(Boolean, nullable=False)

    session_id = Column(String, nullable=True)
    feedback = Column(String, nullable=True)
    flagged = Column(Boolean, nullable=False, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class GapRecommendation(Base):
    __tablename__ = "gap_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(Text, nullable=False)
    example_questions = Column(Text, nullable=False)
    times_asked = Column(Integer, nullable=False)

    suggested_question = Column(Text, nullable=False)
    suggested_answer = Column(Text, nullable=False)

    status = Column(String, nullable=False, default="pending")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
